from app import create_app

app = create_app()

def test_corrective_tasks_route():
    with app.test_client() as client:
        with app.app_context():
            from app.models import User
            user = User.query.filter_by(role='technician').first()
            if not user:
                print("No technician user found")
                return
                
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['username'] = user.username
                sess['role'] = user.role
            
            # Test the corrective tasks route
            response = client.get('/corrective-maintenance-tasks')
            print(f"GET /corrective-maintenance-tasks: {response.status_code}")
            
            if response.status_code == 200:
                content = response.data.decode('utf-8').lower()
                checks = [
                    ('corrective maintenance tasks' in content, 'Page title found'),
                    ('filter by category' in content, 'Filter section found'),
                    ('search tasks' in content, 'Search input found'),
                    ('mécanique' in content, 'Mécanique category found'),
                    ('électrique' in content, 'Électrique category found'),
                    ('informatique' in content, 'Informatique category found'),
                ]
                
                print("\nContent checks:")
                for check, description in checks:
                    status = "✓" if check else "✗"
                    print(f"  {status} {description}")

if __name__ == '__main__':
    test_corrective_tasks_route()
