from dataclasses import dataclass

@dataclass
class Transaction:
    id: int | None
    date: str
    amount: float
    category: str
    description: str
    type: str  # 'income' or 'expense'

    @staticmethod
    def from_row(row: tuple):
        return Transaction(id=row[0], date=row[1], amount=row[2], category=row[3], description=row[4], type=row[5])
