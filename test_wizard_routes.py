from app import create_app

app = create_app()

def test_routes():
    with app.test_client() as client:
        with app.app_context():
            # Get a technician user to set up session
            from app.models import User
            user = User.query.filter_by(role='technician').first()
            if not user:
                print("No technician user found")
                return
                
            # Create a session
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['username'] = user.username
                sess['role'] = user.role
            
            # Test wizard entry point
            print("Testing /new-maintenance-report")
            response = client.get('/new-maintenance-report')
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                if b"Step 1: Select Zone" in response.data:
                    print("  ✓ Zones section found")
                if b"Step 2: Select Machine" in response.data:
                    print("  ✓ Machine selection section found")
                if b"Step 3: Maintenance Category" in response.data:
                    print("  ✓ Maintenance Category section found")
                if b"Step 4: Preventive Type" in response.data:
                    print("  ✓ Preventive Type section found")
            else:
                print(f"  Error: {response.status_code}")
            
            # Test API endpoint
            print("\nTesting /api/machines-by-zone/1")
            response = client.get('/api/machines-by-zone/1')
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✓ Found {len(data)} machines")
            
            # Test maintenance report route
            print("\nTesting /maintenance-report")
            response = client.get('/maintenance-report')
            print(f"  Status: {response.status_code}")

if __name__ == '__main__':
    test_routes()
