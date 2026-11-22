"""The owner's sign-in: only the owner's Google account opens the home page and the games.

The page signs in as the game's web client does (Google Identity Services' button, and a
silent sign-in once the owner has signed in before). Google's button gives the page an ID
token; the page POSTs it to ``/sign-in``, which asks Google whether it is genuine
(``tokeninfo``), checks that it was made for this page's client ID and names the owner's
verified address, and answers with a session cookie. The cookie holds only its expiry and a
MAC: nothing of Google's is kept, and changing ``OWNER_EMAIL``, ``GOOGLE_CLIENT_ID`` or
``SESSION_SECRET`` ends every session.

Without all three settings nobody can sign in, and the page stays closed.
"""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# Google's check of an ID token: its answer is the token's claims, or an error status.
TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
ISSUERS = ("accounts.google.com", "https://accounts.google.com")
COOKIE = "owner_session"
SESSION_SECONDS = 30 * 24 * 3600


class Refused(Exception):
    """A credential that doesn't sign the owner in, and why."""


@dataclass(frozen=True)
class Owner:
    """Who may sign in, and the secret that signs their sessions."""

    client_id: str
    emails: frozenset[str]
    secret: str

    @classmethod
    def from_settings(cls, client_id: str, emails: str, secret: str) -> Owner:
        """The owner from the function's variables; ``OWNER_EMAIL`` may list several, comma-separated."""
        return cls(
            client_id.strip(),
            frozenset(email.strip().lower() for email in emails.split(",") if email.strip()),
            secret,
        )

    @property
    def ready(self) -> bool:
        """Whether anyone can sign in: a client ID, an owner and a secret are all set."""
        return bool(self.client_id and self.emails and len(self.secret) >= 16)

    def check(self, claims: dict[str, Any], now: float) -> str:
        """The owner's address, when Google's claims of a credential sign the owner in."""
        if claims.get("aud") != self.client_id:
            raise Refused("the credential was made for another page")
        if claims.get("iss") not in ISSUERS:
            raise Refused("the credential isn't Google's")
        if int(claims.get("exp") or 0) <= now:
            raise Refused("the credential has expired")
        if str(claims.get("email_verified")).lower() != "true":
            raise Refused("the Google account's address isn't verified")
        email = str(claims.get("email") or "").lower()
        if email not in self.emails:
            raise Refused("this page is its owner's alone")
        return email

    def sign_in(self, credential: str, tokeninfo: Callable[[str], dict[str, Any]], now: float) -> str:
        """A session cookie's value for a credential that signs the owner in."""
        if not self.ready:
            raise Refused("sign-in isn't set up")
        if not credential or len(credential) > 4096:
            raise Refused("no credential")
        self.check(tokeninfo(credential), now)
        return self.session(int(now) + SESSION_SECONDS)

    def session(self, expires: int) -> str:
        """A session cookie's value that lasts until ``expires``."""
        return f"{expires}.{self._mac(expires)}"

    def signed_in(self, cookie: str | None, now: float) -> bool:
        """Whether a session cookie's value is the owner's and still lasts."""
        if not self.ready or not cookie:
            return False
        expires, _, mac = cookie.partition(".")
        if not expires.isdigit() or int(expires) <= now:
            return False
        return hmac.compare_digest(mac.encode(), self._mac(int(expires)).encode())

    def _mac(self, expires: int) -> str:
        message = f"{expires}|{self.client_id}|{','.join(sorted(self.emails))}".encode()
        return hmac.new(self.secret.encode(), message, hashlib.sha256).hexdigest()


def cookie_value(event: dict[str, Any]) -> str | None:
    """The session cookie of a function URL request, if it has one."""
    cookies = list(event.get("cookies") or [])
    header = (event.get("headers") or {}).get("cookie")
    if header:
        cookies.extend(header.split(";"))
    for cookie in cookies:
        name, _, value = cookie.strip().partition("=")
        if name == COOKIE:
            return value
    return None


def set_cookie(value: str, max_age: int) -> str:
    """The ``Set-Cookie`` of a session, or of its end with an empty value and no age."""
    return f"{COOKIE}={value}; Max-Age={max_age}; Path=/; Secure; HttpOnly; SameSite=Lax"
