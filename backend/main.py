from fastapi import FastAPI
from backend.routers import auth,books,memberships,transactions,reports,maintenance
from backend.database import engine,Base

Base.metadata.create_all(bind=engine)

app = FastAPI()



app.include_router(auth.router,prefix="/auth")
app.include_router(books.router)
app.include_router(memberships.router)
app.include_router(transactions.router)
app.include_router(reports.router)
app.include_router(maintenance.router)