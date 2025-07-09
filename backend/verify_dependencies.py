#!/usr/bin/env python3
"""
Dependency verification script for the wellbeing platform backend.

This script checks that all required dependencies are properly installed
and can be imported without errors.
"""

import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Check if a dependency can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"✗ {package_name or module_name}: {e}")
        return False

def main():
    """Check all required dependencies."""
    print("=== Dependency Verification ===")
    print("Checking required packages for the wellbeing platform...\n")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlmodel", "SQLModel"),
        ("psycopg2", "PostgreSQL adapter"),
        ("passlib", "Password hashing"),
        ("jose", "JWT tokens"),
        ("dotenv", "Environment variables"),
        ("alembic", "Database migrations"),
        ("google.auth", "Google authentication"),
        ("reportlab", "PDF generation"),
        ("email_validator", "Email validation"),
        ("multipart", "Form data handling"),
        ("requests", "HTTP client"),
    ]
    
    test_dependencies = [
        ("pytest", "Testing framework"),
        ("httpx", "Async HTTP client for tests"),
        ("pytest_asyncio", "Async test support"),
    ]
    
    print("Core Dependencies:")
    failed_core = 0
    for module, name in dependencies:
        if not check_dependency(module, name):
            failed_core += 1
    
    print(f"\nTest Dependencies (optional):")
    failed_test = 0
    for module, name in test_dependencies:
        if not check_dependency(module, name):
            failed_test += 1
    
    print(f"\n=== Summary ===")
    print(f"Core dependencies: {len(dependencies) - failed_core}/{len(dependencies)} working")
    print(f"Test dependencies: {len(test_dependencies) - failed_test}/{len(test_dependencies)} working")
    
    if failed_core > 0:
        print(f"\n❌ {failed_core} core dependencies are missing!")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    if failed_test > 0:
        print(f"\n⚠️  {failed_test} test dependencies are missing (optional)")
        print("Install with: pip install -r requirements-dev.txt")
    
    print("\n✅ All core dependencies are properly installed!")
    print("Ready to run the wellbeing platform backend.")

if __name__ == "__main__":
    main()