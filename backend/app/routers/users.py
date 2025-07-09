from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.app.deps import require_admin
from backend.app.database import get_session
from backend.app.schemas import UserRead
from backend.app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def list_users(admin=Depends(require_admin), session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return users