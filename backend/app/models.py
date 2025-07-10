from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship


class Role(str, enum.Enum):
    employee = "employee"
    admin = "admin"


class UserBase(SQLModel):
    email: str = Field(index=True, nullable=False, unique=True, sa_column_kwargs={"unique": True})
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    role: Role = Field(default=Role.employee, nullable=False)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # GDPR-related fields
    data_processing_consent: bool = True
    analytics_consent: bool = False
    marketing_consent: bool = False
    consent_date: Optional[datetime] = None
    privacy_policy_version: str = "1.0"
    last_privacy_policy_acceptance: Optional[datetime] = None
    data_retention_override: Optional[int] = None  # Custom retention period in days

    # Anonymization tracking
    is_anonymized: bool = False
    anonymized_at: Optional[datetime] = None
    anonymization_method: Optional[str] = None

    # Account deletion
    deletion_requested_at: Optional[datetime] = None
    deletion_scheduled_for: Optional[datetime] = None

    # Relationships
    # Use built-in `list[...]` generics instead of `typing.List[...]` so SQLAlchemy receives
    # the plain model class (UserConsent / DataProcessingLog / DataExportRequest) rather than
    # the unreduced generic string "List[Model]", which triggers a mapper error in SQLAlchemy ≥2.
    consents: list["UserConsent"] = Relationship(back_populates="user")
    processing_logs: list["DataProcessingLog"] = Relationship(back_populates="user")
    export_requests: list["DataExportRequest"] = Relationship(back_populates="user")


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
    show_if_question_id: Optional[int] = Field(default=None, foreign_key="question.id")
    show_if_value: Optional[int] = None

    template: TestTemplate = Relationship(back_populates="questions")


class TestAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="testtemplate.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw_score: Optional[float] = None
    normalized_score: Optional[float] = None
    interpretation: Optional[str] = None

    # GDPR compliance fields
    is_anonymized: bool = False
    anonymized_at: Optional[datetime] = None
    retention_expires_at: Optional[datetime] = None
    legal_basis: str = "legitimate_interest"  # GDPR legal basis
    consent_id: Optional[int] = Field(default=None, foreign_key="userconsent.id")
    
    # For anonymized data
    anonymized_user_hash: Optional[str] = None  # Hash for linking anonymized records
    department_hash: Optional[str] = None  # Anonymized department identifier

    responses: list["Response"] = Relationship(back_populates="attempt")


class Response(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="testattempt.id")
    question_id: int = Field(foreign_key="question.id")
    value: int

    attempt: TestAttempt = Relationship(back_populates="responses")


class ResourceType(str, enum.Enum):
    article = "article"
    video = "video"
    course = "course"


class Resource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    url: str
    type: ResourceType = Field(default=ResourceType.article)
    tags: Optional[str] = None  # comma separated
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsentType(str, Enum):
    DATA_PROCESSING = "data_processing"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    RESEARCH = "research"

class UserConsent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    consent_type: ConsentType
    granted: bool = True
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    withdrawn_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    version: str = "1.0"  # Consent version for tracking changes

    # Relationships
    user: Optional["User"] = Relationship(back_populates="consents")

class DataProcessingLog(SQLModel, table=True):
    """Audit trail for data processing activities (GDPR Article 30)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.id")
    activity_type: str  # "assessment", "report_generation", "data_export", etc.
    purpose: str  # Legal basis for processing
    data_categories: str  # JSON string of data categories processed
    recipients: Optional[str] = None  # Who received the data
    retention_period: Optional[str] = None
    security_measures: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(foreign_key="user.id")

    # Relationships
    user: Optional["User"] = Relationship(back_populates="processing_logs")

class DataRetentionPolicy(SQLModel, table=True):
    """Define data retention policies for different data types"""
    id: Optional[int] = Field(default=None, primary_key=True)
    data_type: str  # "assessment_results", "personal_data", "analytics", etc.
    retention_period_days: int
    purpose: str
    legal_basis: str
    auto_delete: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class DataExportRequest(SQLModel, table=True):
    """Track data export requests (GDPR Article 20 - Right to data portability)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    request_type: str  # "export", "deletion", "rectification"
    status: str = "pending"  # "pending", "processing", "completed", "rejected"
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    expires_at: Optional[datetime] = None  # When the export link expires
    notes: Optional[str] = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="export_requests")


