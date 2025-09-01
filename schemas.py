from typing import List, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel

T = TypeVar('T')

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
    reference_transaction_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CreateTransaction(Transaction):
    recipient_user_id: int

class GetAllTransactions(BaseModel):
    user_id: int
    transactions: List[Transaction]

# Pagination models
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10
    
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool