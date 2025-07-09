import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.deps import require_admin, get_current_user
from backend.app.database import get_session
from backend.app.schemas import UserRead, UserInvite, UserStatusUpdate, PasswordReset
from backend.app.models import User
from backend.app import crud

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def list_users(admin=Depends(require_admin), session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return users


# Invite user (creates inactive user)


@router.post("/invite", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def invite_user(payload: UserInvite, admin=Depends(require_admin), session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, email=payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    temp_password = secrets.token_urlsafe(10)
    user = crud.create_user(session, email=payload.email, full_name=payload.full_name, password=temp_password)
    user.role = payload.role
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    # TODO: send invitation email with temp_password.
    return user


# Enable/disable user


@router.patch("/{user_id}/status", response_model=UserRead)
def update_status(user_id: int, payload: UserStatusUpdate, admin=Depends(require_admin), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.update_user_status(session, user=user, is_active=payload.is_active)
    return user


# Reset password


@router.post("/{user_id}/reset_password", response_model=UserRead)
def reset_password(user_id: int, payload: PasswordReset, admin=Depends(require_admin), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.set_user_password(session, user=user, password=payload.password)
    return user