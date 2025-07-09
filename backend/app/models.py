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