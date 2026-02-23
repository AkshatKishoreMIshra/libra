# create_admin.py
from backend.database import SessionLocal, engine
from backend.models import Base, User
from backend.utils.security import hash_password

def create_admin():
    # 1️⃣ Ensure all tables exist
    Base.metadata.create_all(bind=engine)

    # 2️⃣ Open a new DB session
    db = SessionLocal()

    try:
        # 3️⃣ Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@library.com").first()

        if existing_admin:
            print("Admin already exists.")
            return
        

        # 4️⃣ Create admin user
        admin_user = User(
            name="Admin",
            email="admin@library.com",
            password=hash_password("AdminPassword.@14"),  # Replace with your secure password
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Admin created successfully!")

    except Exception as e:
        print("Error creating admin:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()