"""
Single Sign-On (SSO) integration service for Azure AD and Google Workspace.

This module provides comprehensive SSO functionality including:
1. Azure AD (Microsoft Entra ID) integration
2. Google Workspace integration
3. User provisioning and profile synchronization
4. Group/role mapping
5. Session management
6. Error handling and logging
"""

import os
import secrets
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import httpx
import json

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from google.auth.exceptions import GoogleAuthError
import msal
from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.app.models import User, Role
from backend.app.core.security import create_access_token
from backend.app import crud

# Configure logging
logger = logging.getLogger(__name__)

# SSO Configuration
class SSOConfig:
    """SSO Configuration management"""
    
    # Google Workspace Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DOMAIN_RESTRICTION = os.getenv("GOOGLE_DOMAIN_RESTRICTION")  # Optional: restrict to specific domain
    
    # Azure AD Configuration
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET") 
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_AUTHORITY = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID', 'common')}"
    AZURE_SCOPE = ["https://graph.microsoft.com/User.Read", "https://graph.microsoft.com/Directory.Read.All"]
    
    # Role mapping configuration
    AZURE_ROLE_MAPPING = {
        "Global Administrator": Role.admin,
        "User Administrator": Role.admin,
        "HR Manager": Role.admin,
        "Employee": Role.employee
    }
    
    GOOGLE_ROLE_MAPPING = {
        "admin": Role.admin,
        "manager": Role.admin,
        "employee": Role.employee
    }
    
    # Auto-provisioning settings
    AUTO_PROVISION_USERS = os.getenv("AUTO_PROVISION_USERS", "true").lower() == "true"
    DEFAULT_ROLE = Role.employee


class SSOError(Exception):
    """Base exception for SSO-related errors"""
    pass


class SSOValidationError(SSOError):
    """Exception for token validation errors"""
    pass


class SSOProvisioningError(SSOError):
    """Exception for user provisioning errors"""
    pass


class GoogleSSOService:
    """Google Workspace SSO integration service"""
    
    def __init__(self):
        self.client_id = SSOConfig.GOOGLE_CLIENT_ID
        self.client_secret = SSOConfig.GOOGLE_CLIENT_SECRET
        self.domain_restriction = SSOConfig.GOOGLE_DOMAIN_RESTRICTION
        
    def validate_token(self, id_token: str) -> Dict[str, Any]:
        """
        Validate Google ID token and extract user information.
        
        Args:
            id_token: Google ID token from client
            
        Returns:
            Dictionary containing user information
            
        Raises:
            SSOValidationError: If token validation fails
        """
        if not self.client_id:
            raise SSOValidationError("Google SSO not configured - missing GOOGLE_CLIENT_ID")
        
        try:
            # Verify the ID token
            idinfo = google_id_token.verify_oauth2_token(
                id_token, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Validate issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise SSOValidationError("Invalid token issuer")
            
            # Check domain restriction if configured
            email = idinfo.get('email')
            if self.domain_restriction and email:
                domain = email.split('@')[1]
                if domain != self.domain_restriction:
                    raise SSOValidationError(f"Email domain {domain} not allowed")
            
            return idinfo
            
        except GoogleAuthError as e:
            logger.error(f"Google token validation failed: {e}")
            raise SSOValidationError(f"Invalid Google token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error validating Google token: {e}")
            raise SSOValidationError("Token validation failed")
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get additional user profile information from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            Dictionary containing extended user profile
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get user profile
            profile_response = httpx.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers=headers
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get organization info if available
            try:
                admin_response = httpx.get(
                    "https://www.googleapis.com/admin/directory/v1/users/me",
                    headers=headers
                )
                if admin_response.status_code == 200:
                    admin_data = admin_response.json()
                    profile_data.update({
                        "department": admin_data.get("orgUnitPath", "").replace("/", ""),
                        "title": admin_data.get("title"),
                        "manager": admin_data.get("managerId")
                    })
            except Exception:
                # Admin API not available, continue with basic profile
                pass
            
            return profile_data
            
        except Exception as e:
            logger.warning(f"Failed to get Google user profile: {e}")
            return {}
    
    def map_user_role(self, user_info: Dict[str, Any]) -> Role:
        """
        Map Google user information to application role.
        
        Args:
            user_info: User information from Google
            
        Returns:
            Mapped Role enum value
        """
        # Check if user is in admin role based on email or groups
        email = user_info.get('email', '').lower()
        
        # Simple admin detection based on email patterns
        admin_patterns = ['admin@', 'hr@', 'manager@']
        if any(pattern in email for pattern in admin_patterns):
            return Role.admin
        
        # Check organization unit for admin roles
        org_unit = user_info.get('department', '').lower()
        if any(dept in org_unit for dept in ['admin', 'hr', 'management']):
            return Role.admin
        
        return SSOConfig.DEFAULT_ROLE


class AzureSSOService:
    """Azure AD (Microsoft Entra ID) SSO integration service"""
    
    def __init__(self):
        self.client_id = SSOConfig.AZURE_CLIENT_ID
        self.client_secret = SSOConfig.AZURE_CLIENT_SECRET
        self.tenant_id = SSOConfig.AZURE_TENANT_ID
        self.authority = SSOConfig.AZURE_AUTHORITY
        self.scope = SSOConfig.AZURE_SCOPE
        
        # Initialize MSAL app
        if self.client_id and self.client_secret:
            self.msal_app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
        else:
            self.msal_app = None
    
    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate Azure AD access token and get user information.
        
        Args:
            access_token: Azure AD access token
            
        Returns:
            Dictionary containing user information
            
        Raises:
            SSOValidationError: If token validation fails
        """
        if not self.client_id or not self.tenant_id:
            raise SSOValidationError("Azure AD SSO not configured")
        
        try:
            # Call Microsoft Graph API to validate token and get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = httpx.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers
            )
            
            if response.status_code == 401:
                raise SSOValidationError("Invalid or expired Azure token")
            elif response.status_code != 200:
                raise SSOValidationError(f"Azure API error: {response.status_code}")
            
            user_info = response.json()
            
            # Get additional user information
            extended_info = self.get_user_profile(access_token)
            user_info.update(extended_info)
            
            return user_info
            
        except httpx.RequestError as e:
            logger.error(f"Network error validating Azure token: {e}")
            raise SSOValidationError("Network error during token validation")
        except Exception as e:
            logger.error(f"Unexpected error validating Azure token: {e}")
            raise SSOValidationError("Token validation failed")
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get extended user profile from Azure AD.
        
        Args:
            access_token: Azure AD access token
            
        Returns:
            Dictionary containing extended profile information
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            extended_info = {}
            
            # Get manager information
            try:
                manager_response = httpx.get(
                    "https://graph.microsoft.com/v1.0/me/manager",
                    headers=headers
                )
                if manager_response.status_code == 200:
                    manager_data = manager_response.json()
                    extended_info["manager"] = {
                        "id": manager_data.get("id"),
                        "displayName": manager_data.get("displayName"),
                        "mail": manager_data.get("mail")
                    }
            except Exception:
                pass
            
            # Get group memberships for role mapping
            try:
                groups_response = httpx.get(
                    "https://graph.microsoft.com/v1.0/me/memberOf",
                    headers=headers
                )
                if groups_response.status_code == 200:
                    groups_data = groups_response.json()
                    extended_info["groups"] = [
                        {
                            "id": group.get("id"),
                            "displayName": group.get("displayName")
                        }
                        for group in groups_data.get("value", [])
                    ]
            except Exception:
                pass
            
            return extended_info
            
        except Exception as e:
            logger.warning(f"Failed to get Azure user profile: {e}")
            return {}
    
    def map_user_role(self, user_info: Dict[str, Any]) -> Role:
        """
        Map Azure AD user information to application role.
        
        Args:
            user_info: User information from Azure AD
            
        Returns:
            Mapped Role enum value
        """
        # Check job title for admin roles
        job_title = user_info.get("jobTitle", "").lower()
        admin_titles = ["administrator", "manager", "director", "hr", "admin"]
        
        if any(title in job_title for title in admin_titles):
            return Role.admin
        
        # Check department
        department = user_info.get("department", "").lower()
        admin_departments = ["hr", "human resources", "administration", "management"]
        
        if any(dept in department for dept in admin_departments):
            return Role.admin
        
        # Check group memberships
        groups = user_info.get("groups", [])
        admin_groups = ["admins", "hr", "managers", "administrators"]
        
        for group in groups:
            group_name = group.get("displayName", "").lower()
            if any(admin_group in group_name for admin_group in admin_groups):
                return Role.admin
        
        return SSOConfig.DEFAULT_ROLE
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Get Azure AD authorization URL for OAuth flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL string
        """
        if not self.msal_app:
            raise SSOError("Azure AD not properly configured")
        
        auth_url = self.msal_app.get_authorization_request_url(
            scopes=self.scope,
            state=state or secrets.token_urlsafe(32)
        )
        return auth_url
    
    def exchange_code_for_token(self, auth_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            auth_code: Authorization code from Azure AD
            redirect_uri: Redirect URI used in authorization request
            
        Returns:
            Token response dictionary
        """
        if not self.msal_app:
            raise SSOError("Azure AD not properly configured")
        
        try:
            result = self.msal_app.acquire_token_by_authorization_code(
                auth_code,
                scopes=self.scope,
                redirect_uri=redirect_uri
            )
            
            if "error" in result:
                raise SSOValidationError(f"Token exchange failed: {result.get('error_description')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Azure token exchange failed: {e}")
            raise SSOValidationError("Token exchange failed")


class SSOUserService:
    """Service for managing SSO user provisioning and synchronization"""
    
    def __init__(self, session: Session):
        self.session = session
        self.google_service = GoogleSSOService()
        self.azure_service = AzureSSOService()
    
    def provision_or_update_user(
        self, 
        user_info: Dict[str, Any], 
        provider: str,
        role: Role = None
    ) -> User:
        """
        Provision a new user or update an existing one from SSO provider.
        
        Args:
            user_info: User information from SSO provider
            provider: SSO provider name ('google' or 'azure')
            role: Optional role override
            
        Returns:
            User model instance
        """
        # Extract common user information
        if provider == "google":
            email = user_info.get("email")
            full_name = user_info.get("name")
            department = user_info.get("department")
            mapped_role = role or self.google_service.map_user_role(user_info)
        elif provider == "azure":
            email = user_info.get("mail") or user_info.get("userPrincipalName")
            full_name = user_info.get("displayName")
            department = user_info.get("department")
            mapped_role = role or self.azure_service.map_user_role(user_info)
        else:
            raise SSOProvisioningError(f"Unknown SSO provider: {provider}")
        
        if not email:
            raise SSOProvisioningError("Email not provided by SSO provider")
        
        # Check if user already exists
        existing_user = crud.get_user_by_email(self.session, email=email)
        
        if existing_user:
            # Update existing user
            existing_user.full_name = full_name or existing_user.full_name
            existing_user.department = department or existing_user.department
            existing_user.role = mapped_role
            existing_user.is_active = True
            
            self.session.add(existing_user)
            self.session.commit()
            self.session.refresh(existing_user)
            
            logger.info(f"Updated existing user {email} from {provider} SSO")
            return existing_user
        
        elif SSOConfig.AUTO_PROVISION_USERS:
            # Create new user
            random_password = secrets.token_urlsafe(32)
            
            new_user = crud.create_user(
                session=self.session,
                email=email,
                full_name=full_name or email.split("@")[0],
                password=random_password,
                department=department,
                role=mapped_role
            )
            
            logger.info(f"Auto-provisioned new user {email} from {provider} SSO")
            return new_user
        
        else:
            raise SSOProvisioningError(f"User {email} not found and auto-provisioning is disabled")
    
    def authenticate_google_user(self, id_token: str) -> Tuple[User, str]:
        """
        Authenticate user with Google ID token.
        
        Args:
            id_token: Google ID token
            
        Returns:
            Tuple of (User instance, JWT access token)
        """
        try:
            # Validate token and get user info
            user_info = self.google_service.validate_token(id_token)
            
            # Provision or update user
            user = self.provision_or_update_user(user_info, "google")
            
            # Create JWT token
            access_token = create_access_token(user.id)
            
            return user, access_token
            
        except Exception as e:
            logger.error(f"Google SSO authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google SSO authentication failed: {str(e)}"
            )
    
    def authenticate_azure_user(self, access_token: str) -> Tuple[User, str]:
        """
        Authenticate user with Azure AD access token.
        
        Args:
            access_token: Azure AD access token
            
        Returns:
            Tuple of (User instance, JWT access token)
        """
        try:
            # Validate token and get user info
            user_info = self.azure_service.validate_token(access_token)
            
            # Provision or update user
            user = self.provision_or_update_user(user_info, "azure")
            
            # Create JWT token
            jwt_token = create_access_token(user.id)
            
            return user, jwt_token
            
        except Exception as e:
            logger.error(f"Azure SSO authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Azure SSO authentication failed: {str(e)}"
            )
    
    def sync_user_profile(self, user_id: int, provider: str, access_token: str) -> User:
        """
        Sync user profile information from SSO provider.
        
        Args:
            user_id: User ID to sync
            provider: SSO provider ('google' or 'azure')
            access_token: Valid access token for the provider
            
        Returns:
            Updated User instance
        """
        user = self.session.get(User, user_id)
        if not user:
            raise SSOProvisioningError(f"User {user_id} not found")
        
        try:
            if provider == "google":
                profile_info = self.google_service.get_user_profile(access_token)
            elif provider == "azure":
                profile_info = self.azure_service.get_user_profile(access_token)
            else:
                raise SSOProvisioningError(f"Unknown provider: {provider}")
            
            # Update user profile with latest information
            if profile_info.get("department"):
                user.department = profile_info["department"]
            
            # Update role based on current provider information
            if provider == "google":
                user.role = self.google_service.map_user_role(profile_info)
            elif provider == "azure":
                user.role = self.azure_service.map_user_role(profile_info)
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            
            logger.info(f"Synced profile for user {user.email} from {provider}")
            return user
            
        except Exception as e:
            logger.error(f"Profile sync failed for user {user_id}: {e}")
            raise SSOProvisioningError(f"Profile sync failed: {str(e)}")


# Convenience functions for easy integration
def create_google_sso_service() -> GoogleSSOService:
    """Create a Google SSO service instance."""
    return GoogleSSOService()


def create_azure_sso_service() -> AzureSSOService:
    """Create an Azure SSO service instance."""
    return AzureSSOService()


def create_sso_user_service(session: Session) -> SSOUserService:
    """Create an SSO user service instance."""
    return SSOUserService(session)