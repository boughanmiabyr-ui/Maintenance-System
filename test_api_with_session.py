from app import create_app, db
from app.models import User
from flask import session

app = create_app()

def test_with_session():
    with app.test_client() as client:
        with app.app_context():
            # Get a technician user
            user = User.query.filter_by(role='technician').first()
            if not user:
                print("No technician user found in database")
                return
                
            # Create a session and test
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['username'] = user.username
                sess['role'] = user.role
            
            # Now test the API  
            response = client.get('/api/machines-by-zone/1')
            print(f"GET /api/machines-by-zone/1: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"Success! Found {len(data)} machines:")
                for machine in data:
                    print(f"  - {machine['name']} ({machine['code']})")
            elif response.status_code == 401:
                print("Unauthorized - session not working")
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.data[:200]}")

if __name__ == '__main__':
    test_with_session()
