from fastapi import Depends
from schemas import Transaction, CreateUser, UserResponse, UpdateUser
from database import get_db
from sqlalchemy.orm import Session

async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    print("user", user)
    print("user.model_dump()", user.model_dump())
    db.add(**user.model_dump())
    db.commit()
    db.refresh(user)
    return user

async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserResponse).filter(UserResponse.id == user_id).first()

async def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    db.query(UserResponse).filter(UserResponse.id == user_id).update(user.model_dump())
    db.refresh(UserResponse)
    db.commit()
    return user

async def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    db.add(**transaction.model_dump())
    db.commit()
    db.refresh(Transaction)
    return transaction