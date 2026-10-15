from fastapi import FastAPI

from app import models  # noqa: F401  (registra las tablas en Base)
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}