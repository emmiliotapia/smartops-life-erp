import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
import models
import schemas

def get_config(db: Session):
    config = db.query(models.UsersConfig).first()
    if not config:
        config = models.UsersConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

def get_daily_power(db: Session):
    config = get_config(db)
    # The Penalty Rule: If bucket 'Fanny' balance < 0
    fanny_bucket = db.query(models.Bucket).filter(models.Bucket.name == "Fanny").first()
    
    # 1. Base Calculation
    daily_power = config.current_weekly_pool / 6.0
    penalty_days = 0
    
    if fanny_bucket and fanny_bucket.current_balance < 0:
        daily_personal_budget = daily_power
        if daily_personal_budget > 0:
            penalty_days = (abs(fanny_bucket.current_balance) / (daily_personal_budget * 0.25)) + 1
            
    # 2. Daily Power 14-Day Projection
    # This acts as a mockup projection for the Next 14 days based on the current daily power.
    # In a real app, it would look at recurring expenses.
    projections = [round(daily_power, 2) for _ in range(14)]
            
    return {"daily_power": daily_power, "penalty_days": penalty_days, "projections": projections, "state": config.current_state.value}

def update_state(db: Session, config: models.UsersConfig):
    total_debt = db.query(func.sum(models.Debt.total_hp)).scalar() or 0.0
    if total_debt > 0:
        config.current_state = models.State.guerra
    else:
        config.current_state = models.State.expansion
    return config

def perform_monday_reset(db: Session):
    config = get_config(db)
    config = update_state(db, config)
    
    # Logic: weekly_base_budget + carry_over + extra_income_distribution
    last_reset = db.query(models.Ledger).filter(models.Ledger.description == "[SYSTEM_RESET]").order_by(models.Ledger.timestamp.desc()).first()
    since_date = last_reset.timestamp if last_reset else datetime.datetime.min
    
    # Calculate extra income since last reset
    extra_income = db.query(func.sum(models.Ledger.amount)).filter(
        models.Ledger.type == models.TransactionType.income,
        models.Ledger.description != "[SYSTEM_RESET]",
        models.Ledger.timestamp >= since_date
    ).scalar() or 0.0
    
    buff = 0.0
    total_debt = db.query(func.sum(models.Debt.total_hp)).scalar() or 0.0
    
    if config.current_state == models.State.guerra:
        buff = extra_income * 0.30
        # 70% to Debt Boss Raid is symbolic here, should theoretically create defense transactions automatically
    else:
        buff = extra_income * 0.30
        config.luxury_vault_pool += extra_income * 0.30
        config.investment_vault_pool += extra_income * 0.40
    
    # Stub for carry_over (would be tracked dynamically)
    carry_over = 0.0 
    
    config.current_weekly_pool = config.weekly_base_budget + carry_over + buff
    
    # Log reset
    reset_tx = models.Ledger(amount=config.current_weekly_pool, type=models.TransactionType.income, description="[SYSTEM_RESET]")
    db.add(reset_tx)
    db.commit()
    
    return config

def get_debts(db: Session):
    return db.query(models.Debt).all()

def create_bucket(db: Session, bucket: schemas.BucketCreate):
    db_bucket = models.Bucket(**bucket.model_dump())
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def get_buckets(db: Session):
    return db.query(models.Bucket).all()

from fastapi import HTTPException

# ... (We must import HTTPException in crud.py if resolving there, however it's better to raise standard python exceptions and let fastapi catch them or just raise HTTPException)

def create_transaction(db: Session, tx: schemas.TransactionCreate):
    # Failsafe Logic for Apartados (Vaults)
    if tx.type == models.TransactionType.expense and tx.category_id:
        bucket = db.query(models.Bucket).filter(models.Bucket.id == tx.category_id).first()
        if bucket:
            if bucket.current_balance < tx.amount:
                raise ValueError("[ SYSTEM_ERROR: INSUFFICIENT_FUNDS_IN_VAULT ]")
            bucket.current_balance -= tx.amount
                
    db_tx = models.Ledger(**tx.model_dump())
    
    # Business Logic for Income / Apartado transfers
    if tx.type == models.TransactionType.apartado and tx.category_id:
        # Update virtual balance of bucket securely
        bucket = db.query(models.Bucket).filter(models.Bucket.id == tx.category_id).first()
        if bucket:
            bucket.current_balance += tx.amount
    elif tx.type == models.TransactionType.defense and tx.category_id:
        # Reduce Debt HP
        debt = db.query(models.Debt).filter(models.Debt.id == tx.category_id).first()
        if debt:
            debt.total_hp -= tx.amount
            if debt.total_hp < 0:
                debt.total_hp = 0
                
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ledger).offset(skip).limit(limit).all()
