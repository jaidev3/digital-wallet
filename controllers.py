from turtle import update
from fastapi import Depends, HTTPException
from schemas import Transaction, CreateUser, UserResponse, UpdateUser
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, update

async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    db.add(**user.model_dump())
    db.commit()
    db.refresh(user)
    return user

async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserResponse).filter(UserResponse.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    db.execute(update(UserResponse).filter(UserResponse.id == user_id), user.model_dump())
    db.commit()
    db.refresh(user)
    return user

#  get wallet balance of user
async def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserResponse).filter(UserResponse.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.balance

#  add wallet balance of user
async def add_wallet_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(UserResponse).filter(UserResponse.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += amount
    db.commit()
    db.refresh(user)
    return user

#  withdraw wallet balance of user
async def withdraw_wallet_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(UserResponse).filter(UserResponse.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    user.balance -= amount
    db.commit()
    db.refresh(user)
    return user

async def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    db.add(**transaction.model_dump())
    db.commit()
    db.refresh(transaction)
    return transaction

