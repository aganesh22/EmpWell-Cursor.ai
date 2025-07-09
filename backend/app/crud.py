from __future__ import annotations

from sqlmodel import Session, select

from backend.app.core.security import get_password_hash, verify_password
from backend.app.models import User


def get_user_by_email(session: Session, *, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, *, email: str, full_name: str | None, password: str) -> User:
    db_user = User(email=email.lower(), full_name=full_name, hashed_password=get_password_hash(password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate_user(session: Session, *, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_status(session: Session, user: User, *, is_active: bool) -> User:
    user.is_active = is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def set_user_password(session: Session, user: User, *, password: str) -> User:
    user.hashed_password = get_password_hash(password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user