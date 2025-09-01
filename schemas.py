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
    username: str
    email: str
    phone_number: str
    password: str
    balance: float

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
    description: str
    reference_transaction_id: int
    recipient_user_id: int
    created_at: datetime