#!/usr/bin/env python
"""
Simple test to verify the application starts without database errors
"""

from app import create_app, db
from flask import render_template
from sqlalchemy import text

app = create_app()

print("Testing application startup...")
print()

# Test 1: App created successfully
print("✓ Flask app created successfully")

# Test 2: Database connection
with app.app_context():
    try:
        # Test database connection
        result = db.session.execute(text("SELECT 1"))
        print("✓ Database connection OK")
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        exit(1)

# Test 3: Check schema
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    if 'maintenance_reports' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('maintenance_reports')]
        if 'archive_date' in columns:
            print("✓ archive_date column present in database")
        else:
            print("✗ archive_date column NOT found")
            exit(1)

# Test 4: Try the problematic query
with app.app_context():
    try:
        from app.models import MaintenanceReport
        reports = MaintenanceReport.query.filter_by(report_type='preventive').all()
        print(f"✓ Preventive reports query works ({len(reports)} records)")
    except Exception as e:
        print(f"✗ Preventive reports query failed: {e}")
        exit(1)

print()
print("✓ All tests passed! Application is ready.")
