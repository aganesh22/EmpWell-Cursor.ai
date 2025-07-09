#!/usr/bin/env python3
"""
Database migration script to add GDPR compliance tables and fields.

This script adds:
- UserConsent table for consent management
- DataProcessingLog table for audit trail
- DataRetentionPolicy table for retention policies
- DataExportRequest table for data export requests
- GDPR-related fields to existing User and TestAttempt tables

Usage:
    python create_gdpr_tables.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel

# Add the parent directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models import (
    User, UserConsent, DataProcessingLog, DataRetentionPolicy, 
    DataExportRequest, TestAttempt
)
from backend.app.database import engine

def create_gdpr_tables():
    """Create GDPR compliance tables and add new fields to existing tables"""
    
    print("Creating GDPR compliance tables...")
    
    # Create all tables defined in models
    SQLModel.metadata.create_all(engine)
    
    # Add GDPR fields to existing tables using raw SQL
    # These may already exist if the models were updated before running this script
    
    gdpr_migrations = [
        # Add GDPR fields to User table
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS data_processing_consent BOOLEAN DEFAULT TRUE;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS analytics_consent BOOLEAN DEFAULT FALSE;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN DEFAULT FALSE;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS consent_date TIMESTAMP;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS privacy_policy_version VARCHAR DEFAULT '1.0';
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS last_privacy_policy_acceptance TIMESTAMP;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS data_retention_override INTEGER;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS is_anonymized BOOLEAN DEFAULT FALSE;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS anonymized_at TIMESTAMP;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS anonymization_method VARCHAR;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS deletion_requested_at TIMESTAMP;
        """,
        """
        ALTER TABLE user ADD COLUMN IF NOT EXISTS deletion_scheduled_for TIMESTAMP;
        """,
        
        # Add GDPR fields to TestAttempt table
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS is_anonymized BOOLEAN DEFAULT FALSE;
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS anonymized_at TIMESTAMP;
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS retention_expires_at TIMESTAMP;
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS legal_basis VARCHAR DEFAULT 'legitimate_interest';
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS consent_id INTEGER REFERENCES userconsent(id);
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS anonymized_user_hash VARCHAR;
        """,
        """
        ALTER TABLE testattempt ADD COLUMN IF NOT EXISTS department_hash VARCHAR;
        """,
    ]
    
    try:
        with engine.connect() as conn:
            for migration in gdpr_migrations:
                try:
                    # Clean up the SQL - remove extra whitespace and newlines
                    clean_sql = ' '.join(migration.strip().split())
                    print(f"Executing: {clean_sql}")
                    conn.execute(text(clean_sql))
                    conn.commit()
                except Exception as e:
                    print(f"Migration may have already been applied or failed: {e}")
                    continue
    
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    
    print("GDPR tables and fields created successfully!")
    return True

def create_default_retention_policies():
    """Create default data retention policies"""
    
    print("Creating default data retention policies...")
    
    default_policies = [
        {
            "data_type": "assessment_results",
            "retention_period_days": 2555,  # 7 years
            "purpose": "Employee wellbeing monitoring and historical analysis",
            "legal_basis": "Legitimate interest - employee health and safety"
        },
        {
            "data_type": "personal_data",
            "retention_period_days": 1825,  # 5 years
            "purpose": "Account management and compliance",
            "legal_basis": "Contract performance and legal obligations"
        },
        {
            "data_type": "consent_records",
            "retention_period_days": 2555,  # 7 years
            "purpose": "GDPR compliance and audit trail",
            "legal_basis": "Legal obligation - GDPR Article 7"
        },
        {
            "data_type": "processing_logs",
            "retention_period_days": 2555,  # 7 years
            "purpose": "GDPR compliance and audit trail",
            "legal_basis": "Legal obligation - GDPR Article 30"
        },
        {
            "data_type": "marketing_data",
            "retention_period_days": 730,   # 2 years
            "purpose": "Marketing communications",
            "legal_basis": "Consent"
        }
    ]
    
    try:
        from backend.app.database import get_session
        from backend.app.models import DataRetentionPolicy
        from datetime import datetime
        
        session = next(get_session())
        
        for policy_data in default_policies:
            # Check if policy already exists
            existing = session.query(DataRetentionPolicy).filter(
                DataRetentionPolicy.data_type == policy_data["data_type"]
            ).first()
            
            if not existing:
                policy = DataRetentionPolicy(
                    data_type=policy_data["data_type"],
                    retention_period_days=policy_data["retention_period_days"],
                    purpose=policy_data["purpose"],
                    legal_basis=policy_data["legal_basis"],
                    auto_delete=True,
                    created_at=datetime.utcnow()
                )
                session.add(policy)
        
        session.commit()
        session.close()
        print("Default retention policies created successfully!")
        
    except Exception as e:
        print(f"Error creating default retention policies: {e}")
        return False
    
    return True

def main():
    """Run the GDPR migration"""
    print("=== GDPR Compliance Migration ===")
    print("This script will add GDPR compliance tables and fields to your database.")
    print()
    
    # Confirm with user
    response = input("Do you want to proceed? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Create tables and fields
    if not create_gdpr_tables():
        print("Migration failed!")
        sys.exit(1)
    
    # Create default policies
    if not create_default_retention_policies():
        print("Warning: Failed to create default retention policies.")
    
    print()
    print("=== Migration Complete ===")
    print("GDPR compliance features have been added to your database.")
    print()
    print("Next steps:")
    print("1. Update your .env file with any new configuration variables")
    print("2. Restart your FastAPI application")
    print("3. Test the new GDPR endpoints")
    print("4. Configure data retention policies as needed")
    print()

if __name__ == "__main__":
    main()