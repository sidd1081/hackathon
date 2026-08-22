"""Minimal authentication service: SQLite user store + JWT tokens.

Passwords are hashed with PBKDF2-HMAC-SHA256 (Python stdlib — no bcrypt build
dependency). Access tokens are signed JWTs (HS256). The user store is a small
SQLite database; the plaintext password is never stored or logged.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# backend/app/services/auth_service.py -> parents[2] == backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH: Path = _BACKEND_ROOT / "data" / "auth.db"

# PBKDF2 parameters.
_PBKDF2_ALGO = "sha256"
_PBKDF2_ITERATIONS = 200_000
_SALT_BYTES = 16


class AuthError(Exception):
    """Base class for auth failures."""


class EmailExistsError(AuthError):
    """Signup attempted with an email that is already registered."""


class InvalidCredentialsError(AuthError):
    """Login failed (unknown email or wrong password)."""


# --- password hashing ---------------------------------------------------------

def hash_password(password: str) -> str:
    """Return a self-describing PBKDF2 hash: ``pbkdf2_sha256$iter$salt$hash``."""
    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return f"pbkdf2_{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verify a password against a stored PBKDF2 hash."""
    try:
        algo, iterations, salt_hex, hash_hex = stored.split("$")
        assert algo == f"pbkdf2_{_PBKDF2_ALGO}"
        dk = hashlib.pbkdf2_hmac(
            _PBKDF2_ALGO,
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
    except (ValueError, AssertionError):
        return False
    return hmac.compare_digest(dk.hex(), hash_hex)


# --- database -----------------------------------------------------------------

def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the users table if it does not exist (idempotent)."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL
            )
            """
        )
        conn.commit()


def _row_to_user(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def create_user(name: str, email: str, password: str) -> dict:
    """Create a user and return the public dict. Raises EmailExistsError."""
    email = email.strip().lower()
    pw_hash = hash_password(password)
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (name.strip(), email, pw_hash, created_at),
            )
            conn.commit()
            user_id = int(cur.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise EmailExistsError("An account with this email already exists.") from exc
    logger.info("Created user id=%d", user_id)
    return {"id": user_id, "name": name.strip(), "email": email}


def authenticate(email: str, password: str) -> dict:
    """Verify credentials and return the public user dict, else raise."""
    email = email.strip().lower()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        raise InvalidCredentialsError("Incorrect email or password.")
    return _row_to_user(row)


def get_user_by_id(user_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return _row_to_user(row) if row else None


# --- JWT ----------------------------------------------------------------------

def create_access_token(user_id: int) -> str:
    """Create a signed JWT whose subject is the user id."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> int:
    """Decode a JWT and return the user id. Raises jwt exceptions on failure."""
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    return int(payload["sub"])
