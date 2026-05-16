"""
Impulse/Sensor Detection Module
Handles movement detection, counting, and preventive maintenance alerts
"""

import logging
from datetime import datetime, timedelta
from app.models import db, Machine, SensorCount
import requests
import json

logger = logging.getLogger(__name__)


class ImpulseDetector:
    """
    Manages impulse/movement detection and sensor counting for preventive maintenance
    """
    
    def __init__(self, machine_name, threshold=300000, flush_interval=5.0):
        """
        Initialize impulse detector
        
        Args:
            machine_name: Name/ID of the machine
            threshold: Sensor count threshold that triggers preventive maintenance alert
            flush_interval: Seconds between server sync operations
        """
        self.machine_name = machine_name
        self.threshold = threshold
        self.flush_interval = flush_interval
        self.pending_count = 0
        self.last_flush = datetime.utcnow()
        self.total_count = 0
        self.alert_active = False
        
    def record_impulse(self):
        """Record a single impulse/movement detection"""
        self.pending_count += 1
        logger.info(f"Impulse recorded for {self.machine_name}. Pending count: {self.pending_count}")
        
    def should_flush(self):
        """Check if buffered counts should be flushed to server"""
        elapsed = (datetime.utcnow() - self.last_flush).total_seconds()
        return elapsed >= self.flush_interval and self.pending_count > 0
    
    def flush_counts_async(self):
        """Flush buffered sensor counts to the main server"""
        if self.pending_count <= 0:
            return
            
        count_to_send = self.pending_count
        self.pending_count = 0
        self.last_flush = datetime.utcnow()
        
        # Store locally in database
        self._store_sensor_count(count_to_send)
        
        logger.info(f"Flushed {count_to_send} sensor counts for {self.machine_name}")
        return count_to_send
    
    def _store_sensor_count(self, increment):
        """Store sensor count in database"""
        try:
            machine = Machine.query.filter_by(machine_name=self.machine_name).first()
            if not machine:
                logger.warning(f"Machine {self.machine_name} not found in database")
                return
            
            # Get or create sensor count record for today
            today = datetime.utcnow().date()
            sensor_record = SensorCount.query.filter_by(
                machine_id=machine.id,
                date=today
            ).first()
            
            if not sensor_record:
                sensor_record = SensorCount(
                    machine_id=machine.id,
                    date=today,
                    daily_count=increment,
                    total_count=self.total_count + increment
                )
            else:
                sensor_record.daily_count += increment
                sensor_record.total_count = self.total_count + increment
                sensor_record.updated_at = datetime.utcnow()
            
            self.total_count += increment
            
            # Check if threshold is reached
            if self.total_count >= self.threshold and not self.alert_active:
                self.alert_active = True
                sensor_record.threshold_reached = True
                logger.warning(
                    f"PREVENTIVE MAINTENANCE THRESHOLD REACHED for {self.machine_name} "
                    f"at {self.total_count} impulses"
                )
            
            db.session.add(sensor_record)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing sensor count: {e}")
            db.session.rollback()
    
    def reset_counter(self, reset_by_user_id=None):
        """Reset sensor counter after preventive maintenance completion"""
        try:
            machine = Machine.query.filter_by(machine_name=self.machine_name).first()
            if not machine:
                logger.warning(f"Machine {self.machine_name} not found")
                return False
            
            # Create reset record
            today = datetime.utcnow().date()
            sensor_record = SensorCount.query.filter_by(
                machine_id=machine.id,
                date=today
            ).first()
            
            if sensor_record:
                sensor_record.threshold_reached = False
                sensor_record.reset_by_user_id = reset_by_user_id
                sensor_record.reset_at = datetime.utcnow()
                db.session.add(sensor_record)
                db.session.commit()
            
            self.total_count = 0
            self.alert_active = False
            self.pending_count = 0
            
            logger.info(f"Sensor counter reset for {self.machine_name} by user {reset_by_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting sensor counter: {e}")
            db.session.rollback()
            return False
    
    def get_status(self):
        """Get current impulse detection status"""
        return {
            'machine_name': self.machine_name,
            'total_count': self.total_count,
            'pending_count': self.pending_count,
            'threshold': self.threshold,
            'threshold_reached': self.alert_active,
            'percentage': (self.total_count / self.threshold * 100) if self.threshold > 0 else 0,
            'last_flush': self.last_flush.isoformat()
        }


class SensorCountManager:
    """
    Manages sensor counts for preventive maintenance reporting
    """
    
    @staticmethod
    def get_machine_sensor_stats(machine_id, days=30):
        """
        Get sensor statistics for a machine over a period
        
        Args:
            machine_id: Machine ID
            days: Number of days to look back
            
        Returns:
            Dictionary with sensor statistics
        """
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).date()
            
            records = SensorCount.query.filter(
                SensorCount.machine_id == machine_id,
                SensorCount.date >= start_date
            ).order_by(SensorCount.date.desc()).all()
            
            if not records:
                return {
                    'total_impulses': 0,
                    'daily_average': 0,
                    'threshold': 300000,
                    'threshold_reached': False,
                    'days_tracked': 0,
                    'trend': []
                }
            
            total_impulses = sum(r.daily_count for r in records)
            daily_average = total_impulses / len(records) if records else 0
            latest = records[0]
            
            # Calculate trend (last 7 days vs previous 7 days)
            recent = records[:7]
            previous = records[7:14]
            recent_sum = sum(r.daily_count for r in recent)
            previous_sum = sum(r.daily_count for r in previous) if previous else recent_sum
            trend_increase = ((recent_sum - previous_sum) / previous_sum * 100) if previous_sum > 0 else 0
            
            return {
                'total_impulses': total_impulses,
                'daily_average': round(daily_average, 2),
                'threshold': latest.total_count if latest else 0,
                'threshold_reached': latest.threshold_reached if latest else False,
                'days_tracked': len(records),
                'trend_increase_percent': round(trend_increase, 2),
                'records': [(r.date.isoformat(), r.daily_count) for r in records]
            }
            
        except Exception as e:
            logger.error(f"Error getting sensor stats: {e}")
            return None
    
    @staticmethod
    def get_threshold_status(machine_id):
        """Get current threshold status for a machine"""
        try:
            today = datetime.utcnow().date()
            record = SensorCount.query.filter_by(
                machine_id=machine_id,
                date=today
            ).first()
            
            if not record:
                return {
                    'threshold_reached': False,
                    'total_count': 0,
                    'percentage': 0,
                    'days_since_last_reset': None
                }
            
            # Calculate days since last reset
            days_since_reset = None
            if record.reset_at:
                days_since_reset = (datetime.utcnow() - record.reset_at).days
            
            return {
                'threshold_reached': record.threshold_reached,
                'total_count': record.total_count,
                'percentage': (record.total_count / 300000 * 100) if record.total_count < 300000 else 100,
                'days_since_last_reset': days_since_reset,
                'last_updated': record.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting threshold status: {e}")
            return None
    
    @staticmethod
    def log_impulse_detection(machine_id, count=1, timestamp=None):
        """
        Log impulse detection event
        
        Args:
            machine_id: Machine ID
            count: Number of impulses
            timestamp: When the impulse occurred (defaults to now)
        """
        if not timestamp:
            timestamp = datetime.utcnow()
        
        try:
            machine = Machine.query.get(machine_id)
            if not machine:
                logger.warning(f"Machine {machine_id} not found")
                return False
            
            date = timestamp.date()
            record = SensorCount.query.filter_by(
                machine_id=machine_id,
                date=date
            ).first()
            
            if not record:
                record = SensorCount(
                    machine_id=machine_id,
                    date=date,
                    daily_count=count,
                    total_count=count
                )
            else:
                record.daily_count += count
                record.total_count += count
                record.updated_at = timestamp
            
            db.session.add(record)
            db.session.commit()
            
            logger.info(f"Logged {count} impulse(s) for machine {machine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging impulse detection: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def is_maintenance_due(machine_id):
        """
        Check if preventive maintenance is due based on impulse threshold
        
        Returns:
            Dictionary with maintenance status
        """
        try:
            status = SensorCountManager.get_threshold_status(machine_id)
            if not status:
                return {'maintenance_due': False, 'reason': 'No sensor data'}
            
            if status['threshold_reached']:
                return {
                    'maintenance_due': True,
                    'reason': 'Impulse threshold reached',
                    'current_count': status['total_count'],
                    'threshold': 300000,
                    'percentage': status['percentage']
                }
            
            return {
                'maintenance_due': False,
                'reason': 'Below threshold',
                'current_count': status['total_count'],
                'threshold': 300000,
                'percentage': status['percentage']
            }
            
        except Exception as e:
            logger.error(f"Error checking maintenance due: {e}")
            return {'maintenance_due': False, 'reason': 'Error checking status'}
