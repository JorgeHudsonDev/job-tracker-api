from fastapi import FastAPI

from app import models  # noqa: F401  (registra las tablas en Base)
from app.database import Base, engine
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Tracker API")
app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}