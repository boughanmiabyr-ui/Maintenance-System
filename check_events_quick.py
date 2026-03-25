#!/usr/bin/env python3
"""
Quick example: Check events from command line
Usage:
    python check_events_quick.py M001           # Get all events from M001
    python check_events_quick.py M001 12        # Get events from last 12 hours
    python check_events_quick.py --active       # Get active events
    python check_events_quick.py --all          # Get all machines & their latest events
"""

from app.models import Machine, MachineStatus, MachineEvent
from app import create_app
from datetime import datetime, timedelta
import sys

app = create_app()

def main():
    with app.app_context():
        # Default: show all machines and latest events
        if len(sys.argv) == 1 or sys.argv[1] == '--all':
            show_all_machines()
        
        # Show active events
        elif sys.argv[1] == '--active':
            show_active_events()
        
        # Show events for specific machine
        else:
            machine_code = sys.argv[1].upper()
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            show_machine_events(machine_code, hours)


def show_all_machines():
    """Show all machines with their IP and latest event"""
    machines = Machine.query.all()
    
    print("\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                    ALL MACHINES & LATEST EVENTS                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝\n")
    
    for machine in machines:
        print(f"Machine: {machine.machine_code}")
        print(f"  Name: {machine.machine_name or machine.name}")
        print(f"  IP: {machine.ip_address or '❌ NO IP'}")
        print(f"  Department: {machine.department}")
        print(f"  Zone: {machine.zone or 'N/A'}")
        
        # Get latest event
        latest_event = MachineEvent.query.filter_by(
            machine_id=machine.id
        ).order_by(MachineEvent.event_start_time.desc()).first()
        
        if latest_event:
            print(f"  Latest Event: {latest_event.event_type} ({latest_event.event_status})")
            print(f"    Time: {latest_event.event_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  Latest Event: ❌ NO EVENTS YET")
        
        # Get current status
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if status:
            print(f"  Status: {status.current_status} | Downtime: {status.cumulative_downtime_today:.2f}h")
        
        print()


def show_machine_events(machine_code, hours=24):
    """Show events for a specific machine"""
    machine = Machine.query.filter_by(machine_code=machine_code).first()
    
    if not machine:
        print(f"❌ Machine {machine_code} not found!")
        return
    
    print(f"\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║  EVENTS FOR {machine.machine_code} (Last {hours} hours)")
    print(f"╚════════════════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"Machine: {machine.machine_code}")
    print(f"Name: {machine.machine_name or machine.name}")
    print(f"IP: {machine.ip_address or '❌ NO IP'}\n")
    
    since = datetime.utcnow() - timedelta(hours=hours)
    events = MachineEvent.query.filter(
        MachineEvent.machine_id == machine.id,
        MachineEvent.event_start_time >= since
    ).order_by(MachineEvent.event_start_time.desc()).all()
    
    if not events:
        print(f"No events found in the last {hours} hours.")
        return
    
    for i, event in enumerate(events, 1):
        status_icon = "✓" if event.event_status == 'ended' else "⏳" if event.event_status == 'started' else "✗"
        
        print(f"{i}. [{status_icon}] {event.event_type.upper()}")
        print(f"   Status: {event.event_status}")
        print(f"   Start: {event.event_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if event.event_end_time:
            duration = event.duration_seconds
            if duration:
                hours_val = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                print(f"   End:   {event.event_end_time.strftime('%Y-%m-%d %H:%M:%S')} ({hours_val}h {minutes}m {seconds}s)")
        else:
            print(f"   End:   ONGOING...")
        
        if event.start_user_id:
            print(f"   User: {event.start_user_id}")
        
        if event.start_comment:
            print(f"   Note: {event.start_comment}")
        
        print()


def show_active_events():
    """Show all currently active events"""
    print("\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                         CURRENTLY ACTIVE EVENTS                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝\n")
    
    active = MachineEvent.query.filter(
        MachineEvent.event_status == 'started'
    ).order_by(MachineEvent.event_start_time.desc()).all()
    
    if not active:
        print("✓ No active events. All machines are in normal state.\n")
        return
    
    print(f"⚠️  {len(active)} ACTIVE EVENT(S):\n")
    
    for event in active:
        machine = Machine.query.get(event.machine_id)
        elapsed = (datetime.utcnow() - event.event_start_time).total_seconds()
        hours_elapsed = int(elapsed // 3600)
        minutes_elapsed = int((elapsed % 3600) // 60)
        
        print(f"Machine: {event.machine_name} ({machine.ip_address if machine else 'NO IP'})")
        print(f"  Event: {event.event_type}")
        print(f"  Started: {event.event_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Elapsed: {hours_elapsed}h {minutes_elapsed}m")
        print()


if __name__ == '__main__':
    main()
