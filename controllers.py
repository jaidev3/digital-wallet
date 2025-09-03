from fastapi import Depends, HTTPException
from models import Transaction, User
from schemas import CreateUser, UserResponse, UpdateUser, Transaction, GetAllTransactions
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return user

async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    user.password = None
    return user

async def get_users(db: AsyncSession = Depends(get_db), limit: int = 10, offset: int = 0):
    users = await db.execute(select(User).order_by(User.id).offset(offset).limit(limit))
    users = users.scalars().all()
    return users

async def update_user(user_id: int, user_update: UpdateUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)

    await db.commit()
    await db.refresh(db_user)
    return db_user

#  get wallet balance of user
async def get_wallet_balance(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.balance

#  add wallet balance of user
async def add_wallet_balance(user_id: int, amount: float, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
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
    await db.commit()
    db.refresh(user)
    return user

#  withdraw wallet balance of user
async def withdraw_wallet_balance(user_id: int, amount: float, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    print("user2", user)
    print("user3", user.balance)
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
    await db.commit()
    db.refresh(user)
    return user


# money transfer to another user
async def money_transfer(user_id: int, recipient_user_id: int, amount: float, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    recipient_user = await db.execute(select(User).filter(User.id == recipient_user_id))
    recipient_user = recipient_user.scalar_one_or_none()
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
    await db.commit()
    db.refresh(user)
    db.refresh(recipient_user)
    return user


# get all transactions of user
async def get_all_transactions(user_id: int, db: AsyncSession = Depends(get_db)):
    transactions = await db.execute(select(Transaction).where(Transaction.user_id == user_id))
    transactions = transactions.scalars().all()
    print("transactions", transactions)
    return transactions