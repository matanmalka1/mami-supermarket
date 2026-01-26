# seed/seed_branches.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.branch import Branch

def _ensure_branch(session: Session, *, name: str, address: str) -> Branch:
    b = session.execute(select(Branch).where(Branch.name == name)).scalar_one_or_none()
    if b:
        updated = False
        if hasattr(b, "is_active") and b.is_active is False:
            b.is_active = True; updated = True
        if b.address != address:
            b.address = address; updated = True
        if updated:
            session.add(b)
        return b
    b = Branch(name=name, address=address); session.add(b); return b


def seed_branches(session: Session) -> list[Branch]:
    data = [
        ("Mami - Tel Aviv (Dizengoff)", "123 Dizengoff St, Tel Aviv-Yafo, Israel"),
        ("Mami - Tel Aviv (Yarkon)", "180 HaYarkon St, Tel Aviv-Yafo, Israel"),
        ("Mami - Rishon LeZion", "15 Rothschild Blvd, Rishon LeZion, Israel"),
        ("Mami - Ramat Gan", "3 Ben Gurion Rd, Ramat Gan, Israel"),
    ]
    created: list[Branch] = []
    for name, address in data:
        created.append(_ensure_branch(session, name=name, address=address))
    session.flush()
    return created