from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.schemas import ResourceRead
from backend.app.models import Resource
from backend.app.deps import require_admin

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=list[ResourceRead])
def list_resources(session: Session = Depends(get_session)):
    return session.exec(select(Resource)).all()


@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceRead, admin=Depends(require_admin), session: Session = Depends(get_session)):
    db_res = Resource(**resource.dict(exclude_unset=True))
    session.add(db_res)
    session.commit()
    session.refresh(db_res)
    return db_res