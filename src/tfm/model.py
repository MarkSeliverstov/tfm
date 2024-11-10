from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int
    initial_balance: float
    current_balance: float
    created_at: datetime
    updated_at: datetime
    transactions_types: list[str] = field(default_factory=list)


@dataclass
class Transaction:
    user_id: int
    amount: float
    transaction_date: datetime
    transaction_type: str
    description: str
