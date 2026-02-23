from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend.models import Transaction, Book, User
from backend.utils.dependencies import require_admin

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ✅ 1. Mark Overdue Transactions
@router.post("/mark-overdue")
def mark_overdue(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    today = date.today()
    updated = 0

    transactions = (
        db.query(Transaction)
        .filter(Transaction.status == "issued")
        .all()
    )

    for txn in transactions:
        if txn.due_date < today:
            txn.status = "overdue"
            updated += 1

    db.commit()

    return {"overdue_marked": updated}


# ✅ 2. Recalculate Fines
@router.post("/recalculate-fines")
def recalculate_fines(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    today = date.today()
    total_updated = 0

    transactions = (
        db.query(Transaction)
        .filter(Transaction.status == "overdue")
        .all()
    )

    for txn in transactions:
        overdue_days = (today - txn.due_date).days
        txn.fine_amount = overdue_days * 10  # ₹10 per day
        total_updated += 1

    db.commit()

    return {"fines_updated": total_updated}


# ✅ 3. Fix Negative Book Copies
@router.post("/fix-book-copies")
def fix_book_copies(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    books = (
        db.query(Book)
        .filter(Book.available_copies < 0)
        .all()
    )

    affected = len(books)

    for book in books:
        book.available_copies = 0

    db.commit()

    return {"fixed_books": affected}


# ✅ 4. System Status
@router.get("/system-status")
def system_status(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    issued_books = db.query(Transaction).filter(Transaction.status == "issued").count()
    overdue_books = db.query(Transaction).filter(Transaction.status == "overdue").count()

    return {
        "total_users": total_users,
        "total_books": total_books,
        "issued_books": issued_books,
        "overdue_books": overdue_books,
    }