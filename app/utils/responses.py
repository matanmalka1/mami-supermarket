"""Standardized API response envelope helpers."""

from __future__ import annotations

from typing import Any, Mapping


def success_envelope(data: Any, pagination: Mapping[str, Any] | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"data": data}
    if pagination:
        response["pagination"] = pagination
    return response


def error_envelope(code: str, message: str, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def pagination_envelope(total: int, limit: int, offset: int) -> dict[str, int]:
    """Provide consistent pagination metadata."""
    return {"total": total, "limit": limit, "offset": offset}
