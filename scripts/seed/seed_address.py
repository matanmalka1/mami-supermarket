# seed/seed_address.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address


CITY_COORDS: dict[str, tuple[float, float]] = {
    "Tel Aviv-Yafo": (32.0853, 34.7818),
    "Jerusalem": (31.7683, 35.2137),
    "Haifa": (32.7940, 34.9896),
    "Rishon LeZion": (31.9730, 34.7925),
    "Be'er Sheva": (31.2520, 34.7915),
    "Ramat Gan": (32.0823, 34.8105),
    "Petah Tikva": (32.0840, 34.8878),
    "Holon": (32.0150, 34.7874),
    "Herzliya": (32.1640, 34.8440),
    "Netanya": (32.3215, 34.8532),
}


def _ensure_address(session: Session, *, user_id: int, address_line: str, city: str, country: str, postal_code: str, is_default: bool) -> Address:
    a = session.execute(
        select(Address).where(Address.user_id == user_id, Address.address_line == address_line, Address.city == city, Address.postal_code == postal_code)
    ).scalar_one_or_none()

    lat, lng = CITY_COORDS.get(city, (None, None))

    if a:
        updated = False
        if is_default and getattr(a, "is_default", False) is False:
            a.is_default = True; updated = True
        if lat is not None and (a.latitude != lat or a.longitude != lng):
            a.latitude = lat; a.longitude = lng; updated = True
        if updated:
            session.add(a)
        return a

    a = Address(
        user_id=user_id,
        address_line=address_line,
        city=city,
        country=country,
        postal_code=postal_code,
        latitude=lat,
        longitude=lng,
        is_default=is_default,
    )
    session.add(a)
    return a


def seed_addresses(session: Session, user_ids: list[int]) -> list[Address]:
    templates = [
        ("Dizengoff 123, Apt 4", "Tel Aviv-Yafo", "Israel", "6433221"),
        ("Ibn Gabirol 77, Floor 2", "Tel Aviv-Yafo", "Israel", "6433402"),
        ("HaNasi 10", "Haifa", "Israel", "3463807"),
        ("Rothschild Boulevard 15", "Rishon LeZion", "Israel", "7536508"),
        ("Herzl 52", "Rehovot", "Israel", "7642341"),
        ("Ben Gurion 3", "Ramat Gan", "Israel", "5257333"),
        ("Weizmann 19", "Kfar Saba", "Israel", "4432009"),
        ("HaNevi'im 25", "Jerusalem", "Israel", "9510416"),
        ("Jerusalem Blvd 102", "Ashdod", "Israel", "7745120"),
        ("HaAtzmaut 8", "Be'er Sheva", "Israel", "8453210"),
        ("Allenby 99", "Tel Aviv-Yafo", "Israel", "6332111"),
        ("Jabotinsky 45", "Petah Tikva", "Israel", "4951445"),
        ("Begin Blvd 68", "Jerusalem", "Israel", "9136802"),
        ("Hillel 12", "Jerusalem", "Israel", "9458104"),
        ("HaYarkon 180", "Tel Aviv-Yafo", "Israel", "6340506"),
        ("Sderot Chen 5", "Tel Aviv-Yafo", "Israel", "6437305"),
        ("Keren Hayesod 20", "Ramat Gan", "Israel", "5268102"),
        ("HaPalmach 7", "Netanya", "Israel", "4230617"),
        ("Derech HaAtzmaut 50", "Haifa", "Israel", "3303112"),
        ("HaGalil 30", "Nazareth", "Israel", "1610201"),
        ("HaHistadrut 15", "Holon", "Israel", "5822015"),
        ("Sokolov 120", "Herzliya", "Israel", "4653210"),
        ("Bialik 18", "Ramat Gan", "Israel", "5250208"),
        ("HaMaccabi 3", "Givatayim", "Israel", "5332103"),
        ("Shazar Blvd 12", "Be'er Sheva", "Israel", "8411204"),
    ]

    created: list[Address] = []
    for i, user_id in enumerate(user_ids):
        t1 = templates[i % len(templates)]
        created.append(_ensure_address(session, user_id=user_id, address_line=t1[0], city=t1[1], country=t1[2], postal_code=t1[3], is_default=True))

        # second address for some users
        if i % 2 == 0:
            t2 = templates[(i + 5) % len(templates)]
            created.append(_ensure_address(session, user_id=user_id, address_line=t2[0], city=t2[1], country=t2[2], postal_code=t2[3], is_default=False))

    session.flush()
    return created