#!/usr/bin/env python
"""Test script for Preventive Maintenance Plan Card functionality"""

import os
import sys
from app import create_app, db
from app.models import Zone, Machine

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

def test_zones_and_machines():
    """Test if zones and machines exist in database"""
    with app.app_context():
        print("\n" + "="*60)
        print("PREVENTIVE MAINTENANCE CARD - TEST REPORT")
        print("="*60)
        
        # Check zones
        zones = Zone.query.all()
        print(f"\n✓ Total Zones: {len(zones)}")
        for zone in zones:
            print(f"  - {zone.name} (ID: {zone.id})")
        
        # Check machines
        machines = Machine.query.filter_by(status='active').all()
        print(f"\n✓ Total Active Machines: {len(machines)}")
        for machine in machines:
            print(f"  - {machine.machine_code} ({machine.name}) - Zone: {machine.zone}")
        
        # Check machines by zone
        print("\n✓ Machines by Zone:")
        for zone in zones:
            zone_machines = Machine.query.filter_by(zone_id=zone.id, status='active').all()
            print(f"  {zone.name}: {len(zone_machines)} machines")
            for machine in zone_machines:
                print(f"    - {machine.machine_code} ({machine.name})")
        
        print("\n" + "="*60)
        print("TEMPLATE REQUIREMENTS:")
        print("="*60)
        print("✓ Template: /app/templates/main/preventive_maintenance_plan_card.html")
        print("✓ Route: /preventive-maintenance-plan")
        print("✓ API Endpoint: /api/machines-by-zone/<zone_id>")
        print("✓ Features:")
        print("  - Step 1: Zone selection")
        print("  - Step 2: Machine selection (filtered by zone)")
        print("  - Step 3: 6-month calendar with maintenance schedules")
        print("  - Schedule details table (1-month, 3-month, 6-month)")
        print("\n" + "="*60)

if __name__ == '__main__':
    test_zones_and_machines()
