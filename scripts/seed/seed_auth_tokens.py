# seed/seed_auth_tokens.py
from __future__ import annotations

import datetime as dt
import hashlib
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.registration_otp import RegistrationOTP
from app.models.user import User

try:
    from app.models.password_reset_token import PasswordResetToken
except Exception:  # pragma: no cover
    PasswordResetToken = None  # type: ignore


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def seed_auth_tokens(session: Session) -> tuple[list[RegistrationOTP], list]:
    users = session.execute(select(User)).scalars().all()
    if not users:
        raise RuntimeError("Seed users first.")

    rnd = random.Random(333)
    now = dt.datetime.utcnow()

    otps: list[RegistrationOTP] = []
    resets: list = []

    # OTPs for a few emails (including non-users to test registration)
    emails = [u.email for u in users[:5]] + ["new.user1@example.com", "new.user2@example.com"]
    for e in emails:
        code = f"{rnd.randint(100000, 999999)}"
        otps.append(RegistrationOTP(email=e, code_hash=_sha(code), expires_at=now + dt.timedelta(minutes=15), is_used=False))

    for o in otps:
        session.add(o)

    # Password reset tokens for existing users (only if model/table exists)
    if PasswordResetToken is not None:
        for u in users[:6]:
            raw = f"reset_{u.id}_{rnd.randint(1, 10_000)}"
            resets.append(PasswordResetToken(user_id=u.id, token_hash=_sha(raw), expires_at=now + dt.timedelta(hours=2)))
        for r in resets:
            session.add(r)

    session.flush()
    return otps, resets