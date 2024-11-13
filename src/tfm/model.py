from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class User:
    id: int
    initial_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
    transactions_types: list[str] = field(default_factory=list)


@dataclass
class Transaction:
    user_id: int
    amount: Decimal
    transaction_date: datetime
    transaction_type: str
    description: str
