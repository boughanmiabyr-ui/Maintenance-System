#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot Raspberry Pi connectivity issues
Run this from the Flask app directory to test the API endpoints
"""

from app.models import Machine, MachineEvent, MachineStatus
from app import create_app
import json

app = create_app()

def check_database():
    """Check if machines have IP addresses recorded"""
    with app.app_context():
        print("\n" + "="*80)
        print("DATABASE CHECK: Machines with IP Addresses")
        print("="*80 + "\n")
        
        machines = Machine.query.all()
        
        if not machines:
            print("❌ NO MACHINES FOUND IN DATABASE")
            return False
        
        has_ip = False
        for machine in machines:
            status = "✓" if machine.ip_address else "❌"
            print(f"{status} {machine.machine_code}")
            print(f"   Name: {machine.machine_name or machine.name}")
            print(f"   IP: {machine.ip_address or 'NO IP ADDRESS SET'}")
            print(f"   Department: {machine.department}")
            print()
            
            if machine.ip_address:
                has_ip = True
        
        if not has_ip:
            print("❌ WARNING: No machines have IP addresses assigned!")
            print("   You need to run the migration and add IP addresses to machines")
            return False
        
        return True


def check_api_endpoint():
    """Test the /api/events/get_machine_name endpoint"""
    with app.app_context():
        print("\n" + "="*80)
        print("API ENDPOINT TEST: /api/events/get_machine_name")
        print("="*80 + "\n")
        
        # Find a machine with an IP
        machine = Machine.query.filter(Machine.ip_address != None).first()
        
        if not machine:
            print("❌ No machine with IP address found to test")
            return False
        
        test_ip = machine.ip_address
        print(f"Testing with IP: {test_ip}")
        print(f"Expected machine code: {machine.machine_code}\n")
        
        # Simulate what Raspberry Pi sends
        from app.routes.machine_events import events_bp
        
        # Create test client
        with app.test_client() as client:
            response = client.post(
                '/api/events/get_machine_name',
                json={'ip_address': test_ip},
                content_type='application/json'
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.get_json(), indent=2)}\n")
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('machine_name'):
                    print(f"✓ API is working! Machine name returned: {data['machine_name']}")
                    return True
                else:
                    print("❌ API returned 200 but no machine_name in response")
                    return False
            else:
                print(f"❌ API returned error: {response.status_code}")
                return False


def check_events_recorded():
    """Check if any events have been recorded"""
    with app.app_context():
        print("\n" + "="*80)
        print("EVENTS CHECK: Recent Events")
        print("="*80 + "\n")
        
        events_count = MachineEvent.query.count()
        
        if events_count == 0:
            print("❌ No events recorded yet")
            print("   This is normal on first setup - Raspberry Pi hasn't sent any events yet\n")
            return False
        
        print(f"✓ Found {events_count} total events\n")
        
        recent_events = MachineEvent.query.order_by(
            MachineEvent.event_start_time.desc()
        ).limit(5).all()
        
        for event in recent_events:
            machine = Machine.query.get(event.machine_id)
            print(f"Machine: {event.machine_name} ({machine.ip_address if machine else 'NO IP'})")
            print(f"  Event: {event.event_type} ({event.event_status})")
            print(f"  Time: {event.event_start_time}")
            print()
        
        return True


def check_flask_app():
    """Check if Flask app is configured correctly"""
    with app.app_context():
        print("\n" + "="*80)
        print("FLASK APP CHECK")
        print("="*80 + "\n")
        
        # Check if blueprint is registered
        print("✓ Flask app initialized")
        
        # Check blueprints
        blueprints = app.blueprints
        if 'events' in blueprints:
            print("✓ Events blueprint registered")
        else:
            print("❌ Events blueprint NOT registered")
            return False
        
        # Check routes
        print("\nRoutes available:")
        for rule in app.url_map.iter_rules():
            if 'events' in rule.rule or 'api' in rule.rule:
                print(f"  {rule.rule} [{','.join(rule.methods)}]")
        
        return True


def main():
    print("\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║           RASPBERRY PI CONNECTIVITY TROUBLESHOOTING TOOL                      ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    
    results = {
        "Flask App": check_flask_app(),
        "Database Machines": check_database(),
        "API Endpoint": check_api_endpoint(),
        "Events Recorded": check_events_recorded()
    }
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    for check, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80 + "\n")
    
    if not results["Flask App"]:
        print("1. ❌ Flask app issues - Check your app initialization")
        return
    
    if not results["Database Machines"]:
        print("1. ❌ No machines in database OR no IP addresses assigned")
        print("   ACTION: Run the migration_add_machine_ip.sql script")
        print("   Then add IP addresses to your machines:")
        print("   UPDATE machines SET ip_address = '192.168.1.100' WHERE machine_code = 'M001';")
        return
    
    if not results["API Endpoint"]:
        print("1. ❌ API endpoint not working")
        print("   ACTION: Check if:");
        print("   - Flask app is running (python main.py)")
        print("   - app/routes/machine_events.py exists and is imported")
        print("   - Blueprint is registered in app/__init__.py")
        return
    
    print("✓ All checks passed!")
    print("\nRaspberry Pi should now work. To verify:")
    print("1. Update raspberrycode.py MAIN_API_BASE_URL to point to your Flask server")
    print("2. Run the Raspberry Pi code")
    print("3. You should see 'Machine: [MACHINE_CODE]' in the output")
    print("4. Run this script again to see events appearing in the database")


if __name__ == '__main__':
    main()
