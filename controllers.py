from turtle import update
from fastapi import Depends, HTTPException
from models import Transaction
from schemas import CreateUser, UserResponse, UpdateUser, TRANSACTION_TYPES, WalletBalance
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
    transaction = Transaction(
        user_id=user_id,
        transaction_type="CREDIT",
        amount=amount,
        description="Add wallet balance",
        reference_transaction_id=None,
    )
    db.add(transaction)
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
    transaction = Transaction(
        user_id=user_id,
        transaction_type="DEBIT",
        amount=amount,
        description="Withdraw wallet balance",
        reference_transaction_id=None,
    )
    db.add(transaction)
    db.commit()
    db.refresh(user)
    return user


# money transfer to another user
async def money_transfer(user_id: int, recipient_user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(UserResponse).filter(UserResponse.id == user_id)).first()
    recipient_user = db.execute(select(UserResponse).filter(UserResponse.id == recipient_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    user.balance -= amount
    recipient_user.balance += amount
    transaction = Transaction(
        user_id=user_id,
        transaction_type="TRANSFER_OUT",
        amount=amount,
        description="Money transfer to another user",
        reference_transaction_id=None,
    )
    db.add(transaction)
    db.commit()
    db.refresh(user)
    db.refresh(recipient_user)
    return user
