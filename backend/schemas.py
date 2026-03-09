from pydantic import BaseModel
from typing import Optional, List
import datetime
from models import TransactionType

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category_id: Optional[int] = None
    description: Optional[str] = None
    account_source: Optional[str] = "Main"

class TransactionResponse(TransactionCreate):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class BucketCreate(BaseModel):
    name: str
    target_balance: Optional[float] = 0.0

class BucketResponse(BucketCreate):
    id: int
    current_balance: float

    class Config:
        from_attributes = True

class DebtCreate(BaseModel):
    name: str
    total_hp: float
    monthly_payment: float
    due_date: int

class DebtResponse(DebtCreate):
    id: int

    class Config:
        from_attributes = True
