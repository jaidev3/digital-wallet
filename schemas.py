from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str
    balance: float

class CreateUser(User):
    pass

class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    balance: Optional[float] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    balance: float
    created_at: datetime
    updated_at: datetime
    


class Transaction(BaseModel):
    user_id: int
    transaction_type: str
    amount: float
    description: Optional[str] = None
    reference_transaction_id: int
    created_at: datetime
    updated_at: datetime

class CreateTransaction(Transaction):
    recipient_user_id: int

class GetAllTransactions(BaseModel):
    user_id: int
    transactions: List[Transaction]