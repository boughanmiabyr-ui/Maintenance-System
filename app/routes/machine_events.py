from flask import Blueprint, request, jsonify
from app.models import db, Machine, MachineStatus, MachineEvent
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

# ============================================
# API ENDPOINTS FOR RASPBERRY PI EVENTS
# ============================================

@events_bp.route('/get_machine_name', methods=['POST'])
def get_machine_name():
    """Get machine name and code from IP address (for Raspberry Pi)"""
    try:
        data = request.get_json() or {}
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({"error": "IP address required"}), 400
        
        machine = Machine.query.filter_by(ip_address=ip_address).first()
        
        if not machine:
            logger.warning(f"Machine not found for IP: {ip_address}")
            return jsonify({"error": "Machine not found for this IP address"}), 404
        
        logger.info(f"Machine found for IP {ip_address}: {machine.machine_code}")
        return jsonify({
            "machine_name": machine.machine_code,
            "machine_id": machine.id,
            "department": machine.department,
            "zone": machine.zone
        }), 200
    except Exception as e:
        logger.error(f"Error getting machine name: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/machines/list', methods=['GET'])
def get_machines_list():
    """Get list of all active machines"""
    try:
        machines = Machine.query.filter_by(status='active').all()
        return jsonify({
            "machines": [
                {
                    "id": m.id,
                    "machine_code": m.machine_code,
                    "machine_name": m.machine_name,
                    "department": m.department
                }
                for m in machines
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error getting machines list: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/recent/<machine_name>', methods=['GET'])
def get_recent_events(machine_name):
    """Get recent events for a machine"""
    try:
        hours = request.args.get('hours', default=24, type=int)
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        since = datetime.utcnow() - timedelta(hours=hours)
        events = MachineEvent.query.filter(
            MachineEvent.machine_id == machine.id,
            MachineEvent.event_start_time >= since
        ).order_by(MachineEvent.event_start_time.desc()).limit(50).all()
        
        return jsonify({
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "event_status": e.event_status,
                    "event_start_time": e.event_start_time.isoformat(),
                    "event_end_time": e.event_end_time.isoformat() if e.event_end_time else None,
                    "duration_seconds": e.duration_seconds,
                    "start_user_id": e.start_user_id,
                    "end_user_id": e.end_user_id,
                    "start_comment": e.start_comment,
                    "end_comment": e.end_comment
                }
                for e in events
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error getting recent events: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/machine_status/<machine_name>', methods=['GET'])
def get_machine_status(machine_name):
    """Get current status of a machine"""
    try:
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            return jsonify({"status": "unknown"}), 404
        
        return jsonify({
            "machine_name": status.machine_name,
            "current_status": status.current_status,
            "status_since": status.status_since.isoformat(),
            "power_status": status.power_status,
            "last_event_type": status.last_event_type,
            "last_user_start": status.last_user_start,
            "last_user_end": status.last_user_end,
            "cumulative_downtime_today": status.cumulative_downtime_today,
            "current_downtime_duration": status.current_downtime_duration,
            "last_updated": status.last_updated.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting machine status: {e}")
        return jsonify({"error": str(e)}), 500



@events_bp.route('/downtime/<machine_name>', methods=['POST'])
def downtime_event(machine_name):
    """Handle downtime start event from Raspberry Pi"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        # Get or create machine status
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        # Update status
        status.current_status = 'downtime'
        status.status_since = datetime.utcnow()
        status.last_event_type = 'downtime'
        status.last_user_start = data.get('start_user_id', 'N/A')
        status.last_comment = data.get('start_comment', '')
        
        # Create event record
        event = MachineEvent(
            machine_id=machine.id,
            machine_name=machine_name,
            event_type='downtime',
            event_status='started',
            start_user_id=data.get('start_user_id', 'N/A'),
            start_comment=data.get('start_comment', ''),
            event_start_time=datetime.utcnow()
        )
        
        db.session.add(event)
        status.current_downtime_duration = 0
        db.session.commit()
        
        logger.info(f"Downtime started for {machine_name}")
        return jsonify({"status": "success", "message": f"Downtime started for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording downtime: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/reset_downtime/<machine_name>', methods=['POST'])
def reset_downtime(machine_name):
    """Handle downtime end event"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        # Find last downtime event
        last_event = MachineEvent.query.filter_by(
            machine_id=machine.id,
            event_type='downtime',
            event_status='started'
        ).order_by(MachineEvent.event_start_time.desc()).first()
        
        if last_event:
            last_event.event_end_time = datetime.utcnow()
            last_event.event_status = 'ended'
            last_event.duration_seconds = (last_event.event_end_time - last_event.event_start_time).total_seconds()
            last_event.end_user_id = data.get('end_user_id', 'N/A')
            last_event.end_comment = data.get('end_comment', '')
            
            duration_hours = last_event.duration_seconds / 3600
            status.cumulative_downtime_today += duration_hours
        
        status.current_status = 'working'
        status.last_user_end = data.get('end_user_id', 'N/A')
        status.current_downtime_duration = 0
        
        db.session.commit()
        logger.info(f"Downtime ended for {machine_name}")
        return jsonify({"status": "success", "message": f"Downtime ended for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting downtime: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/maintenance/<machine_name>', methods=['POST'])
def maintenance_event(machine_name):
    """Handle maintenance/breakdown start event"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        status.current_status = 'maintenance'
        status.status_since = datetime.utcnow()
        status.last_event_type = 'maintenance'
        status.last_user_start = data.get('start_user_id', 'N/A')
        status.last_comment = data.get('start_comment', '')
        
        event = MachineEvent(
            machine_id=machine.id,
            machine_name=machine_name,
            event_type='maintenance',
            event_status='started',
            start_user_id=data.get('start_user_id', 'N/A'),
            start_comment=data.get('start_comment', ''),
            breakdown_type=data.get('start_comment', ''),
            event_start_time=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Maintenance started for {machine_name}")
        return jsonify({"status": "success", "message": f"Maintenance started for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording maintenance event: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/reset_maintenance/<machine_name>', methods=['POST'])
def reset_maintenance(machine_name):
    """Handle maintenance end event"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        # Find last maintenance event
        last_event = MachineEvent.query.filter_by(
            machine_id=machine.id,
            event_type='maintenance',
            event_status='started'
        ).order_by(MachineEvent.event_start_time.desc()).first()
        
        if last_event:
            last_event.event_end_time = datetime.utcnow()
            last_event.event_status = 'ended'
            last_event.duration_seconds = (last_event.event_end_time - last_event.event_start_time).total_seconds()
            last_event.end_user_id = data.get('end_user_id', 'N/A')
            last_event.end_comment = data.get('end_comment', '')
            last_event.breakdown_type = data.get('breakdown', last_event.breakdown_type)
        
        status.current_status = 'working'
        status.last_user_end = data.get('end_user_id', 'N/A')
        
        db.session.commit()
        logger.info(f"Maintenance ended for {machine_name}")
        return jsonify({"status": "success", "message": f"Maintenance ended for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting maintenance: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/maintenance_arrival/<machine_name>', methods=['POST'])
def maintenance_arrival(machine_name):
    """Handle maintenance team arrival"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        # Find last maintenance event
        last_event = MachineEvent.query.filter_by(
            machine_id=machine.id,
            event_type='maintenance',
            event_status='started'
        ).order_by(MachineEvent.event_start_time.desc()).first()
        
        if last_event:
            last_event.maintenance_arrival_time = datetime.utcnow()
            last_event.maintenance_arrival_user_id = data.get('maintenance_arrival_user_id', 'N/A')
            last_event.reaction_time_seconds = data.get('reaction_time', 0)
            db.session.commit()
        
        logger.info(f"Maintenance arrived for {machine_name}")
        return jsonify({"status": "success", "message": f"Maintenance arrival recorded"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording maintenance arrival: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/break/<machine_name>', methods=['POST'])
def break_event(machine_name):
    """Handle break/lunch start event"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        status.current_status = 'break'
        status.status_since = datetime.utcnow()
        status.last_event_type = 'break'
        status.last_user_start = data.get('start_user_id', 'N/A')
        status.last_comment = data.get('start_comment', '')
        
        event = MachineEvent(
            machine_id=machine.id,
            machine_name=machine_name,
            event_type='break',
            event_status='started',
            start_user_id=data.get('start_user_id', 'N/A'),
            start_comment=data.get('start_comment', ''),
            event_start_time=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Break started for {machine_name}")
        return jsonify({"status": "success", "message": f"Break started for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording break event: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/reset_break/<machine_name>', methods=['POST'])
def reset_break(machine_name):
    """Handle break end event"""
    try:
        data = request.get_json() or {}
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        # Find last break event
        last_event = MachineEvent.query.filter_by(
            machine_id=machine.id,
            event_type='break',
            event_status='started'
        ).order_by(MachineEvent.event_start_time.desc()).first()
        
        if last_event:
            last_event.event_end_time = datetime.utcnow()
            last_event.event_status = 'ended'
            last_event.duration_seconds = (last_event.event_end_time - last_event.event_start_time).total_seconds()
            last_event.end_user_id = data.get('end_user_id', 'N/A')
            last_event.end_comment = data.get('end_comment', '')
        
        status.current_status = 'working'
        status.last_user_end = data.get('end_user_id', 'N/A')
        
        db.session.commit()
        logger.info(f"Break ended for {machine_name}")
        return jsonify({"status": "success", "message": f"Break ended for {machine_name}"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting break: {e}")
        return jsonify({"error": str(e)}), 500


@events_bp.route('/power_cut/<machine_name>', methods=['POST'])
def power_cut_event(machine_name):
    """Handle power cut event"""
    try:
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if not status:
            status = MachineStatus(machine_id=machine.id, machine_name=machine_name)
            db.session.add(status)
        
        status.current_status = 'offline'
        status.power_status = 'off'
        status.status_since = datetime.utcnow()
        
        event = MachineEvent(
            machine_id=machine.id,
            machine_name=machine_name,
            event_type='power_cut',
            event_status='started',
            event_start_time=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Power cut recorded for {machine_name}")
        return jsonify({"status": "success", "message": f"Power cut recorded"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording power cut: {e}")
        return jsonify({"error": str(e)}), 500
