from __future__ import annotations
from uuid import UUID

def toggle_flag(args) -> bool:
    active = args.get("active")
    return active != "false"

def safe_int(args, name: str, default: int) -> int:
    try:
        return int(args.get(name, default))
    except (TypeError, ValueError):
        return default

def optional_uuid(args, name: str) -> UUID | None:
    value = args.get(name)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None
