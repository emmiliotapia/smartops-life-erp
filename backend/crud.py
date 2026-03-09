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
    
    daily_power = config.current_weekly_pool / 6.0
    penalty_days = 0
    
    if fanny_bucket and fanny_bucket.current_balance < 0:
        # Days = (|Fanny_Balance| / (Daily_Personal_Budget * 0.25)) + 1
        daily_personal_budget = daily_power # Assuming daily power is personal budget
        if daily_personal_budget > 0:
            penalty_days = (abs(fanny_bucket.current_balance) / (daily_personal_budget * 0.25)) + 1
            
    return {"daily_power": daily_power, "penalty_days": penalty_days}

def perform_monday_reset(db: Session):
    config = get_config(db)
    # Logic: weekly_base_budget + carry_over + 30%_extra_income
    # This is a stub for the background task or manual trigger
    # In a full implementation, carry_over and extra_income would be calculated from ledger records
    carry_over = 0 # Calculate from previous week unspent amount
    extra_income = 0 # Calculate from Income type transactions
    buff = extra_income * config.next_week_buff_pct
    
    config.current_weekly_pool = config.weekly_base_budget + carry_over + buff
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

def create_transaction(db: Session, tx: schemas.TransactionCreate):
    db_tx = models.Ledger(**tx.model_dump())
    
    # Business Logic
    if tx.type == models.TransactionType.apartado and tx.category_id:
        # Update virtual balance of bucket without affecting total bank.
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
