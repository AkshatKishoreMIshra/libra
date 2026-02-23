from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Membership
from backend.utils.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/memberships", tags=["Memberships"])


# ✅ Create Membership
@router.post("/")
def add_membership(
    name: str,
    duration_days: int,
    max_books_allowed: int,
    fine_per_day: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    membership = Membership(
        name=name,
        duration_days=duration_days,
        max_books_allowed=max_books_allowed,
        fine_per_day=fine_per_day
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return {"message": "Membership created successfully", "id": membership.id}


# ✅ Update Membership
@router.put("/{membership_id}")
def update_membership(
    membership_id: int,
    name: str,
    duration_days: int,
    max_books_allowed: int,
    fine_per_day: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    membership = db.query(Membership).filter(
        Membership.id == membership_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.name = name
    membership.duration_days = duration_days
    membership.max_books_allowed = max_books_allowed
    membership.fine_per_day = fine_per_day

    db.commit()

    return {"message": "Membership updated successfully"}


# ✅ Get All Memberships
@router.get("/")
def get_memberships(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    memberships = db.query(Membership).all()

    return {"memberships": memberships}