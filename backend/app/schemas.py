from __future__ import annotations

from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel

from backend.app.models import Role


class UserCreate(SQLModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str


class UserRead(SQLModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    role: Role

    class Config:
        orm_mode = True


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class GoogleToken(SQLModel):
    id_token: str