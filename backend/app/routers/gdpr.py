"""
GDPR Compliance Router

Implements GDPR requirements including:
- Article 7: Consent management
- Article 17: Right to erasure (right to be forgotten)
- Article 20: Right to data portability
- Article 30: Records of processing activities
- Article 35: Data protection impact assessment
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.auth import get_current_user
from backend.app.models import (
    User, UserConsent, DataExportRequest, DataProcessingLog, 
    TestAttempt, Response, ConsentType
)
from backend.app.schemas import (
    ConsentCreate, ConsentRead, ConsentUpdate, DataExportRequestCreate,
    DataExportRequestRead, DataExportResponse, PrivacyPolicyAcceptance,
    AnonymizationRequest, GDPRComplianceReport
)

router = APIRouter(prefix="/gdpr", tags=["GDPR Compliance"])

# --- Consent Management (GDPR Article 7) ---

@router.post("/consent", response_model=ConsentRead)
def create_or_update_consent(
    consent: ConsentCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create or update user consent for data processing"""
    
    # Check if consent already exists
    existing_consent = session.exec(
        select(UserConsent).where(
            UserConsent.user_id == current_user.id,
            UserConsent.consent_type == consent.consent_type
        )
    ).first()
    
    if existing_consent:
        # Update existing consent
        if not consent.granted and existing_consent.granted:
            existing_consent.withdrawn_at = datetime.utcnow()
        existing_consent.granted = consent.granted
        existing_consent.ip_address = consent.ip_address or request.client.host
        existing_consent.user_agent = consent.user_agent or request.headers.get("user-agent")
        session.add(existing_consent)
    else:
        # Create new consent
        new_consent = UserConsent(
            user_id=current_user.id,
            consent_type=consent.consent_type,
            granted=consent.granted,
            ip_address=consent.ip_address or request.client.host,
            user_agent=consent.user_agent or request.headers.get("user-agent"),
            withdrawn_at=datetime.utcnow() if not consent.granted else None
        )
        session.add(new_consent)
        existing_consent = new_consent
    
    # Log the consent activity
    log_data_processing(
        session=session,
        user_id=current_user.id,
        activity_type="consent_management",
        purpose="GDPR Article 7 - Consent",
        data_categories=json.dumps([consent.consent_type.value]),
        created_by=current_user.id
    )
    
    session.commit()
    session.refresh(existing_consent)
    return existing_consent

@router.get("/consents", response_model=List[ConsentRead])
def get_user_consents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all consents for the current user"""
    consents = session.exec(
        select(UserConsent).where(UserConsent.user_id == current_user.id)
    ).all()
    return consents

@router.put("/consent/{consent_id}", response_model=ConsentRead)
def update_consent(
    consent_id: int,
    consent_update: ConsentUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a specific consent"""
    consent = session.exec(
        select(UserConsent).where(
            UserConsent.id == consent_id,
            UserConsent.user_id == current_user.id
        )
    ).first()
    
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    # Update consent
    if not consent_update.granted and consent.granted:
        consent.withdrawn_at = datetime.utcnow()
    elif consent_update.granted and not consent.granted:
        consent.withdrawn_at = None
        
    consent.granted = consent_update.granted
    consent.ip_address = consent_update.ip_address or request.client.host
    consent.user_agent = consent_update.user_agent or request.headers.get("user-agent")
    
    session.add(consent)
    session.commit()
    session.refresh(consent)
    return consent

# --- Privacy Policy Acceptance ---

@router.post("/privacy-policy/accept")
def accept_privacy_policy(
    acceptance: PrivacyPolicyAcceptance,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Record privacy policy acceptance"""
    current_user.privacy_policy_version = acceptance.version
    current_user.last_privacy_policy_acceptance = datetime.utcnow()
    
    # Log the activity
    log_data_processing(
        session=session,
        user_id=current_user.id,
        activity_type="privacy_policy_acceptance",
        purpose="GDPR compliance",
        data_categories=json.dumps(["user_preferences"]),
        created_by=current_user.id
    )
    
    session.add(current_user)
    session.commit()
    return {"message": "Privacy policy acceptance recorded"}

# --- Data Export (GDPR Article 20) ---

@router.post("/data-export", response_model=DataExportRequestRead)
def request_data_export(
    export_request: DataExportRequestCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Request data export (Right to data portability)"""
    
    # Check for existing pending requests
    existing_request = session.exec(
        select(DataExportRequest).where(
            DataExportRequest.user_id == current_user.id,
            DataExportRequest.status == "pending"
        )
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=400, 
            detail="You already have a pending data export request"
        )
    
    # Create new export request
    new_request = DataExportRequest(
        user_id=current_user.id,
        request_type=export_request.request_type,
        expires_at=datetime.utcnow() + timedelta(days=30)  # Export expires in 30 days
    )
    
    session.add(new_request)
    session.commit()
    session.refresh(new_request)
    
    # Process export in background
    if export_request.request_type == "export":
        background_tasks.add_task(generate_data_export, new_request.id, session)
    elif export_request.request_type == "deletion":
        background_tasks.add_task(process_deletion_request, new_request.id, session)
    
    return new_request

@router.get("/data-export/{request_id}")
def get_export_status(
    request_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get status of data export request"""
    export_request = session.exec(
        select(DataExportRequest).where(
            DataExportRequest.id == request_id,
            DataExportRequest.user_id == current_user.id
        )
    ).first()
    
    if not export_request:
        raise HTTPException(status_code=404, detail="Export request not found")
    
    return export_request

@router.get("/data-export/{request_id}/download")
def download_export(
    request_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Download completed data export"""
    export_request = session.exec(
        select(DataExportRequest).where(
            DataExportRequest.id == request_id,
            DataExportRequest.user_id == current_user.id,
            DataExportRequest.status == "completed"
        )
    ).first()
    
    if not export_request:
        raise HTTPException(status_code=404, detail="Export not found or not ready")
    
    if export_request.expires_at and export_request.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Export has expired")
    
    if not export_request.file_path or not os.path.exists(export_request.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Log download activity
    log_data_processing(
        session=session,
        user_id=current_user.id,
        activity_type="data_export_download",
        purpose="GDPR Article 20 - Data portability",
        data_categories=json.dumps(["all_user_data"]),
        created_by=current_user.id
    )
    
    return FileResponse(
        export_request.file_path,
        filename=f"user_data_export_{current_user.id}_{export_request.id}.json",
        media_type="application/json"
    )

# --- Right to be Forgotten (GDPR Article 17) ---

@router.post("/forget-me")
def request_account_deletion(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Request account deletion (Right to be forgotten)"""
    
    if current_user.deletion_requested_at:
        raise HTTPException(
            status_code=400, 
            detail="Account deletion has already been requested"
        )
    
    # Mark account for deletion (30-day grace period)
    current_user.deletion_requested_at = datetime.utcnow()
    current_user.deletion_scheduled_for = datetime.utcnow() + timedelta(days=30)
    
    # Log the request
    log_data_processing(
        session=session,
        user_id=current_user.id,
        activity_type="deletion_request",
        purpose="GDPR Article 17 - Right to erasure",
        data_categories=json.dumps(["all_user_data"]),
        created_by=current_user.id
    )
    
    session.add(current_user)
    session.commit()
    
    return {
        "message": "Account deletion requested",
        "deletion_date": current_user.deletion_scheduled_for,
        "grace_period_days": 30
    }

@router.post("/cancel-deletion")
def cancel_account_deletion(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Cancel pending account deletion"""
    
    if not current_user.deletion_requested_at:
        raise HTTPException(status_code=400, detail="No deletion request found")
    
    if current_user.deletion_scheduled_for and current_user.deletion_scheduled_for < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Deletion has already been processed")
    
    # Cancel deletion
    current_user.deletion_requested_at = None
    current_user.deletion_scheduled_for = None
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Account deletion cancelled"}

# --- Admin Functions ---

@router.get("/compliance-report", response_model=GDPRComplianceReport)
def get_compliance_report(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Generate GDPR compliance report (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Gather compliance metrics
    total_users = len(session.exec(select(User)).all())
    users_with_consent = len(session.exec(
        select(User).join(UserConsent).where(UserConsent.granted == True)
    ).all())
    
    pending_deletions = len(session.exec(
        select(User).where(User.deletion_requested_at.is_not(None))
    ).all())
    
    anonymized_records = len(session.exec(
        select(TestAttempt).where(TestAttempt.is_anonymized == True)
    ).all())
    
    recent_exports = session.exec(
        select(DataExportRequest)
        .where(DataExportRequest.requested_at > datetime.utcnow() - timedelta(days=30))
        .order_by(DataExportRequest.requested_at.desc())
        .limit(10)
    ).all()
    
    # Calculate consent withdrawal rate
    total_consents = len(session.exec(select(UserConsent)).all())
    withdrawn_consents = len(session.exec(
        select(UserConsent).where(UserConsent.withdrawn_at.is_not(None))
    ).all())
    
    withdrawal_rate = (withdrawn_consents / total_consents * 100) if total_consents > 0 else 0
    
    return GDPRComplianceReport(
        total_users=total_users,
        users_with_consent=users_with_consent,
        pending_deletion_requests=pending_deletions,
        anonymized_records=anonymized_records,
        data_retention_compliance={
            "assessment_retention_days": 2555,  # 7 years
            "personal_data_retention_days": 1825,  # 5 years
            "marketing_data_retention_days": 730   # 2 years
        },
        recent_exports=recent_exports,
        consent_withdrawal_rate=withdrawal_rate,
        last_updated=datetime.utcnow()
    )

@router.post("/anonymize-user")
def anonymize_user_data(
    anonymization: AnonymizationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Anonymize user data while preserving analytics (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = session.get(User, anonymization.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_anonymized:
        raise HTTPException(status_code=400, detail="User data is already anonymized")
    
    # Generate anonymized identifiers
    user_hash = hashlib.sha256(f"{user.id}_{user.email}_{datetime.utcnow()}".encode()).hexdigest()[:16]
    dept_hash = hashlib.sha256(f"{user.department}_{datetime.utcnow()}".encode()).hexdigest()[:8] if user.department else None
    
    # Anonymize user record
    user.email = f"anonymized_{user_hash}@example.com"
    user.full_name = f"Anonymized User {user_hash[:8]}"
    user.department = f"Dept_{dept_hash}" if dept_hash else None
    user.is_anonymized = True
    user.anonymized_at = datetime.utcnow()
    user.anonymization_method = anonymization.method
    
    # Anonymize assessment data
    if anonymization.preserve_analytics:
        test_attempts = session.exec(
            select(TestAttempt).where(TestAttempt.user_id == user.id)
        ).all()
        
        for attempt in test_attempts:
            attempt.is_anonymized = True
            attempt.anonymized_at = datetime.utcnow()
            attempt.anonymized_user_hash = user_hash
            attempt.department_hash = dept_hash
            session.add(attempt)
    
    # Log anonymization
    log_data_processing(
        session=session,
        user_id=user.id,
        activity_type="data_anonymization",
        purpose="GDPR compliance",
        data_categories=json.dumps(["personal_data", "assessment_data"]),
        created_by=current_user.id
    )
    
    session.add(user)
    session.commit()
    
    return {"message": f"User {anonymization.user_id} data anonymized successfully"}

# --- Helper Functions ---

def log_data_processing(
    session: Session,
    user_id: int,
    activity_type: str,
    purpose: str,
    data_categories: str,
    created_by: int,
    recipients: str = None,
    retention_period: str = None
):
    """Log data processing activity for GDPR Article 30 compliance"""
    log_entry = DataProcessingLog(
        user_id=user_id,
        activity_type=activity_type,
        purpose=purpose,
        data_categories=data_categories,
        recipients=recipients,
        retention_period=retention_period,
        security_measures="TLS encryption, access controls, audit logging",
        created_by=created_by
    )
    session.add(log_entry)

def generate_data_export(request_id: int, session: Session):
    """Generate complete user data export"""
    export_request = session.get(DataExportRequest, request_id)
    if not export_request:
        return
    
    try:
        export_request.status = "processing"
        session.add(export_request)
        session.commit()
        
        user = session.get(User, export_request.user_id)
        if not user:
            export_request.status = "failed"
            export_request.notes = "User not found"
            session.add(export_request)
            session.commit()
            return
        
        # Gather all user data
        export_data = {
            "user_info": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "department": user.department,
                "created_at": user.created_at.isoformat(),
                "role": user.role,
                "privacy_policy_version": user.privacy_policy_version,
                "last_privacy_policy_acceptance": user.last_privacy_policy_acceptance.isoformat() if user.last_privacy_policy_acceptance else None
            },
            "assessments": [],
            "consents": [],
            "processing_logs": [],
            "export_metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "request_id": request_id
            }
        }
        
        # Get assessments
        assessments = session.exec(
            select(TestAttempt).where(TestAttempt.user_id == user.id)
        ).all()
        
        for assessment in assessments:
            assessment_data = {
                "id": assessment.id,
                "template_id": assessment.template_id,
                "created_at": assessment.created_at.isoformat(),
                "raw_score": assessment.raw_score,
                "normalized_score": assessment.normalized_score,
                "interpretation": assessment.interpretation,
                "responses": []
            }
            
            responses = session.exec(
                select(Response).where(Response.attempt_id == assessment.id)
            ).all()
            
            for response in responses:
                assessment_data["responses"].append({
                    "question_id": response.question_id,
                    "value": response.value
                })
            
            export_data["assessments"].append(assessment_data)
        
        # Get consents
        consents = session.exec(
            select(UserConsent).where(UserConsent.user_id == user.id)
        ).all()
        
        for consent in consents:
            export_data["consents"].append({
                "consent_type": consent.consent_type,
                "granted": consent.granted,
                "granted_at": consent.granted_at.isoformat(),
                "withdrawn_at": consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
                "version": consent.version
            })
        
        # Get processing logs
        logs = session.exec(
            select(DataProcessingLog).where(DataProcessingLog.user_id == user.id)
        ).all()
        
        for log in logs:
            export_data["processing_logs"].append({
                "activity_type": log.activity_type,
                "purpose": log.purpose,
                "data_categories": log.data_categories,
                "created_at": log.created_at.isoformat()
            })
        
        # Save export file
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, f"user_export_{request_id}.json")
        
        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        # Update request
        export_request.status = "completed"
        export_request.completed_at = datetime.utcnow()
        export_request.file_path = file_path
        export_request.file_size_bytes = os.path.getsize(file_path)
        
        session.add(export_request)
        session.commit()
        
    except Exception as e:
        export_request.status = "failed"
        export_request.notes = str(e)
        session.add(export_request)
        session.commit()

def process_deletion_request(request_id: int, session: Session):
    """Process account deletion request"""
    export_request = session.get(DataExportRequest, request_id)
    if not export_request or export_request.request_type != "deletion":
        return
    
    try:
        export_request.status = "processing"
        session.add(export_request)
        session.commit()
        
        user = session.get(User, export_request.user_id)
        if not user:
            export_request.status = "failed"
            export_request.notes = "User not found"
            session.add(export_request)
            session.commit()
            return
        
        # Delete user data (can be implemented as soft delete or hard delete based on requirements)
        # For now, we'll anonymize instead of hard delete to maintain referential integrity
        
        user_hash = hashlib.sha256(f"deleted_{user.id}_{datetime.utcnow()}".encode()).hexdigest()[:16]
        
        user.email = f"deleted_{user_hash}@example.com"
        user.full_name = "Deleted User"
        user.department = None
        user.is_anonymized = True
        user.anonymized_at = datetime.utcnow()
        user.anonymization_method = "deletion_request"
        
        # Mark assessment data as anonymized
        test_attempts = session.exec(
            select(TestAttempt).where(TestAttempt.user_id == user.id)
        ).all()
        
        for attempt in test_attempts:
            attempt.is_anonymized = True
            attempt.anonymized_at = datetime.utcnow()
            attempt.anonymized_user_hash = user_hash
            session.add(attempt)
        
        export_request.status = "completed"
        export_request.completed_at = datetime.utcnow()
        export_request.notes = "Account anonymized as per deletion request"
        
        session.add(user)
        session.add(export_request)
        session.commit()
        
    except Exception as e:
        export_request.status = "failed"
        export_request.notes = str(e)
        session.add(export_request)
        session.commit()