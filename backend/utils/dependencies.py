from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User

# ---------------------------------
# Get the current logged-in user
# ---------------------------------
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is disabled")

    return user

# ---------------------------------
# Require admin role
# ---------------------------------
def require_admin(
    user: User = Depends(get_current_user)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user