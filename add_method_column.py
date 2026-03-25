#!/usr/bin/env python3
"""Add method column to preventive_maintenance_tasks table"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    # Check if column exists
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('preventive_maintenance_tasks')]
    
    if 'method' not in columns:
        print("Adding method column to preventive_maintenance_tasks...")
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE preventive_maintenance_tasks ADD COLUMN method VARCHAR(10) DEFAULT "N"'))
        print("✓ method column added successfully")
    else:
        print("✓ method column already exists")
