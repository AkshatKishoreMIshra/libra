from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models import Book
from backend.schemas import BookCreate, BookResponse
from backend.utils.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


# -----------------------------------------
# 1️⃣ ADD BOOK (Admin Only)
# -----------------------------------------
@router.post("/", response_model=dict)
def add_book(
    book: BookCreate,
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Validate copies
    if book.total_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total copies must be greater than 0"
        )

    try:
        new_book = Book(
            title=book.title.strip(),
            author=book.author.strip(),
            category=book.category.strip(),
            total_copies=book.total_copies,
            available_copies=book.total_copies
        )

        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        return {
            "message": "Book added successfully",
            "book_id": new_book.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add book: {str(e)}"
        )


# -----------------------------------------
# 2️⃣ UPDATE BOOK (Admin Only)
# -----------------------------------------
@router.put("/{book_id}", response_model=dict)
def update_book(
    book_id: int,
    updated_book: BookCreate,
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    db_book: Book | None = db.query(Book).filter(Book.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    difference = updated_book.total_copies - int(db_book.total_copies)
    new_available = int(db_book.available_copies) + difference

    if new_available < 0:
        raise HTTPException(status_code=400, detail="Invalid total copies")

    db_book.title = updated_book.title
    db_book.author = updated_book.author
    db_book.category = updated_book.category
    db_book.total_copies = updated_book.total_copies
    db_book.available_copies = new_available

    db.commit()
    db.refresh(db_book)

    return {"message": "Book updated successfully"}


# -----------------------------------------
# 3️⃣ GET ALL BOOKS
# -----------------------------------------
@router.get("/", response_model=list[BookResponse])
def get_all_books(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    books = db.query(Book).all()
    return books


# -----------------------------------------
# 4️⃣ SEARCH BOOKS
# -----------------------------------------
@router.get("/search", response_model=list[BookResponse])
def search_books(
    query: str = Query(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(Book).filter(
        or_(
            Book.title.ilike(f"%{query}%"),
            Book.author.ilike(f"%{query}%"),
            Book.category.ilike(f"%{query}%")
        )
    ).all()

    return results


# -----------------------------------------
# 5️⃣ CHECK AVAILABILITY
# -----------------------------------------
@router.get("/{book_id}/availability")
def check_availability(
    book_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return {
        "available_copies": book.available_copies,
        "is_available": book.available_copies > 0
    }
