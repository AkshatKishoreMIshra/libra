from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date

from backend.database import get_db
from backend.models import Transaction, Book, User, Membership, IssueRequest
from backend.utils.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# -----------------------------
# 1️⃣ Issue Book (Admin Only)
# -----------------------------
@router.post("/issue")
def issue_book(
    user_id: int = Query(...),
    book_id: int = Query(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    # 1️⃣ Fetch book
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")

    # 2️⃣ Fetch user along with membership
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.membership:
        raise HTTPException(status_code=400, detail="User has no membership")

    membership = user.membership  # Safe to access now

    # 3️⃣ Check active issued books
    active_count = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.user_id == user.id, Transaction.status == "issued")
        .scalar()
    )

    if active_count >= membership.max_books_allowed:
        raise HTTPException(status_code=400, detail="User reached max book limit")

    # 4️⃣ Create transaction
    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=membership.duration_days)

    transaction = Transaction(
        user_id=user.id,
        book_id=book.id,
        issue_date=issue_date,
        due_date=due_date,
        status="issued"
    )

    db.add(transaction)

    # 5️⃣ Update book availability
    book.available_copies -= 1

    db.commit()

    return {"message": "Book issued successfully"}


# -----------------------------
@router.post("/return/{transaction_id}")
def return_book(
    transaction_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # 1️⃣ Fetch the transaction
    transaction: Transaction | None = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status != "issued":
        raise HTTPException(status_code=400, detail="Book already returned or overdue")

    # 2️⃣ Fetch the book
    book: Book | None = db.query(Book).filter(Book.id == transaction.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 3️⃣ Fetch user's membership safely
    user_obj: User | None = db.query(User).filter(User.id == transaction.user_id).first()
    if not user_obj or not user_obj.membership_id:
        raise HTTPException(status_code=400, detail="User has no membership assigned")

    membership: Membership | None = db.query(Membership).filter(
        Membership.id == user_obj.membership_id
    ).first()
    if not membership:
        raise HTTPException(status_code=400, detail="Membership not found")

    # 4️⃣ Calculate fine safely
    return_date = datetime.now()
    fine = 0
    days_late = 0

    if transaction.due_date and return_date.date() > transaction.due_date:
        days_late = (return_date.date() - transaction.due_date).days
        fine_per_day = membership.fine_per_day or 0
        fine = days_late * fine_per_day

    # 5️⃣ Update transaction
    transaction.return_date = return_date
    transaction.fine_amount = fine
    transaction.status = "returned"

    # 6️⃣ Update book availability
    book.available_copies += 1

    # 7️⃣ Commit changes
    db.commit()
    db.refresh(transaction)
    db.refresh(book)

    return {
        "message": "Book returned successfully",
        "fine": fine,
        "days_late": days_late,
        "book_title": book.title
    }


# -----------------------------
# 3️⃣ My Active Books (User)
# -----------------------------
@router.get("/my-books")
def my_books(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    results = (
        db.query(
            Transaction.id,
            Book.title.label("title"),
            Transaction.issue_date,
            Transaction.due_date
        )
        .join(Book, Transaction.book_id == Book.id)
        .filter(
            Transaction.user_id == user.id,
            Transaction.status == "issued"
        )
        .all()
    )

    return {
        "my_books": [
            dict(row._mapping)
            for row in results
        ]
    }


# -----------------------------
# 4️⃣ All Transactions (Admin)
# -----------------------------
@router.get("/")
def all_transactions(
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
            Transaction.return_date,
            Transaction.status
        )
        .join(User, Transaction.user_id == User.id)
        .join(Book, Transaction.book_id == Book.id)
        .all()
    )

    return {"transactions": results}


# --------------------------
# User: Request a Book
# --------------------------
@router.post("/request/{book_id}")
def request_book(
    book_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")

    request = IssueRequest(
        user_id=user.id,
        book_id=book_id,
        status="pending"
    )

    db.add(request)
    db.commit()

    return {"message": "Book request submitted successfully"}


# --------------------------
# Admin: View All Pending Requests
# --------------------------
@router.get("/requests")
def get_requests(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    results = (
        db.query(
            IssueRequest.id,
            User.name.label("user_name"),
            User.email.label("user_email"),
            Book.title.label("book_title"),
            IssueRequest.request_date,
            IssueRequest.status
        )
        .join(User, IssueRequest.user_id == User.id)
        .join(Book, IssueRequest.book_id == Book.id)
        .filter(IssueRequest.status == "pending")
        .all()
    )

    requests_list = [
        {
            "id": r.id,
            "user_name": r.user_name,
            "user_email": r.user_email,
            "book_title": r.book_title,
            "request_date": r.request_date,
            "status": r.status
        }
        for r in results
    ]

    return {"requests": requests_list}


# --------------------------
# Admin: Approve a Request
# --------------------------
@router.post("/approve/{request_id}")
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    request = db.query(IssueRequest).filter(
        IssueRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    # Reuse issue logic
    return issue_book(
        user_id=request.user_id,
        book_id=request.book_id,
        db=db,
        admin=admin
    )


# --------------------------
# Admin: Reject a Request
# --------------------------
@router.post("/reject/{request_id}")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    request = db.query(IssueRequest).filter(
        IssueRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = "rejected"
    db.commit()

    return {"message": "Request rejected successfully"}