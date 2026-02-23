from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import LoginSchema, SignUpSchema  # 👈 use existing schemas
from backend.utils.security import verify_password, hash_password

router = APIRouter()


# ==============================
# LOGIN
# ==============================

@router.post("/login")
def login(user: LoginSchema, response: Response, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    if db_user.is_active is False:
        raise HTTPException(status_code=403, detail="User disabled")
    

    # Set cookie session
    response.set_cookie(
        key="user_id",
        value=str(db_user.id),
        httponly=True
    )

    return {
        "message": "Login successful",
        "role": db_user.role
    }


# ==============================
# LOGOUT
# ==============================

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("user_id")
    return {"message": "Logged out successfully"}


# ==============================
# GET CURRENT USER (COOKIE AUTH)
# ==============================

def get_current_user(request: Request, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


# ==============================
# SIGNUP
# ==============================

@router.post("/signup", status_code=201)
def signup(user: SignUpSchema, db: Session = Depends(get_db)):

    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role="user",
        membership_id=1  # default membership
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "role": "user"
    }