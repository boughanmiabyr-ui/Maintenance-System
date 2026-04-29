"""
Script to clean up orphaned and invalid alerts
"""

import os
from app import create_app, db
from app.models import StockAlert, Material
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    print("Cleaning up alerts...")
    
    # Get all alerts
    all_alerts = StockAlert.query.all()
    print(f"Total alerts in database: {len(all_alerts)}")
    
    # Find orphaned alerts (referencing deleted materials)
    orphaned_count = 0
    for alert in all_alerts:
        material = Material.query.get(alert.material_id)
        if material is None:
            orphaned_count += 1
            db.session.delete(alert)
    
    print(f"Orphaned alerts (referencing deleted materials): {orphaned_count}")
    
    # Get remaining alerts for the 10 materials
    remaining_alerts = StockAlert.query.filter(
        StockAlert.material_id.in_([m.id for m in Material.query.all()])
    ).all()
    
    print(f"Valid alerts for remaining materials: {len(remaining_alerts)}")
    
    # Commit cleanup
    db.session.commit()
    
    # Verify final count
    final_alert_count = StockAlert.query.count()
    print(f"\nFinal alert count: {final_alert_count}")
    print("✓ Alert cleanup completed!")
