import enum
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base

class TransactionType(str, enum.Enum):
    income = "Income"
    expense = "Expense"
    apartado = "Apartado"
    defense = "Defense" # For paying debts

class UsersConfig(Base):
    __tablename__ = "users_config"
    id = Column(Integer, primary_key=True, index=True)
    weekly_base_budget = Column(Float, default=500.0)
    next_week_buff_pct = Column(Float, default=0.30)
    daily_multiplier = Column(Float, default=1.0)
    current_weekly_pool = Column(Float, default=500.0)

class Bucket(Base):
    __tablename__ = "buckets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    current_balance = Column(Float, default=0.0)
    target_balance = Column(Float, default=0.0)

class Ledger(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category_id = Column(Integer, ForeignKey("buckets.id"), nullable=True) # Used if type is Apartado (Virtual bucket)
    description = Column(String)
    account_source = Column(String)

class Debt(Base):
    __tablename__ = "debts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    total_hp = Column(Float, default=0.0) # Represents the remaining debt
    monthly_payment = Column(Float, default=0.0)
    due_date = Column(Integer) # Day of the month to pay

class FixedExpense(Base):
    __tablename__ = "fixed_expenses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    amount = Column(Float, default=0.0)
    recurrence = Column(String) # Weekly, Monthly
    last_paid = Column(DateTime, nullable=True)
