from __future__ import annotations

import os
import secrets
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from backend.app import crud, schemas
from backend.app.core.security import create_access_token
from backend.app.core.sso import create_sso_user_service, create_azure_sso_service, SSOError
from backend.app.deps import get_current_user
from backend.app.database import get_session

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session, email=user_in.email, full_name=user_in.full_name, password=user_in.password, department=user_in.department)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = crud.authenticate_user(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.id)
    return schemas.Token(access_token=token)


# --- Enhanced SSO Endpoints ---

@router.post("/sso/google", response_model=schemas.Token)
def google_sso_login(
    payload: schemas.GoogleToken, 
    session: Session = Depends(get_session)
):
    """
    Authenticate with Google Workspace using ID token.
    Supports auto-provisioning and role mapping.
    """
    try:
        sso_service = create_sso_user_service(session)
        user, access_token = sso_service.authenticate_google_user(payload.id_token)
        
        logger.info(f"Successful Google SSO login for user: {user.email}")
        return schemas.Token(access_token=access_token)
        
    except SSOError as e:
        logger.warning(f"Google SSO failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in Google SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.post("/sso/azure", response_model=schemas.Token)
def azure_sso_login(
    payload: schemas.AzureToken,
    session: Session = Depends(get_session)
):
    """
    Authenticate with Azure AD using access token.
    Supports auto-provisioning and role mapping.
    """
    try:
        sso_service = create_sso_user_service(session)
        user, access_token = sso_service.authenticate_azure_user(payload.access_token)
        
        logger.info(f"Successful Azure SSO login for user: {user.email}")
        return schemas.Token(access_token=access_token)
        
    except SSOError as e:
        logger.warning(f"Azure SSO failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in Azure SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.get("/sso/azure/login-url")
def get_azure_login_url(redirect_uri: str = None):
    """
    Get Azure AD authorization URL for OAuth flow.
    
    Args:
        redirect_uri: Optional redirect URI for the OAuth flow
    """
    try:
        azure_service = create_azure_sso_service()
        state = secrets.token_urlsafe(32)
        
        # Store state in session or cache for validation
        # For now, we'll return it for the client to track
        auth_url = azure_service.get_authorization_url(state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": redirect_uri
        }
        
    except SSOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {e}"
        )


@router.post("/sso/azure/callback")
def azure_oauth_callback(
    code: str,
    state: str,
    redirect_uri: str,
    session: Session = Depends(get_session)
):
    """
    Handle Azure AD OAuth callback and exchange code for token.
    
    Args:
        code: Authorization code from Azure AD
        state: State parameter for CSRF protection
        redirect_uri: Redirect URI used in authorization request
    """
    try:
        azure_service = create_azure_sso_service()
        
        # Exchange code for token
        token_result = azure_service.exchange_code_for_token(code, redirect_uri)
        access_token = token_result.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Authenticate user with token
        sso_service = create_sso_user_service(session)
        user, jwt_token = sso_service.authenticate_azure_user(access_token)
        
        logger.info(f"Successful Azure OAuth callback for user: {user.email}")
        return schemas.Token(access_token=jwt_token)
        
    except SSOError as e:
        logger.warning(f"Azure OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in Azure OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.post("/sso/sync-profile")
def sync_sso_profile(
    provider: str,
    access_token: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Sync user profile from SSO provider.
    
    Args:
        provider: SSO provider ('google' or 'azure')
        access_token: Valid access token for the provider
    """
    if provider not in ["google", "azure"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider. Must be 'google' or 'azure'"
        )
    
    try:
        sso_service = create_sso_user_service(session)
        updated_user = sso_service.sync_user_profile(
            current_user.id, 
            provider, 
            access_token
        )
        
        logger.info(f"Profile synced for user {updated_user.email} from {provider}")
        return {
            "message": "Profile synchronized successfully",
            "user": {
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "department": updated_user.department,
                "role": updated_user.role
            }
        }
        
    except SSOError as e:
        logger.warning(f"Profile sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error syncing profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile sync service unavailable"
        )


# --- Legacy SSO Endpoints (for backward compatibility) ---

@router.post("/google", response_model=schemas.Token)
def google_sso_legacy(payload: schemas.GoogleToken, session: Session = Depends(get_session)):
    """Legacy Google SSO endpoint - redirects to new endpoint"""
    return google_sso_login(payload, session)


@router.post("/azure", response_model=schemas.Token)
def azure_sso_legacy(payload: schemas.AzureToken, session: Session = Depends(get_session)):
    """Legacy Azure SSO endpoint - redirects to new endpoint"""
    return azure_sso_login(payload, session)


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user=Depends(get_current_user)):
    return current_user