from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel
from enum import Enum

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


class AzureToken(SQLModel):
    access_token: str


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

class ConsentTypeEnum(str, Enum):
    DATA_PROCESSING = "data_processing"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    RESEARCH = "research"

class ConsentCreate(BaseModel):
    consent_type: ConsentTypeEnum
    granted: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class ConsentRead(BaseModel):
    id: int
    consent_type: ConsentTypeEnum
    granted: bool
    granted_at: datetime
    withdrawn_at: Optional[datetime] = None
    version: str

class ConsentUpdate(BaseModel):
    granted: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class DataExportRequestCreate(BaseModel):
    request_type: str = "export"  # "export", "deletion", "rectification"

class DataExportRequestRead(BaseModel):
    id: int
    request_type: str
    status: str
    requested_at: datetime
    completed_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

class DataExportResponse(BaseModel):
    """Complete user data export for GDPR compliance"""
    user_info: Dict[str, Any]
    assessments: List[Dict[str, Any]]
    consents: List[Dict[str, Any]]
    processing_logs: List[Dict[str, Any]]
    export_metadata: Dict[str, Any]

class PrivacyPolicyAcceptance(BaseModel):
    version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AnonymizationRequest(BaseModel):
    user_id: int
    method: str = "hash_based"  # "hash_based", "k_anonymity", "differential_privacy"
    preserve_analytics: bool = True

class GDPRComplianceReport(BaseModel):
    """GDPR compliance status report"""
    total_users: int
    users_with_consent: int
    pending_deletion_requests: int
    anonymized_records: int
    data_retention_compliance: Dict[str, Any]
    recent_exports: List[DataExportRequestRead]
    consent_withdrawal_rate: float
    last_updated: datetime