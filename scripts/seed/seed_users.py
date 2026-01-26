# seed/seed_users.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import Role
from app.models.user import User


def _ensure_user(
    session: Session,
    *,
    email: str,
    full_name: str,
    password_hash: str,
    role: Role,
    default_branch_id: int | None,
    phone: str | None = None,
    membership_tier: str | None = None,
) -> User:
    u = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if u:
        updated = False
        for k, v in {
            "full_name": full_name,
            "role": role,
            "default_branch_id": default_branch_id,
            "phone": phone,
            "membership_tier": membership_tier or getattr(u, "membership_tier", None),
        }.items():
            if v is not None and getattr(u, k, None) != v:
                setattr(u, k, v); updated = True
        if hasattr(u, "is_active") and u.is_active is False:
            u.is_active = True; updated = True
        if updated:
            session.add(u)
        return u

    u = User(
        email=email,
        full_name=full_name,
        phone=phone,
        password_hash=password_hash,
        role=role,
        default_branch_id=default_branch_id,
        membership_tier=membership_tier or "FREE",
    )
    session.add(u)
    return u


def seed_users(session: Session, *, default_branch_id: int | None, password: str = "Mami2026!") -> list[User]:
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)

    customers = [
        ("noam.levi@example.com", "Noam Levi", "050-111-2233", "FREE"),
        ("yael.cohen@example.com", "Yael Cohen", "052-234-7788", "PREMIUM"),
        ("itamari.ben@example.com", "Itamari Ben-David", "054-987-6655", "FREE"),
        ("dana.levy@example.com", "Dana Levy", "053-556-1122", "FREE"),
        ("roee.mizrahi@example.com", "Roee Mizrahi", "050-778-9001", "PREMIUM"),
        ("shira.peretz@example.com", "Shira Peretz", "052-665-4433", "FREE"),
        ("lior.shani@example.com", "Lior Shani", "054-212-3434", "FREE"),
        ("omer.golan@example.com", "Omer Golan", "053-909-1010", "PREMIUM"),
        ("maya.katz@example.com", "Maya Katz", "050-404-8080", "FREE"),
        ("tomer.dahan@example.com", "Tomer Dahan", "052-707-1212", "FREE"),
    ]

    staff = [
        ("employee1@mami.local", "Mami Employee", Role.EMPLOYEE),
        ("employee2@mami.local", "Ops Employee", Role.EMPLOYEE),
        ("manager@mami.local", "Mami Manager", Role.MANAGER),
        ("admin@mami.local", "Mami Admin", Role.ADMIN),
    ]

    created: list[User] = []
    for email, name, phone, tier in customers:
        created.append(_ensure_user(session, email=email, full_name=name, phone=phone, membership_tier=tier, password_hash=pwd, role=Role.CUSTOMER, default_branch_id=default_branch_id))
    for email, name, role in staff:
        created.append(_ensure_user(session, email=email, full_name=name, phone=None, membership_tier="FREE", password_hash=pwd, role=role, default_branch_id=default_branch_id))

    session.flush()
    return created