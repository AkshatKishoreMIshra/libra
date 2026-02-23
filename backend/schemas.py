from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ==============================
# MEMBERSHIP SCHEMAS
# ==============================

class MembershipBase(BaseModel):
    name: str
    duration_days: int
    max_books_allowed: int
    fine_per_day: int


class MembershipCreate(MembershipBase):
    pass


class MembershipResponse(MembershipBase):
    id: int

    class Config:
        from_attributes = True


# ==============================
# USER SCHEMAS
# ==============================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str
    membership_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    membership_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================
# BOOK SCHEMAS
# ==============================

class BookBase(BaseModel):
    title: str
    author: str
    category: Optional[str] = None
    total_copies: int
    available_copies: int


# schemas/book.py

class BookCreate(BaseModel):
    title: str
    author: str
    category: str
    total_copies: int


class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================
# ISSUE REQUEST SCHEMAS
# ==============================

class IssueRequestBase(BaseModel):
    user_id: int
    book_id: int


class IssueRequestCreate(IssueRequestBase):
    pass


class IssueRequestResponse(IssueRequestBase):
    id: int
    request_date: datetime
    status: str

    class Config:
        from_attributes = True


# ==============================
# TRANSACTION SCHEMAS
# ==============================

class TransactionBase(BaseModel):
    user_id: int
    book_id: int


class TransactionCreate(TransactionBase):
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class TransactionResponse(TransactionBase):
    id: int
    issue_date: Optional[datetime]
    due_date: Optional[datetime]
    return_date: Optional[datetime]
    fine_amount: int
    status: str

    class Config:
        from_attributes = True


# ==============================
# FINE SCHEMAS
# ==============================

class FineBase(BaseModel):
    transaction_id: int
    amount: int


class FineCreate(FineBase):
    pass


class FineResponse(FineBase):
    id: int
    paid: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================
# AUDIT LOG SCHEMAS
# ==============================

class AuditLogBase(BaseModel):
    action: str
    performed_by: Optional[int] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class SignUpSchema(BaseModel):
    name: str
    email: EmailStr
    password: str