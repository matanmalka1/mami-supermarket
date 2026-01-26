# seed/seed_orders_helpers.py
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from app.models.delivery_slot import DeliverySlot


def next_slot_window(slot: DeliverySlot, *, now: dt.datetime) -> tuple[dt.datetime, dt.datetime]:
    """Return next datetime window matching slot.day_of_week/start/end (0=Sun)."""
    # Python: Monday=0..Sunday=6. Our model: Sunday=0..Saturday=6.
    target_py = (slot.day_of_week - 1) % 7
    days_ahead = (target_py - now.weekday()) % 7
    if days_ahead == 0:
        # If we're past today's end time, move to next week.
        end_today = now.replace(hour=slot.end_time.hour, minute=slot.end_time.minute, second=0, microsecond=0)
        if now >= end_today:
            days_ahead = 7
    day = (now + dt.timedelta(days=days_ahead)).date()
    start = dt.datetime.combine(day, slot.start_time)
    end = dt.datetime.combine(day, slot.end_time)
    return start, end


def sum_lines(lines: list[tuple[Decimal, int]]) -> Decimal:
    total = Decimal("0.00")
    for unit_price, qty in lines:
        total += unit_price * qty
    return total