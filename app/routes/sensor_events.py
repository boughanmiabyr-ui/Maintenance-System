"""
Machine Events and Sensor API Routes
Handles events from Raspberry Pi and sensor count tracking for preventive maintenance
"""

from flask import Blueprint, request, jsonify, session, render_template, current_app
from app.models import db, Machine, MachineEvent, SensorCount, User
from app.routes.auth import login_required, role_required
from app.impulse_sensor import ImpulseDetector, SensorCountManager
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

# Create sensor events blueprint
sensor_bp = Blueprint('sensor', __name__, url_prefix='/api/sensor')


# ============================================
# SENSOR COUNT API ENDPOINTS
# ============================================

@sensor_bp.route('/sensor_count/<machine_name>', methods=['POST'])
def sensor_count_endpoint(machine_name):
    """
    Record sensor count increments
    Called from Raspberry Pi to log movement/impulse counts
    """
    try:
        data = request.get_json() or {}
        increment = data.get('increment', 0)
        
        if increment <= 0:
            return jsonify({'error': 'Invalid increment value'}), 400
        
        machine = Machine.query.filter_by(machine_name=machine_name).first()
        if not machine:
            return jsonify({'error': f'Machine {machine_name} not found'}), 404
        
        # Use SensorCountManager to record the impulse
        SensorCountManager.log_impulse_detection(machine.id, increment)
        
        # Check threshold status
        status = SensorCountManager.get_threshold_status(machine.id)
        
        logger.info(f"Sensor count recorded: {increment} for {machine_name}. Total: {status['total_count']}")
        
        return jsonify({
            'status': 'success',
            'total': status['total_count'],
            'percentage': status['percentage'],
            'threshold_reached': status['threshold_reached']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_count_endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@sensor_bp.route('/sensor_count_reset/<machine_name>', methods=['POST'])
def sensor_count_reset_endpoint(machine_name):
    """
    Reset sensor counter after preventive maintenance
    Called when maintenance is completed
    """
    try:
        data = request.get_json() or {}
        reset_by_user_id = data.get('reset_by_user_id', 'N/A')
        
        machine = Machine.query.filter_by(machine_name=machine_name).first()
        if not machine:
            return jsonify({'error': f'Machine {machine_name} not found'}), 404
        
        # Reset the counter
        success = SensorCountManager.get_threshold_status(machine.id)
        
        if success:
            # Update reset info
            today = datetime.utcnow().date()
            record = SensorCount.query.filter_by(
                machine_id=machine.id,
                date=today
            ).first()
            
            if record:
                record.threshold_reached = False
                record.reset_by_user_id = reset_by_user_id
                record.reset_at = datetime.utcnow()
                db.session.add(record)
                db.session.commit()
            
            logger.info(f"Sensor counter reset for {machine_name} by user {reset_by_user_id}")
            
            return jsonify({
                'status': 'success',
                'message': 'Counter reset successfully',
                'reset_by': reset_by_user_id,
                'reset_at': datetime.utcnow().isoformat()
            }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_count_reset_endpoint: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sensor_bp.route('/status/<machine_name>', methods=['GET'])
def sensor_status_endpoint(machine_name):
    """
    Get current sensor status for a machine
    Shows impulse count and maintenance due status
    """
    try:
        machine = Machine.query.filter_by(machine_name=machine_name).first()
        if not machine:
            return jsonify({'error': f'Machine {machine_name} not found'}), 404
        
        status = SensorCountManager.get_threshold_status(machine.id)
        is_due = SensorCountManager.is_maintenance_due(machine.id)
        
        return jsonify({
            'machine_name': machine_name,
            'sensor_status': status,
            'maintenance_due': is_due,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_status_endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@sensor_bp.route('/stats/<int:machine_id>', methods=['GET'])
@login_required
def sensor_stats_endpoint(machine_id):
    """
    Get sensor statistics for a machine (Dashboard)
    Shows 30-day history and trends
    """
    try:
        machine = Machine.query.get_or_404(machine_id)
        
        # Get 30-day statistics
        stats = SensorCountManager.get_machine_sensor_stats(machine_id, days=30)
        
        if not stats:
            return jsonify({'error': 'Unable to retrieve statistics'}), 500
        
        return jsonify({
            'machine': machine.machine_name,
            'machine_id': machine_id,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_stats_endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@sensor_bp.route('/display-counts/<machine_name>', methods=['GET'])
def sensor_display_counts(machine_name):
    """
    Get sensor counts for real-time display on machine status page
    Called frequently (every 2-5 minutes) to update dashboard
    """
    try:
        machine = Machine.query.filter_by(machine_code=machine_name).first()
        if not machine:
            return jsonify({'error': f'Machine {machine_name} not found'}), 404
        
        # Get today's sensor count
        today = datetime.utcnow().date()
        sensor_count = SensorCount.query.filter_by(
            machine_id=machine.id,
            date=today
        ).first()
        
        if not sensor_count:
            # Return default values if no record exists for today
            return jsonify({
                'machine_name': machine_name,
                'daily_count': 0,
                'total_count': 0,
                'threshold_value': 300000,
                'threshold_reached': False,
                'percentage_to_threshold': 0,
                'last_updated': datetime.utcnow().isoformat()
            }), 200
        
        return jsonify({
            'machine_name': machine_name,
            'daily_count': sensor_count.daily_count,
            'total_count': sensor_count.total_count,
            'threshold_value': sensor_count.threshold_value,
            'threshold_reached': sensor_count.threshold_reached,
            'percentage_to_threshold': sensor_count.percentage_to_threshold,
            'last_updated': sensor_count.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_display_counts: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# SENSOR DASHBOARD
# ============================================

@sensor_bp.route('/dashboard', methods=['GET'])
@login_required
def sensor_dashboard():
    """
    Dashboard showing sensor/impulse tracking for all machines
    Displays preventive maintenance status and alerts
    """
    try:
        user = User.query.get(session['user_id'])
        machines = Machine.query.filter_by(status='active').all()
        
        machine_sensor_data = []
        for machine in machines:
            status = SensorCountManager.get_threshold_status(machine.id)
            is_due = SensorCountManager.is_maintenance_due(machine.id)
            
            machine_sensor_data.append({
                'machine': machine,
                'status': status,
                'maintenance_due': is_due
            })
        
        return render_template(
            'sensor/dashboard.html',
            machine_data=machine_sensor_data,
            user=user
        )
        
    except Exception as e:
        logger.error(f"Error in sensor_dashboard: {e}")
        return render_template('error.html', error='Unable to load sensor dashboard'), 500


# ============================================
# PREVENTIVE MAINTENANCE ALERT API
# ============================================

@sensor_bp.route('/preventive_maintenance_alert/<machine_name>', methods=['POST'])
def preventive_maintenance_alert_endpoint(machine_name):
    """
    Create alert when preventive maintenance threshold is reached
    This is called from the Raspberry Pi when counter exceeds threshold
    """
    try:
        data = request.get_json() or {}
        start_comment = data.get('start_comment', 'Sensor threshold reached')
        
        machine = Machine.query.filter_by(machine_name=machine_name).first()
        if not machine:
            return jsonify({'error': f'Machine {machine_name} not found'}), 404
        
        # Log the alert event
        event = MachineEvent(
            machine_id=machine.id,
            machine_name=machine_name,
            event_type='preventive_maintenance_alert',
            event_status='alert',
            start_comment=start_comment,
            event_start_time=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.warning(f"PREVENTIVE MAINTENANCE ALERT for {machine_name}: {start_comment}")
        
        return jsonify({
            'status': 'success',
            'message': 'Preventive maintenance alert recorded',
            'event_id': event.id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in preventive_maintenance_alert_endpoint: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================
# SENSOR DATA VISUALIZATION
# ============================================

@sensor_bp.route('/chart-data/<int:machine_id>', methods=['GET'])
@login_required
def sensor_chart_data(machine_id):
    """
    Get sensor count data for chart visualization
    Returns daily impulse counts for the last 30 days
    """
    try:
        machine = Machine.query.get_or_404(machine_id)
        
        stats = SensorCountManager.get_machine_sensor_stats(machine_id, days=30)
        
        if not stats or not stats['records']:
            return jsonify({
                'labels': [],
                'data': [],
                'threshold': 300000
            }), 200
        
        # Format for chart.js
        records = sorted(stats['records'], key=lambda x: x[0])
        
        return jsonify({
            'labels': [item[0] for item in records],
            'data': [item[1] for item in records],
            'threshold': 300000,
            'average': stats['daily_average'],
            'total': stats['total_impulses']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in sensor_chart_data: {e}")
        return jsonify({'error': str(e)}), 500
