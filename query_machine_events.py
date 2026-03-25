#!/usr/bin/env python3
"""
Query recent events from Raspberry Pi machines
Shows how to check the latest events received from each machine
"""

from app.models import Machine, MachineStatus, MachineEvent
from app import create_app
from datetime import datetime, timedelta
import json

app = create_app()

def get_machine_info():
    """Display all machines with their IP addresses and current status"""
    with app.app_context():
        machines = Machine.query.all()
        
        if not machines:
            print("No machines found in the system.")
            return
        
        print("\n" + "="*80)
        print("MACHINE INFORMATION & IP ADDRESSES")
        print("="*80 + "\n")
        
        for machine in machines:
            print(f"Machine Code: {machine.machine_code}")
            print(f"  Name: {machine.machine_name or machine.name}")
            print(f"  IP Address: {machine.ip_address or 'NOT SET'}")
            print(f"  Department: {machine.department}")
            print(f"  Zone: {machine.zone or 'N/A'}")
            print(f"  Status: {machine.status}")
            
            # Get current status
            status = MachineStatus.query.filter_by(machine_id=machine.id).first()
            if status:
                print(f"  Current Status: {status.current_status}")
                print(f"  Status Since: {status.status_since}")
                print(f"  Downtime Today: {status.cumulative_downtime_today:.2f} hrs")
            else:
                print(f"  Current Status: NO STATUS RECORDED")
            
            print()


def get_latest_events(machine_code=None, hours=24):
    """Get the latest events from Raspberry Pi"""
    with app.app_context():
        print("\n" + "="*80)
        print(f"LATEST MACHINE EVENTS (Last {hours} Hours)")
        print("="*80 + "\n")
        
        if machine_code:
            # Get specific machine
            machine = Machine.query.filter_by(machine_code=machine_code).first()
            if not machine:
                print(f"Machine {machine_code} not found!")
                return
            
            print(f"Machine: {machine.machine_code} - {machine.machine_name or machine.name}")
            print(f"IP Address: {machine.ip_address or 'NOT SET'}\n")
            
            since = datetime.utcnow() - timedelta(hours=hours)
            events = MachineEvent.query.filter(
                MachineEvent.machine_id == machine.id,
                MachineEvent.event_start_time >= since
            ).order_by(MachineEvent.event_start_time.desc()).all()
            
            if not events:
                print(f"No events found for {machine_code} in the last {hours} hours.")
                return
            
            for event in events:
                print_event(event)
        else:
            # Get all recent events across all machines
            since = datetime.utcnow() - timedelta(hours=hours)
            events = MachineEvent.query.filter(
                MachineEvent.event_start_time >= since
            ).order_by(MachineEvent.event_start_time.desc()).all()
            
            if not events:
                print(f"No events found in the last {hours} hours.")
                return
            
            current_machine = None
            for event in events:
                if event.machine_name != current_machine:
                    if current_machine is not None:
                        print("\n" + "-"*80 + "\n")
                    current_machine = event.machine_name
                    print(f"Machine: {event.machine_name}\n")
                
                print_event(event)


def print_event(event):
    """Pretty print an event"""
    print(f"  [{event.event_type.upper()}] - {event.event_status}")
    print(f"    Start: {event.event_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if event.event_end_time:
        print(f"    End:   {event.event_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        duration = event.duration_seconds
        if duration:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            print(f"    Duration: {hours}h {minutes}m {seconds}s")
    else:
        print(f"    End:   NOT ENDED YET (ONGOING)")
    
    if event.start_user_id:
        print(f"    Started by: {event.start_user_id}")
    
    if event.end_user_id:
        print(f"    Ended by: {event.end_user_id}")
    
    if event.start_comment:
        print(f"    Start Comment: {event.start_comment}")
    
    if event.end_comment:
        print(f"    End Comment: {event.end_comment}")
    
    if event.reaction_time_seconds:
        print(f"    Reaction Time: {event.reaction_time_seconds} seconds")
    
    print()


def get_active_events():
    """Get currently active events (not ended yet)"""
    with app.app_context():
        print("\n" + "="*80)
        print("CURRENTLY ACTIVE EVENTS (NOT YET ENDED)")
        print("="*80 + "\n")
        
        active_events = MachineEvent.query.filter(
            MachineEvent.event_status.in_(['started'])
        ).order_by(MachineEvent.event_start_time.desc()).all()
        
        if not active_events:
            print("No active events currently.")
            return
        
        for event in active_events:
            machine = Machine.query.get(event.machine_id)
            print(f"Machine: {event.machine_name} ({machine.ip_address if machine else 'NO IP'})")
            print_event(event)


def get_machine_downtime_summary():
    """Get downtime summary for all machines today"""
    with app.app_context():
        print("\n" + "="*80)
        print("MACHINE DOWNTIME SUMMARY (TODAY)")
        print("="*80 + "\n")
        
        statuses = MachineStatus.query.all()
        
        if not statuses:
            print("No downtime data recorded yet.")
            return
        
        for status in statuses:
            machine = Machine.query.get(status.machine_id)
            if machine:
                print(f"{machine.machine_code} ({machine.ip_address or 'NO IP'}):")
                print(f"  Current Status: {status.current_status}")
                print(f"  Cumulative Downtime: {status.cumulative_downtime_today:.2f} hours")
                print(f"  Last Updated: {status.last_updated}")
                print()


if __name__ == '__main__':
    import sys
    
    print("\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║              RASPBERRY PI MACHINE EVENTS QUERY TOOL                          ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    
    # Display all options
    print("\nAvailable options:")
    print("  1. Get machine information & IP addresses")
    print("  2. Get latest events (all machines)")
    print("  3. Get latest events for specific machine")
    print("  4. Get currently active events")
    print("  5. Get downtime summary")
    print("  6. Exit")
    
    while True:
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            get_machine_info()
        
        elif choice == '2':
            hours_input = input("How many hours back? (default 24): ").strip()
            hours = int(hours_input) if hours_input.isdigit() else 24
            get_latest_events(hours=hours)
        
        elif choice == '3':
            machine_code = input("Enter machine code (e.g., M001): ").strip().upper()
            hours_input = input("How many hours back? (default 24): ").strip()
            hours = int(hours_input) if hours_input.isdigit() else 24
            get_latest_events(machine_code=machine_code, hours=hours)
        
        elif choice == '4':
            get_active_events()
        
        elif choice == '5':
            get_machine_downtime_summary()
        
        elif choice == '6':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")
