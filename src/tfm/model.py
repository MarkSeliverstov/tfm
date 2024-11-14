from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class User:
    id: int
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
    transactions_types: list[str] = field(default_factory=list)


@dataclass
class Transaction:
    amount: Decimal
    created_at: datetime
    description: str

    def __str__(self) -> str:
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.amount} {self.description}"
