from __future__ import annotations

from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel

from backend.app.models import Role


class UserCreate(SQLModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    department: Optional[str] = None


class UserRead(SQLModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    department: Optional[str]
    is_active: bool
    role: Role

    class Config:
        orm_mode = True


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class GoogleToken(SQLModel):
    id_token: str


class UserInvite(SQLModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Role = Role.employee

class UserStatusUpdate(SQLModel):
    is_active: bool

class PasswordReset(SQLModel):
    password: str

class QuestionRead(SQLModel):
    id: int
    text: str
    order: int
    min_value: int
    max_value: int

    class Config:
        orm_mode = True

class TestTemplateRead(SQLModel):
    key: str
    name: str
    description: Optional[str]
    questions: list[QuestionRead]

    class Config:
        orm_mode = True

class TestResult(SQLModel):
    raw_score: float
    normalized_score: float
    interpretation: str
    tips: list[str] = []

class ResourceRead(SQLModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    type: str
    tags: Optional[str]

    class Config:
        orm_mode = True