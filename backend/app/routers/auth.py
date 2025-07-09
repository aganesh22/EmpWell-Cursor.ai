from __future__ import annotations

import os
import secrets
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from backend.app import crud, schemas
from backend.app.core.security import create_access_token
from backend.app.deps import get_current_user
from backend.app.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session, email=user_in.email, full_name=user_in.full_name, password=user_in.password)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = crud.authenticate_user(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.id)
    return schemas.Token(access_token=token)


# --- Google Workspace SSO ---

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/google", response_model=schemas.Token)
def google_sso(payload: schemas.GoogleToken, session: Session = Depends(get_session)):
    """Accept an `id_token` from Google Identity Services and exchange for platform JWT."""

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google SSO not configured")

    try:
        idinfo = google_id_token.verify_oauth2_token(payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as exc:  # catch verify errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google token") from exc

    email = idinfo.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token missing email")

    user = crud.get_user_by_email(session, email=email)
    if not user:
        # Auto-provision user with random password (not used).
        random_pw = secrets.token_urlsafe(16)
        user = crud.create_user(session, email=email, full_name=idinfo.get("name"), password=random_pw)

    token = create_access_token(user.id)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user=Depends(get_current_user)):
    return current_user