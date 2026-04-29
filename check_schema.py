#!/usr/bin/env python
"""
Check database schema to verify all columns are present
"""

from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print('Checking database schema...\n')
    
    # Get all tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Check maintenance_reports table
    if 'maintenance_reports' in tables:
        columns = inspector.get_columns('maintenance_reports')
        column_names = [col['name'] for col in columns]
        
        print('maintenance_reports table columns:')
        for col in columns:
            col_type = str(col['type'])
            print(f'  - {col["name"]} ({col_type})')
        
        # Check if archive_date is there
        if 'archive_date' in column_names:
            print('\nArchive_date column: OK')
        else:
            print('\nArchive_date column: MISSING')
    else:
        print('maintenance_reports table not found')
