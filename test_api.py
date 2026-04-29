from app import create_app
from flask import json

app = create_app()

with app.test_client() as client:
    with app.app_context():
        # Test accessing new_maintenance_report_wizard route (requires login)
        response = client.get('/new-maintenance-report')
        print(f"GET /new-maintenance-report: {response.status_code}")
        
        # Test API endpoint (requires login)
        response = client.get('/api/machines-by-zone/1')
        print(f"GET /api/machines-by-zone/1: {response.status_code}")
        if response.status_code == 401:
            print("  -> Need authentication")
        elif response.status_code == 200:
            data = response.get_json()
            print(f"  -> Success: {data}")
            print(f"  -> Number of machines: {len(data)}")
        else:
            print(f"  -> Response: {response.data}")
