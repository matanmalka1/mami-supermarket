"""Payment provider stub for tokenized charges."""

from __future__ import annotations
from secrets import token_hex

class PaymentService:
    @staticmethod
    def charge(payment_token_id: int, amount: float) -> str:

        return f"pay_{token_hex(6)}"
