from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class Role(str, enum.Enum):
    employee = "employee"
    admin = "admin"


class UserBase(SQLModel):
    email: str = Field(index=True, nullable=False, unique=True, sa_column_kwargs={"unique": True})
    full_name: Optional[str] = None
    is_active: bool = True
    role: Role = Field(default=Role.employee, nullable=False)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# --- Token management (optional for future blacklisting / refresh) ---
class RevokedToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(index=True, unique=True)
    revoked_at: datetime = Field(default_factory=datetime.utcnow)


# --- Test Engine models ---

class TestTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None

    questions: list["Question"] = Relationship(back_populates="template")


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="testtemplate.id")
    text: str
    order: int
    min_value: int = 0
    max_value: int = 5
    weight: float = 1.0
    dimension_pair: str | None = Field(default=None, max_length=2)  # e.g., "IE", "SN", "D" etc.
    positive_letter: str | None = Field(default=None, max_length=1)

    template: TestTemplate = Relationship(back_populates="questions")


class TestAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="testtemplate.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw_score: Optional[float] = None
    normalized_score: Optional[float] = None

    responses: list["Response"] = Relationship(back_populates="attempt")


class Response(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="testattempt.id")
    question_id: int = Field(foreign_key="question.id")
    value: int

    attempt: TestAttempt = Relationship(back_populates="responses")