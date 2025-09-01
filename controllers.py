from fastapi import Depends, HTTPException, Query
from models import Transaction, User
from schemas import CreateUser, UserResponse, UpdateUser, GetAllTransactions, PaginationParams, PaginatedResponse
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
import math

def create_user(user: CreateUser, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(user_id: int, db: Session = Depends(get_db)):
    print("user_id", user_id)
    #  return user without password
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    if user:
        user.password = None
    return user

def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    #  update data in user database
    user_data = user.model_dump(exclude_unset=True)
    db.execute(update(User).where(User.id == user_id).values(**user_data))
    db.commit()
    # Get updated user
    updated_user = db.execute(select(User).where(User.id == user_id)).scalar()
    return updated_user

#  get wallet balance of user
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.balance

#  add wallet balance of user
def add_wallet_balance(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar()
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
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    print("user2", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    print("user3", user.balance)
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
    user = db.execute(select(User).where(User.id == user_id)).scalar()
    recipient_user = db.execute(select(User).where(User.id == recipient_user_id)).scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
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


# get all transactions of user with pagination
def get_all_transactions(user_id: int, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    # Get total count
    total_count = db.execute(select(func.count(Transaction.id)).where(Transaction.user_id == user_id)).scalar()
    
    # Calculate pagination
    offset = (page - 1) * page_size
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    
    # Get paginated transactions
    transactions = db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    ).scalars().all()
    
    return PaginatedResponse(
        items=transactions,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

# get all users with pagination
def get_all_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    # Get total count
    total_count = db.execute(select(func.count(User.id))).scalar()
    
    # Calculate pagination
    offset = (page - 1) * page_size
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    
    # Get paginated users (without password)
    users = db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    ).scalars().all()
    
    # Remove password from response
    for user in users:
        user.password = None
    
    return PaginatedResponse(
        items=users,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )