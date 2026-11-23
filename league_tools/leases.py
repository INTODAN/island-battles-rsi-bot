"""Leases: work that should happen once in the league, held by one run at a time.

Runs work in parallel (docs/parallel-iterations.md). Besides the matches, which
the store plays once, some work should happen once too: a real game studied, a
league game read, a place of the slate (``league ideas``), an idea, a bot's or a
map's name. A run leases each before it starts on it, and the lease is created
only if nobody holds it, atomically. Kinds:

- ``run/<id>``: the run itself, from start to integration. ``league lease run``
  makes the id, ``<date>-<6 hex>``.
- ``real/<game id>``, ``study/<match key>``, ``slot/<champion>/<place>``,
  ``idea/<hash>``, ``name/<bot or map>``.

A lease holds the run's id and when it expires (an hour after it was taken or
renewed): a run renews its leases while it works (``league lease renew``), so a
dead run frees its places within the hour. An expired lease is taken over, and
the takeover is atomic too: of two runs, one gets it.

Two backends, chosen by ``LEAGUE_STORE``: the store's (a lease is an object
created only if absent) when it is set, else git refs on origin
(``refs/league/leases/<kind>/<name>``, pushed only if absent, as
``scripts/claim-iteration.sh`` pushes a claim), which any session with push
access can use.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .paths import LEAGUE

KEY = re.compile(r"^(run|real|study|slot|idea|name)/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")
HOURS = 1.0
REF_PREFIX = "refs/league/leases/"


@dataclass
class Lease:
    """Who holds a key, and until when."""

    key: str
    run: str
    expires: str

    def expired(self, now: datetime.datetime | None = None) -> bool:
        """Whether the lease has run out."""
        moment = now or datetime.datetime.now(datetime.UTC)
        return datetime.datetime.fromisoformat(self.expires) <= moment

    def text(self) -> str:
        """The lease as stored."""
        return json.dumps({"key": self.key, "run": self.run, "expires": self.expires}, sort_keys=True)

    @classmethod
    def parse(cls, text: str) -> Lease:
        """A lease from its stored text."""
        data = json.loads(text)
        return cls(data["key"], data["run"], data["expires"])


class Backend(Protocol):
    """Where leases live: create only if absent, replace only if unchanged, delete, list."""

    def create(self, key: str, text: str) -> bool:
        """Create the key's ref; False when it exists."""
        """Create the key's lease; False when one exists."""
        raise NotImplementedError

    def read(self, key: str) -> tuple[str, str] | None:
        """The key's lease text and the commit its ref points at, or None."""
        """The key's lease text and its version, or None."""
        raise NotImplementedError

    def replace(self, key: str, version: str, text: str) -> bool:
        """Point the key's ref at a new lease if it still points at version."""
        """Replace the key's lease if its version is still this one."""
        raise NotImplementedError

    def delete(self, key: str, version: str) -> bool:
        """Delete the key's ref if it still points at version."""
        """Delete the key's lease if its version is still this one."""
        raise NotImplementedError

    def keys(self, prefix: str) -> list[str]:
        """The keys under a prefix that have a ref on the remote."""
        """The keys under a prefix that have a lease."""
        raise NotImplementedError


def check_key(key: str) -> str:
    """The key, if it is one.

    Raises:
        ValueError: It isn't a lease's key.
    """
    if not KEY.match(key) or ".." in key:
        raise ValueError(f"{key!r} is not a lease's key (run/, real/, study/, slot/, idea/ or name/, then a name)")
    return key


def new_run_id(now: datetime.datetime | None = None) -> str:
    """A new run's id: the date and six random hex digits."""
    moment = now or datetime.datetime.now(datetime.UTC)
    return f"{moment:%Y%m%d}-{secrets.token_hex(3)}"


def _until(hours: float = HOURS) -> str:
    return (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=hours)).isoformat(timespec="seconds")


def take(backend: Backend, key: str, run: str, hours: float = HOURS, tries: int = 3) -> Lease:
    """Take a key for a run. Returns the run's lease, or the lease of whoever holds it.

    The run already holding it renews it. An expired lease is taken over.

    Raises:
        RuntimeError: The lease could be neither created nor read: the backend refuses this
            machine's writes (no push access to the remote, no write to the store's leases).
    """
    lease = Lease(check_key(key), run, _until(hours))
    for _ in range(tries):
        if backend.create(key, lease.text()):
            return lease
        found = backend.read(key)
        if found is None:
            continue
        text, version = found
        held = Lease.parse(text)
        if held.run != run and not held.expired():
            return held
        if backend.replace(key, version, lease.text()):
            return lease
    raise RuntimeError(f"can't take or read the lease {key}: does this machine have write access to the leases?")


def release(backend: Backend, key: str, run: str) -> bool:
    """Give a key back, only if the run holds it."""
    found = backend.read(check_key(key))
    if found is None or Lease.parse(found[0]).run != run:
        return False
    return backend.delete(key, found[1])


def held(backend: Backend, prefix: str = "") -> list[Lease]:
    """Every lease that hasn't expired, under a prefix."""
    leases = []
    for key in backend.keys(prefix):
        found = backend.read(key)
        if found is not None:
            lease = Lease.parse(found[0])
            if not lease.expired():
                leases.append(lease)
    return sorted(leases, key=lambda lease: lease.key)


def drop(backend: Backend, run: str) -> list[str]:
    """Give back every lease a run holds, as the integrator does once the run is integrated; returns their keys."""
    dropped = []
    for key in backend.keys(""):
        found = backend.read(key)
        if found is not None and Lease.parse(found[0]).run == run and backend.delete(key, found[1]):
            dropped.append(key)
    return dropped


def renew(backend: Backend, run: str, hours: float = HOURS) -> list[str]:
    """Renew every lease a run holds; returns their keys."""
    renewed = []
    for key in backend.keys(""):
        found = backend.read(key)
        if found is not None and Lease.parse(found[0]).run == run:
            if backend.replace(key, found[1], Lease(key, run, _until(hours)).text()):
                renewed.append(key)
    return renewed


class GitRefs:
    """Leases as refs on a git remote: ``refs/league/leases/<key>``, each a commit whose message is the lease.

    A push with ``--force-with-lease=<ref>:`` creates a ref only if it doesn't
    exist, and with ``<ref>:<sha>`` replaces or deletes it only if it still
    points there: the remote decides, atomically.
    """

    def __init__(self, cwd: Path = LEAGUE, remote: str = "origin", push_url: str | None = None) -> None:
        """Leases on ``remote``, read from the clone at ``cwd``, pushed to ``push_url`` (``LEASE_PUSH_URL``)."""
        self.cwd = cwd
        self.remote = remote
        self.push_url = push_url or os.environ.get("LEASE_PUSH_URL") or remote

    def _git(self, *arguments: str, check: bool = True, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        identity = {
            "GIT_AUTHOR_NAME": "league lease",
            "GIT_AUTHOR_EMAIL": "league-lease@users.noreply.github.com",
            "GIT_COMMITTER_NAME": "league lease",
            "GIT_COMMITTER_EMAIL": "league-lease@users.noreply.github.com",
        }
        return subprocess.run(
            ["git", *arguments],
            cwd=self.cwd,
            check=check,
            capture_output=True,
            text=True,
            input=stdin,
            env=os.environ | identity,
        )

    def _commit(self, text: str) -> str:
        tree = self._git("mktree", stdin="").stdout.strip()
        return self._git("commit-tree", tree, "-m", text).stdout.strip()

    def _push(self, ref: str, expected: str, value: str) -> bool:
        pushed = self._git("push", "-q", f"--force-with-lease={ref}:{expected}", self.push_url, value, check=False)
        return pushed.returncode == 0

    def create(self, key: str, text: str) -> bool:
        """Create the key's ref; False when it exists."""
        ref = REF_PREFIX + key
        return self._push(ref, "", f"{self._commit(text)}:{ref}")

    def read(self, key: str) -> tuple[str, str] | None:
        """The key's lease text and the commit its ref points at, or None."""
        ref = REF_PREFIX + key
        listed = self._git("ls-remote", self.remote, ref).stdout.split()
        if not listed:
            return None
        sha = listed[0]
        self._git("fetch", "-q", self.remote, f"+{ref}:refs/league-leases/{key}", check=False)
        message = self._git("log", "-1", "--format=%B", sha, check=False)
        if message.returncode != 0:
            return None
        return message.stdout.strip(), sha

    def replace(self, key: str, version: str, text: str) -> bool:
        """Point the key's ref at a new lease if it still points at version."""
        ref = REF_PREFIX + key
        return self._push(ref, version, f"{self._commit(text)}:{ref}")

    def delete(self, key: str, version: str) -> bool:
        """Delete the key's ref if it still points at version."""
        ref = REF_PREFIX + key
        return self._push(ref, version, f":{ref}")

    def keys(self, prefix: str) -> list[str]:
        """The keys under a prefix that have a ref on the remote."""
        listed = self._git("ls-remote", self.remote, f"{REF_PREFIX}{prefix}*").stdout.splitlines()
        return sorted(line.split("\t")[1].removeprefix(REF_PREFIX) for line in listed if "\t" in line)


class StoreLeases:
    """Leases as objects of the match store, ``work-leases/<key>`` with its slashes written ``~``.

    One flat directory, since the store lists one level at a time; a key has no
    ``~`` (``KEY``). Not under the store's runner build: a run's leases hold
    whatever runner it plays.
    """

    DIRECTORY = "work-leases"

    def __init__(self, location: str) -> None:
        """Leases in the store at ``location`` (``LEAGUE_STORE``'s value)."""
        from . import store

        self.store = store.backend_at(location)

    def _path(self, key: str) -> str:
        return f"{self.DIRECTORY}/{key.replace('/', '~')}"

    def create(self, key: str, text: str) -> bool:
        """Create the key's lease; False when one exists."""
        return self.store.create(self._path(key), text.encode()) is not None

    def read(self, key: str) -> tuple[str, str] | None:
        """The key's lease text and its tag, or None."""
        found = self.store.read(self._path(key))
        return None if found is None else (found[0].decode(), found[1])

    def replace(self, key: str, version: str, text: str) -> bool:
        """Replace the key's lease if its tag is still this one."""
        return self.store.replace(self._path(key), text.encode(), version) is not None

    def delete(self, key: str, version: str) -> bool:
        """Delete the key's lease if its tag is still this one."""
        return self.store.delete(self._path(key), version)

    def keys(self, prefix: str) -> list[str]:
        """The keys under a prefix that have a lease."""
        keys = (name.replace("~", "/") for name in self.store.names(self.DIRECTORY))
        return sorted(key for key in keys if key.startswith(prefix))


def backend() -> Backend:
    """The league's lease backend: the store's when ``LEAGUE_STORE`` is set, else git refs on origin."""
    location = os.environ.get("LEAGUE_STORE")
    if location:
        return StoreLeases(location)
    return GitRefs()
