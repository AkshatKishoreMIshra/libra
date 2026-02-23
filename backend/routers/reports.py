from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from backend.database import get_db
from backend.models import Transaction, User, Book
from backend.utils.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/active-issues")
def active_issues_report(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    results = (
        db.query(
            Transaction.id,
            User.name.label("user_name"),
            Book.title.label("book_title"),
            Transaction.issue_date,
            Transaction.due_date,
        )
        .join(User, Transaction.user_id == User.id)
        .join(Book, Transaction.book_id == Book.id)
        .filter(Transaction.status == "issued")
        .all()
    )

    return {"active_issues": results}

@router.get("/overdue")
def overdue_report(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    today = date.today()

    results = (
        db.query(
            Transaction.id,
            User.name.label("user_name"),
            Book.title.label("book_title"),
            Transaction.due_date,
        )
        .join(User, Transaction.user_id == User.id)
        .join(Book, Transaction.book_id == Book.id)
        .filter(
            Transaction.status == "issued",
            Transaction.due_date < today
        )
        .all()
    )

    return {"overdue_books": results}

@router.get("/fine-summary")
def fine_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    total = (
        db.query(func.sum(Transaction.fine_amount))
        .filter(Transaction.status == "returned")
        .scalar()
    )

    return {
        "total_fines_collected": total or 0
    }

@router.get("/book-summary")
def book_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    books = db.query(
        Book.title,
        Book.total_copies,
        Book.available_copies
    ).all()

    return {"books": books}

@router.get("/user-activity")
def user_activity(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    activity = (
        db.query(
            User.name,
            func.count(Transaction.id).label("total_issued")
        )
        .outerjoin(Transaction, User.id == Transaction.user_id)
        .group_by(User.id)
        .all()
    )

    return {"user_activity": activity}

