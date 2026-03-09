from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import crud
import schemas
from database import SessionLocal, engine, Base

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartOps Life ERP API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartOps Life ERP API"}

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, tx=tx)

@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)

@app.post("/buckets", response_model=schemas.BucketResponse)
def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(get_db)):
    return crud.create_bucket(db=db, bucket=bucket)

@app.get("/buckets", response_model=list[schemas.BucketResponse])
def get_buckets(db: Session = Depends(get_db)):
    return crud.get_buckets(db)

@app.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    power_data = crud.get_daily_power(db)
    debts = crud.get_debts(db)
    return {
        "daily_power": power_data["daily_power"],
        "penalty_days": power_data["penalty_days"],
        "debt_bosses": debts
    }

@app.post("/reset_monday")
def trigger_monday_reset(db: Session = Depends(get_db)):
    config = crud.perform_monday_reset(db)
    return {"message": "Monday reset complete.", "new_weekly_pool": config.current_weekly_pool}
