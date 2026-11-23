"""The league's match store: one place for every machine's results, so that a match is played once.

``LEAGUE_STORE`` names it. Unset (or empty), there is no store, and a
tournament plays and caches on this machine alone, as it always did: the pull
request checks and offline work rely on that. A directory (``/some/dir`` or
``file:///some/dir``) is a store on a filesystem, for machines that share one
and for the tests. ``s3://bucket/prefix`` is the league's bucket, through
boto3, which is imported only then.

Under its root the store keeps one namespace per runner build (the first 16
characters of the build's hash, the build that every key covers):

    <build>/results/<key>.json      a match's result: it counts once this is there
    <build>/results/<key>.json.gz   its demo, written before the result
    <build>/leases/<key>            who plays the match now, and until when
    <build>/failed/<key>-<n>.json   the n-th attempt that failed a turn
    <build>/queue/<key>.json        a match that someone asked the players for
    <build>/code/<fingerprint>.tar.gz   a bot's Go files, named by ``gobots.fingerprint``
    <build>/maps/<sha256>.json      a map file, named by its hash

A lease is made only if none is there (S3's ``If-None-Match: *``), and an
expired one is taken over only if it is unchanged (``If-Match`` on its ETag),
so of two machines that want a match, one plays it. A result with a failed
turn is played again, as a turn can time out on a busy machine, but only
``MAX_FAILED_ATTEMPTS`` times: the last attempt is then the result, and
``--strict`` fails on it.

Every result says who played it (``played_by``: the machine, from
``LEAGUE_PLAYER_ID`` or the host's name, and the run, from ``LEAGUE_RUN_ID``
or ``GITHUB_RUN_ID``), so a machine's results can be dropped if they are ever
in doubt.
"""

from __future__ import annotations

import contextlib
import fcntl
import gzip
import hashlib
import io
import json
import math
import os
import socket
import tarfile
import threading
import time
import uuid
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from types import TracebackType
from typing import Any, Protocol, Self

from .roster import sources

STORE_VARIABLE = "LEAGUE_STORE"
# play (the default): lease, play and write results. request: ask the players
# for matches and wait for them, never writing a result: for a step that read
# real games, whose text may try to talk the model into planting one.
MODE_VARIABLE = "LEAGUE_STORE_MODE"
MODES = ("play", "request")
PLAYER_VARIABLE = "LEAGUE_PLAYER_ID"
RUN_VARIABLE = "LEAGUE_RUN_ID"
# How long a tournament waits for matches that other players hold, at most.
WAIT_VARIABLE = "LEAGUE_STORE_WAIT_SECONDS"
WAIT_SECONDS = 3600.0
# A Lambda player to wake when matches are requested (hosting/players/), if any.
FUNCTION_VARIABLE = "LEAGUE_PLAYER_FUNCTION"

# A match that failed a turn this many times is a real failure of a bot: its last attempt is the result.
MAX_FAILED_ATTEMPTS = 3
# A lease lasts the batch's expected time and this much more, and is renewed while its match is played.
LEASE_MARGIN_SECONDS = 120.0
# A generous guess of a match's time, for a lease's expiry: a Go bot's match takes about a third of a second.
MATCH_SECONDS = 2.0
# How often a waiting tournament looks for results at first, and at most (it backs off in between).
POLL_SECONDS = 1.0
MAX_POLL_SECONDS = 15.0
# How many matches a woken Lambda player takes, and how many players one request wakes at most.
PLAYER_BATCH = 25
MAX_WOKEN = 40


class Backend(Protocol):
    """Where a store's objects are: a directory or an S3 bucket.

    Paths are relative and use ``/``. A tag names one version of an object
    (an S3 ETag, or a hash of a file's contents): ``replace`` and ``delete``
    with a tag change the object only if it is still that version.
    """

    def read(self, path: str) -> tuple[bytes, str] | None:
        """An object's contents and tag, or None when there is none."""
        ...

    def write(self, path: str, data: bytes) -> str:
        """Write an object whatever is there, and return its tag."""
        ...

    def create(self, path: str, data: bytes) -> str | None:
        """Write an object only if there is none, and return its tag; None when there was one."""
        ...

    def replace(self, path: str, data: bytes, tag: str) -> str | None:
        """Write an object only if it is still the version ``tag``, and return its new tag; None otherwise."""
        ...

    def delete(self, path: str, tag: str | None = None) -> bool:
        """Delete an object (only if it is still the version ``tag``, with a tag); whether it was deleted."""
        ...

    def exists(self, path: str) -> bool:
        """Whether there is an object."""
        ...

    def names(self, prefix: str) -> list[str]:
        """The names of the objects directly under a directory-like prefix, sorted."""
        ...


def _tag(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DirectoryBackend:
    """A store in a directory, for machines that share a filesystem, and for the tests.

    A write goes to a file of its own and is renamed into place, so a reader
    sees an object whole or not at all. ``create`` links that file to the
    object's name, which fails if the name is taken: the same create-if-absent
    as ``open(O_CREAT | O_EXCL)``, with the contents already in it. ``create``,
    ``replace`` and a ``delete`` with a tag hold a lock on the object's name
    (``flock`` on a file of ``.locks/``), so a compare and its swap are one
    step, and the lock goes when its process does.
    """

    def __init__(self, root: Path) -> None:
        """A store in this directory, made on the first write."""
        self.root = root

    def _file(self, path: str) -> Path:
        parts = PurePosixPath(path).parts
        if not parts or any(part in ("", ".", "..") or part.startswith(".") for part in parts):
            raise ValueError(f"not a store path: {path!r}")
        return self.root.joinpath(*parts)

    @contextlib.contextmanager
    def _locked(self, path: str) -> Generator[None]:
        lock = self.root / ".locks" / _tag(path.encode())[:32]
        lock.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def _partial(self, file: Path, data: bytes) -> Path:
        file.parent.mkdir(parents=True, exist_ok=True)
        partial = file.with_name(f".{file.name}.{uuid.uuid4().hex}")
        partial.write_bytes(data)
        return partial

    def read(self, path: str) -> tuple[bytes, str] | None:
        """An object's contents and tag, or None when there is none."""
        try:
            data = self._file(path).read_bytes()
        except FileNotFoundError:
            return None
        return data, _tag(data)

    def write(self, path: str, data: bytes) -> str:
        """Write an object whatever is there, and return its tag."""
        file = self._file(path)
        os.replace(self._partial(file, data), file)
        return _tag(data)

    def create(self, path: str, data: bytes) -> str | None:
        """Write an object only if there is none, and return its tag; None when there was one."""
        file = self._file(path)
        partial = self._partial(file, data)
        try:
            with self._locked(path):
                os.link(partial, file)
        except FileExistsError:
            return None
        finally:
            partial.unlink(missing_ok=True)
        return _tag(data)

    def replace(self, path: str, data: bytes, tag: str) -> str | None:
        """Write an object only if it is still the version ``tag``, and return its new tag; None otherwise."""
        file = self._file(path)
        partial = self._partial(file, data)
        try:
            with self._locked(path):
                current = self.read(path)
                if current is None or current[1] != tag:
                    return None
                os.replace(partial, file)
        finally:
            partial.unlink(missing_ok=True)
        return _tag(data)

    def delete(self, path: str, tag: str | None = None) -> bool:
        """Delete an object (only if it is still the version ``tag``, with a tag); whether it was deleted."""
        file = self._file(path)
        if tag is None:
            try:
                file.unlink()
            except FileNotFoundError:
                return False
            return True
        with self._locked(path):
            current = self.read(path)
            if current is None or current[1] != tag:
                return False
            file.unlink()
        return True

    def exists(self, path: str) -> bool:
        """Whether there is an object."""
        return self._file(path).is_file()

    def names(self, prefix: str) -> list[str]:
        """The names of the objects directly under a directory-like prefix, sorted."""
        directory = self._file(prefix.rstrip("/"))
        try:
            return sorted(entry.name for entry in directory.iterdir() if entry.is_file() and entry.name[0] != ".")
        except FileNotFoundError:
            return []


# What S3 answers when a conditional write or delete finds another version, or none.
_CONFLICTS = {"PreconditionFailed", "ConditionalRequestConflict", "NoSuchKey", "NotFound", "404", "409", "412"}


class S3Client(Protocol):
    """What the store calls of boto3's S3 client."""

    def get_object(self, **arguments: object) -> dict[str, Any]:
        """Read an object."""
        ...

    def put_object(self, **arguments: object) -> dict[str, Any]:
        """Write an object."""
        ...

    def delete_object(self, **arguments: object) -> dict[str, Any]:
        """Delete an object."""
        ...

    def head_object(self, **arguments: object) -> dict[str, Any]:
        """Look at an object."""
        ...

    def get_paginator(self, operation: str) -> Any:  # noqa: ANN401  # boto3's paginators have no types here.
        """A paginator of a listing."""
        ...


class S3Backend:
    """A store in an S3 bucket, under a prefix: the league's, for every machine.

    boto3 is imported on the first request, so the league's tools need it only
    when such a store is set.
    """

    def __init__(self, bucket: str, prefix: str = "", client: S3Client | None = None) -> None:
        """A store in this bucket, under this prefix (a client may be given, as the tests do)."""
        self.bucket = bucket
        self.prefix = prefix.strip("/") + "/" if prefix.strip("/") else ""
        self._client = client

    @property
    def client(self) -> S3Client:
        """The S3 client, made on first use."""
        if self._client is None:
            import boto3  # Only a store in S3 needs it.

            self._client = boto3.client("s3")
        return self._client

    def _key(self, path: str) -> str:
        return self.prefix + path

    @staticmethod
    def _code(error: Exception) -> str:
        response = getattr(error, "response", None) or {}
        return str(response.get("Error", {}).get("Code", ""))

    def _conflict(self, error: Exception) -> bool:
        return self._code(error) in _CONFLICTS

    def read(self, path: str) -> tuple[bytes, str] | None:
        """An object's contents and tag, or None when there is none."""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self._key(path))
        except Exception as error:
            if self._code(error) in ("NoSuchKey", "NotFound", "404"):
                return None
            raise
        return response["Body"].read(), response["ETag"]

    def write(self, path: str, data: bytes) -> str:
        """Write an object whatever is there, and return its tag."""
        return self.client.put_object(Bucket=self.bucket, Key=self._key(path), Body=data)["ETag"]

    def create(self, path: str, data: bytes) -> str | None:
        """Write an object only if there is none (``If-None-Match: *``), and return its tag; None when there was one."""
        try:
            response = self.client.put_object(Bucket=self.bucket, Key=self._key(path), Body=data, IfNoneMatch="*")
        except Exception as error:
            if self._conflict(error):
                return None
            raise
        return response["ETag"]

    def replace(self, path: str, data: bytes, tag: str) -> str | None:
        """Write an object only if it is still the version ``tag`` (``If-Match``); None otherwise."""
        try:
            response = self.client.put_object(Bucket=self.bucket, Key=self._key(path), Body=data, IfMatch=tag)
        except Exception as error:
            if self._conflict(error):
                return None
            raise
        return response["ETag"]

    def delete(self, path: str, tag: str | None = None) -> bool:
        """Delete an object (only if it is still the version ``tag``, with ``If-Match``); whether it was deleted."""
        arguments: dict[str, Any] = {"Bucket": self.bucket, "Key": self._key(path)}
        if tag is not None:
            arguments["IfMatch"] = tag
        try:
            self.client.delete_object(**arguments)
        except Exception as error:
            if self._conflict(error):
                return False
            raise
        return True

    def exists(self, path: str) -> bool:
        """Whether there is an object."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._key(path))
        except Exception as error:
            if self._code(error) in ("NoSuchKey", "NotFound", "404"):
                return False
            raise
        return True

    def names(self, prefix: str) -> list[str]:
        """The names of the objects directly under a directory-like prefix, sorted."""
        start = self._key(prefix.rstrip("/") + "/")
        names = []
        for page in self.client.get_paginator("list_objects_v2").paginate(
            Bucket=self.bucket, Prefix=start, Delimiter="/"
        ):
            names += [item["Key"][len(start) :] for item in page.get("Contents", [])]
        return sorted(names)


def backend_at(location: str) -> Backend:
    """The backend that a ``LEAGUE_STORE`` value names: ``s3://bucket/prefix``, ``file:///dir`` or a directory.

    Raises:
        ValueError: An ``s3://`` location names no bucket.
    """
    if location.startswith("s3://"):
        bucket, _, prefix = location.removeprefix("s3://").partition("/")
        if not bucket:
            raise ValueError(f"{STORE_VARIABLE}={location!r} names no bucket: write s3://bucket/prefix")
        return S3Backend(bucket, prefix)
    return DirectoryBackend(Path(location.removeprefix("file://")).expanduser())


def played_by() -> dict[str, str]:
    """Who plays here: the machine (``LEAGUE_PLAYER_ID``, or the host's name) and the run."""
    return {
        "machine": os.environ.get(PLAYER_VARIABLE) or socket.gethostname(),
        "run": os.environ.get(RUN_VARIABLE) or os.environ.get("GITHUB_RUN_ID") or f"pid-{os.getpid()}",
    }


def wait_seconds() -> float:
    """How long a tournament waits for matches that other players hold (``LEAGUE_STORE_WAIT_SECONDS``)."""
    return float(os.environ.get(WAIT_VARIABLE) or WAIT_SECONDS)


def each[Item, Answer](function: Callable[[Item], Answer], items: Iterable[Item], threads: int = 16) -> list[Answer]:
    """``function`` of every item, in order, several at once: a store in S3 answers each request in a few ms."""
    items = list(items)
    if len(items) <= 1:
        return [function(item) for item in items]
    with ThreadPoolExecutor(min(threads, len(items))) as pool:
        return list(pool.map(function, items))


def lease_seconds(matches: int, parallel: int) -> float:
    """How long to lease a batch of matches for: its expected time, and a margin."""
    return MATCH_SECONDS * math.ceil(matches / max(parallel, 1)) + LEASE_MARGIN_SECONDS


@dataclass(frozen=True)
class Lease:
    """A lease this machine holds on a match: the version it wrote, and when it ends."""

    key: str
    tag: str
    expires: float


def pack_bot(directory: Path) -> bytes:
    """A bot's Go files (``roster.sources``: what its fingerprint covers) as a gzipped tarball.

    The same code gives the same bytes: no times, owners or modes of the files.
    """
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sources(directory):
            data = path.read_bytes()
            info = tarfile.TarInfo(path.relative_to(directory).as_posix())
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            archive.addfile(info, io.BytesIO(data))
    return gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0)


def unpack_bot(data: bytes, target: Path) -> None:
    """Unpack ``pack_bot``'s tarball into a directory: Go files only, each inside it.

    Raises:
        ValueError: The tarball holds anything else: a link, a directory entry
            outside it, a file that isn't Go code.
    """
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if (
                not member.isfile()
                or path.is_absolute()
                or any(part in ("", ".", "..") for part in path.parts)
                or path.suffix != ".go"
                or path.name.endswith("_test.go")
            ):
                raise ValueError(f"a bot's code holds {member.name!r}, which is not one of its Go files")
            source = archive.extractfile(member)
            assert source is not None
            file = target.joinpath(*path.parts)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(source.read())


class Store:
    """The match store of one runner build: results, leases, failed attempts, the queue, code and maps."""

    def __init__(self, backend: Backend, build_hash: str, mode: str = "play", location: str = "") -> None:
        """The store of the runner build ``build_hash`` in ``backend``.

        Raises:
            ValueError: The mode is neither play nor request.
        """
        if mode not in MODES:
            raise ValueError(f"{MODE_VARIABLE}={mode!r}: write play or request")
        self.backend = backend
        self.namespace = build_hash[:16]
        self.mode = mode
        self.location = location
        self.played_by = played_by()

    def _path(self, kind: str, name: str = "") -> str:
        return f"{self.namespace}/{kind}/{name}" if name else f"{self.namespace}/{kind}"

    # Results.

    def has_result(self, key: str) -> bool:
        """Whether a match has a result."""
        return self.backend.exists(self._path("results", f"{key}.json"))

    def fetch(self, key: str, directory: Path) -> dict[str, Any] | None:
        """A match's result, with its demo copied into ``directory`` (the local cache); None without one.

        The demo is written first and the result second, as in the store, so
        the local cache never holds a result without its demo. A failure kept
        as the result after ``MAX_FAILED_ATTEMPTS`` may have no demo: it is
        returned and not copied.
        """
        found = self.backend.read(self._path("results", f"{key}.json"))
        if found is None:
            return None
        result = json.loads(found[0])
        demo = self.backend.read(self._path("results", f"{key}.json.gz"))
        if demo is None:
            return result
        directory.mkdir(parents=True, exist_ok=True)
        _write_file(directory / f"{key}.json.gz", demo[0])
        _write_file(directory / f"{key}.json", found[0])
        return result | {"demo": str(directory / f"{key}.json.gz")}

    def put_result(self, key: str, result: dict[str, Any], demo: bytes | None) -> None:
        """Write a match's result, its demo first: the result counts once its ``.json`` is there."""
        if self.mode == "request":
            raise RuntimeError("a store in request mode never writes a result")
        if demo is not None:
            self.backend.write(self._path("results", f"{key}.json.gz"), demo)
        kept = {name: value for name, value in result.items() if name != "demo"} | {"played_by": self.played_by}
        self.backend.write(self._path("results", f"{key}.json"), json.dumps(kept).encode())

    def failures(self, key: str) -> int:
        """How many attempts at a match failed a turn."""
        count = 0
        while self.backend.exists(self._path("failed", f"{key}-{count + 1}.json")):
            count += 1
        return count

    def record_failure(self, key: str, result: dict[str, Any]) -> int:
        """Keep an attempt that failed a turn, without counting it as the result; returns which attempt it was."""
        if self.mode == "request":
            raise RuntimeError("a store in request mode never writes a result")
        kept = {name: value for name, value in result.items() if name != "demo"} | {"played_by": self.played_by}
        attempt = self.failures(key) + 1
        while self.backend.create(self._path("failed", f"{key}-{attempt}.json"), json.dumps(kept).encode()) is None:
            attempt += 1
        return attempt

    # Leases.

    def _lease_body(self, seconds: float) -> tuple[bytes, float]:
        expires = time.time() + seconds
        body = self.played_by | {"expires": expires, "nonce": uuid.uuid4().hex}
        return json.dumps(body).encode(), expires

    def holder(self, key: str) -> dict[str, Any] | None:
        """Who holds a match's lease (machine, run, expires, and ``expired``), or None when nobody does."""
        found = self.backend.read(self._path("leases", key))
        if found is None:
            return None
        try:
            lease = json.loads(found[0])
            expires = float(lease["expires"])
        except ValueError, KeyError, TypeError:
            # A broken lease holds nothing.
            return {"expires": 0.0, "expired": True, "tag": found[1]}
        return lease | {"expired": expires <= time.time(), "tag": found[1]}

    def lease(self, key: str, seconds: float) -> Lease | None:
        """Lease a match for ``seconds``: None when a live lease of someone else's holds it.

        A lease is made only if there is none, and an expired one is taken
        over only if it is unchanged since it was read: of two machines that
        try, one gets it.
        """
        if self.mode == "request":
            raise RuntimeError("a store in request mode never plays a match")
        path = self._path("leases", key)
        current = self.holder(key)
        if current is not None and not current["expired"]:
            return None
        body, expires = self._lease_body(seconds)
        if current is None:
            tag = self.backend.create(path, body)
        else:
            tag = self.backend.replace(path, body, current["tag"])
        return None if tag is None else Lease(key, tag, expires)

    def renew(self, lease: Lease, seconds: float) -> Lease | None:
        """Extend a lease that is still this machine's; None when it isn't any more."""
        body, expires = self._lease_body(seconds)
        tag = self.backend.replace(self._path("leases", lease.key), body, lease.tag)
        return None if tag is None else replace(lease, tag=tag, expires=expires)

    def release(self, lease: Lease) -> None:
        """Give a lease back, if it is still this machine's."""
        self.backend.delete(self._path("leases", lease.key), lease.tag)

    # Code and maps.

    def put_code(self, fingerprint: str, directory: Path) -> None:
        """Keep a bot's code under its fingerprint, unless it is there already."""
        path = self._path("code", f"{fingerprint}.tar.gz")
        if not self.backend.exists(path):
            self.backend.create(path, pack_bot(directory))

    def code(self, fingerprint: str) -> bytes | None:
        """A bot's code by its fingerprint, as ``pack_bot`` packed it; None when it isn't there."""
        found = self.backend.read(self._path("code", f"{fingerprint}.tar.gz"))
        return None if found is None else found[0]

    def put_map(self, data: bytes) -> str:
        """Keep a map file under its hash, unless it is there already; returns the hash."""
        digest = hashlib.sha256(data).hexdigest()
        path = self._path("maps", f"{digest}.json")
        if not self.backend.exists(path):
            self.backend.create(path, data)
        return digest

    def map_data(self, digest: str) -> bytes | None:
        """A map file by its hash; None when it isn't there or isn't what the hash says."""
        found = self.backend.read(self._path("maps", f"{digest}.json"))
        if found is None or hashlib.sha256(found[0]).hexdigest() != digest:
            return None
        return found[0]

    # The queue.

    def enqueue(self, entry: dict[str, Any]) -> bool:
        """Ask the players for a match, unless it is asked for already; whether it was added."""
        body = entry | {"requested_by": self.played_by, "requested_at": time.time()}
        return self.backend.create(self._path("queue", f"{entry['key']}.json"), json.dumps(body).encode()) is not None

    def queued(self) -> list[str]:
        """The keys of the matches asked for, oldest name first."""
        names = self.backend.names(self._path("queue"))
        return [name.removesuffix(".json") for name in names if name.endswith(".json")]

    def queue_entry(self, key: str) -> dict[str, Any] | None:
        """What was asked for a match: its build, map, seats, fingerprints and settings; None when nothing is."""
        found = self.backend.read(self._path("queue", f"{key}.json"))
        if found is None:
            return None
        try:
            entry = json.loads(found[0])
        except ValueError:
            return {}
        return entry if isinstance(entry, dict) else {}

    def is_queued(self, key: str) -> bool:
        """Whether a match is asked for."""
        return self.backend.exists(self._path("queue", f"{key}.json"))

    def dequeue(self, key: str) -> None:
        """Take a match off the queue."""
        self.backend.delete(self._path("queue", f"{key}.json"))

    def wake_players(self, matches: int) -> int:
        """Start Lambda players for this many requested matches (``LEAGUE_PLAYER_FUNCTION``); how many were started.

        Best effort: without the variable, or when the call fails, the players
        that run on a schedule take the queue.
        """
        function = os.environ.get(FUNCTION_VARIABLE)
        if not function or matches <= 0:
            return 0
        count = min(math.ceil(matches / PLAYER_BATCH), MAX_WOKEN)
        try:
            import boto3  # Only a store with Lambda players needs it.

            client = boto3.client("lambda")
            for _ in range(count):
                payload = json.dumps({"batch": PLAYER_BATCH}).encode()
                client.invoke(FunctionName=function, InvocationType="Event", Payload=payload)
        except Exception as error:  # A player that isn't woken leaves the queue to the schedule.
            print(f"league: couldn't wake the players ({function}): {error}", flush=True)
            return 0
        return count


def _write_file(path: Path, data: bytes) -> None:
    """Write a file that another tournament may be reading: whole or not at all."""
    partial = path.with_name(f".{path.name}.{uuid.uuid4().hex}")
    partial.write_bytes(data)
    os.replace(partial, path)


def open_store(build_hash: str) -> Store | None:
    """The store that ``LEAGUE_STORE`` names, for a runner build, in ``LEAGUE_STORE_MODE``; None when it is unset.

    Raises:
        ValueError: The mode is neither play nor request, or the location names no bucket.
    """
    location = os.environ.get(STORE_VARIABLE, "").strip()
    if not location:
        return None
    mode = os.environ.get(MODE_VARIABLE, "").strip() or "play"
    return Store(backend_at(location), build_hash, mode, location)


class Heartbeat:
    """Renews this machine's leases while it plays their matches, so that a long batch keeps them.

    Use it as a context manager around the playing. A lease that is about to
    end is extended by ``LEASE_MARGIN_SECONDS``; one that someone took over
    meanwhile is dropped (its match is still played and written: a result is
    the same whoever plays it).
    """

    def __init__(self, store: Store, leases: Iterable[Lease], interval: float = 30.0) -> None:
        """Hold these leases, renewing them every ``interval`` seconds."""
        self.store = store
        self.interval = interval
        self.leases = {lease.key: lease for lease in leases}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def pop(self, key: str) -> Lease | None:
        """Stop renewing a match's lease, and return it to be released; None when it is not held."""
        with self._lock:
            return self.leases.pop(key, None)

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            soon = time.time() + LEASE_MARGIN_SECONDS / 2
            with self._lock:
                due = [lease for lease in self.leases.values() if lease.expires < soon]
            for lease in due:
                # Renewed under the lock, so that a match that ends meanwhile is
                # popped with the lease as renewed, whose tag its release needs.
                with self._lock:
                    if self.leases.get(lease.key) is not lease:
                        continue
                    try:
                        renewed = self.store.renew(lease, LEASE_MARGIN_SECONDS)
                    except Exception:  # A renewal that fails is tried again next time.
                        continue
                    if renewed is None:
                        del self.leases[lease.key]
                    else:
                        self.leases[lease.key] = renewed

    def __enter__(self) -> Self:
        """Start renewing."""
        self._thread.start()
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop renewing, and give back every lease still held: its match wasn't played."""
        self._stop.set()
        self._thread.join()
        for lease in list(self.leases.values()):
            with contextlib.suppress(Exception):
                self.store.release(lease)
        self.leases.clear()
