from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Application, User
from app.schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatus,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

REQUIRED_FIELDS = {"company", "position", "status"}


def get_owned_application(db: Session, user: User, application_id: int) -> Application:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.owner_id == user.id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, db: DbSession, user: CurrentUser):
    application = Application(**data.model_dump(), owner_id=user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    db: DbSession,
    user: CurrentUser,
    status: ApplicationStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    stmt = select(Application).where(Application.owner_id == user.id)
    if status:
        stmt = stmt.where(Application.status == status)
    stmt = stmt.order_by(Application.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/{application_id}", response_model=ApplicationRead)
def read_application(application_id: int, db: DbSession, user: CurrentUser):
    return get_owned_application(db, user, application_id)


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int, data: ApplicationUpdate, db: DbSession, user: CurrentUser
):
    application = get_owned_application(db, user, application_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field in REQUIRED_FIELDS:
            continue
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: DbSession, user: CurrentUser):
    application = get_owned_application(db, user, application_id)
    db.delete(application)
    db.commit()