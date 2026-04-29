"""
Script to clear all alerts and start fresh
"""

import os
from app import create_app, db
from app.models import StockAlert
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    print("Clearing all alerts...")
    
    # Get alert count before
    before_count = StockAlert.query.count()
    print(f"Alerts before cleanup: {before_count}")
    
    # Delete all alerts
    db.session.query(StockAlert).delete()
    db.session.commit()
    
    # Verify
    after_count = StockAlert.query.count()
    print(f"Alerts after cleanup: {after_count}")
    print(f"✓ Deleted {before_count - after_count} alerts!")
