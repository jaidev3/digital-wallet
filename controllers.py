from fastapi import Depends, HTTPException
from models import Transaction, User
from schemas import CreateUser, UserResponse, UpdateUser, Transaction, GetAllTransactions
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, update

def create_user(user: CreateUser, db: Session = Depends(get_db)):
    db.add(User(**user.model_dump()))
    db.commit()
    # db.refresh(user)
    return user

def get_user(user_id: int, db: Session = Depends(get_db)):
    print("user_id", user_id)
    #  retur user without password
    user = db.execute(select(User).filter(User.id == user_id))
    user = user.scalar()
    user.password = None
    return user

def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    #  update data in user database
    user = user.model_dump()
    db.execute(update(User).filter(User.id == user_id), user)
    db.commit()
    # db.refresh(user)
    return user

#  get wallet balance of user
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == user_id))
    user = user.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.balance

#  add wallet balance of user
def add_wallet_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == user_id))
    user = user.model_dump()
    print("user1", user)
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
def withdraw_wallet_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == user_id))
    user = user.scalar()
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
def money_transfer(user_id: int, recipient_user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == user_id))
    user = user.scalar()
    recipient_user = db.execute(select(User).filter(User.id == recipient_user_id))
    recipient_user = recipient_user.scalar()
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


# get all transactions of user
def get_all_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.execute(select(Transaction).filter(Transaction.user_id == user_id))
    transactions = transactions.scalar()
    return transactions