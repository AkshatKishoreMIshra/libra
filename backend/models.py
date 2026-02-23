from sqlalchemy import (
    Column, Integer, String, Boolean, Text,
    ForeignKey, DateTime, CheckConstraint,Date
)
from sqlalchemy.orm import relationship,Mapped, mapped_column
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime,date
from typing import Optional


# ========================
# MEMBERSHIPS
# ========================
class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    duration_days: Mapped[int]
    max_books_allowed: Mapped[int]
    fine_per_day: Mapped[int]

    users = relationship("User", back_populates="membership")


# ========================
# USERS
# ========================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(20), nullable=False)

    membership_id: Mapped[int | None] = mapped_column(
        ForeignKey("memberships.id", ondelete="SET NULL"),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("role IN ('admin','user')", name="role_check"),
    )

    membership = relationship("Membership", back_populates="users")
    issue_requests = relationship("IssueRequest", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="performed_user")


# ========================
# BOOKS
# ========================
class Book(Base):
    __tablename__ = "books"

    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(150))
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer)
    available_copies: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="total_copies_check"),
        CheckConstraint("available_copies >= 0", name="available_copies_check"),
    )

    issue_requests = relationship("IssueRequest", back_populates="book")
    transactions = relationship("Transaction", back_populates="book")


# ========================
# ISSUE REQUESTS
# ========================
class IssueRequest(Base):
    __tablename__ = "issue_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )

    request_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="issue_request_status_check"
        ),
    )

    user = relationship("User", back_populates="issue_requests")
    book = relationship("Book", back_populates="issue_requests")


# ========================
# TRANSACTIONS
# ========================
from datetime import datetime, date
from sqlalchemy import Date, DateTime, String, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Proper Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )

    # Dates
    issue_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    return_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Money (Correct Type)
    fine_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="issued",
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('issued','returned')",
            name="transaction_status_check"
        ),
    )

    # Relationships
    user = relationship("User", back_populates="transactions")
    book = relationship("Book", back_populates="transactions")
    fines = relationship("Fine", back_populates="transaction", cascade="all, delete")


# ========================
# FINES
# ========================
class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE")
    )
    amount = Column(Integer, nullable=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    transaction = relationship("Transaction", back_populates="fines")


# ========================
# AUDIT LOGS
# ========================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Text, nullable=False)
    performed_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL")
    )
    timestamp = Column(DateTime(timezone=True),
                       server_default=func.now())

    performed_user = relationship("User", back_populates="audit_logs")