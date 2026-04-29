from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from app.models import db, Material, Machine, MaintenanceSchedule, SparePartsDemand, StockAlert, User, MaterialReturn, Zone, MaintenanceReport, StockMovement, PreventiveMaintenanceExecution, PreventiveMaintenanceTaskExecution, MachineStatus
from app.routes.auth import login_required, role_required
from app.email_service import EmailService
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logger = logging.getLogger('MaintenanceAPI')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Redirect based on role
        if user.role in ['admin', 'supervisor']:
            return redirect(url_for('main.dashboard'))
        else:
            # Technician and stock agents go to stock inventory
            return redirect(url_for('stock.inventory'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Define all available modules with role-based access
    modules = {
        'stock': {
            'title': 'Stock Management',
            'icon': 'box',
            'description': 'Manage inventory and materials',
            'url': 'stock.inventory',
            'roles': ['admin', 'stock_agent', 'supervisor', 'technician'],
            'color': '#3b82f6'
        },
        'maintenance': {
            'title': 'Preventive Maintenance Plan',
            'icon': 'tools',
            'description': 'View maintenance calendar for all machines and zones',
            'url': 'preventive.calendar_view',
            'roles': ['admin', 'supervisor', 'technician'],
            'color': '#10b981'
        },
        'demands': {
            'title': 'Spare Parts Demands',
            'icon': 'cart-check',
            'description': 'Request and approve parts',
            'url': 'demands.list_demands',
            'roles': ['admin', 'supervisor', 'technician', 'stock_agent'],
            'color': '#f59e0b'
        },
        'alerts': {
            'title': 'Stock Alerts',
            'icon': 'bell',
            'description': 'View stock level alerts',
            'url': 'stock.stock_alerts',
            'roles': ['admin', 'stock_agent', 'supervisor'],
            'color': '#ef4444'
        },
        'materials': {
            'title': 'Add Material',
            'icon': 'plus-circle',
            'description': 'Add new inventory items',
            'url': 'stock.add_material',
            'roles': ['admin', 'stock_agent'],
            'color': '#8b5cf6'
        },
        'user_management': {
            'title': 'User Management',
            'icon': 'people',
            'description': 'Manage system users and permissions',
            'url': 'auth.list_users',
            'roles': ['admin'],
            'color': '#ec4899'
        }
        ,
        'maintenance_kpis': {
            'title': 'Maintenance KPIs',
            'icon': 'bar-chart-line',
            'description': 'Key performance indicators for maintenance (Admin & Supervisor)',
            'url': 'main.maintenance_kpis',
            'roles': ['admin', 'supervisor'],
            'color': '#0ea5a4'
        },
        'stock_kpis': {
            'title': 'Stock KPIs',
            'icon': 'graph-up',
            'description': 'Inventory & stock KPIs (Admin, Supervisor, Stock Agent)',
            'url': 'main.stock_kpis',
            'roles': ['admin', 'supervisor', 'stock_agent'],
            'color': '#f97316'
        },
        'machine_status': {
            'title': 'Machine Status Monitor',
            'icon': 'heartbeat',
            'description': 'Real-time machine status and events',
            'url': 'main.machine_status_view',
            'roles': ['admin', 'supervisor', 'technician'],
            'color': '#06b6d4'
        },
        'preventive_reports': {
            'title': 'Maintenance Reports',
            'icon': 'clipboard-list',
            'description': 'View preventive maintenance execution reports',
            'url': 'main.preventive_reports_view',
            'roles': ['admin', 'supervisor', 'technician'],
            'color': '#14b8a6'
        }
    }
    
    # Process modules based on user role
    accessible_modules = []
    restricted_modules = []
    
    for module_key, module_data in modules.items():
        module_copy = module_data.copy()
        module_copy['key'] = module_key
        module_copy['is_accessible'] = user.role in module_data['roles']
        
        if module_copy['is_accessible']:
            accessible_modules.append(module_copy)
        else:
            restricted_modules.append(module_copy)
    
    all_modules = accessible_modules + restricted_modules
    
    # Get statistics based on user role
    total_machines = Machine.query.filter_by(status='active').count()
    
    # Maintenance schedules
    upcoming_maintenance = MaintenanceSchedule.query.filter(
        MaintenanceSchedule.scheduled_date >= datetime.now().date(),
        MaintenanceSchedule.status.in_(['scheduled', 'overdue'])
    ).count()
    
    overdue_maintenance = MaintenanceSchedule.query.filter(
        MaintenanceSchedule.scheduled_date < datetime.now().date(),
        MaintenanceSchedule.status == 'scheduled'
    ).count()
    
    # Pending demands
    pending_demands = SparePartsDemand.query.filter(
        SparePartsDemand.demand_status.in_(['pending', 'supervisor_review', 'stock_agent_review'])
    ).count()
    
    # Stock alerts - only for authorized roles
    stock_alerts = 0
    if user.role in ['admin', 'supervisor', 'stock_agent']:
        stock_alerts = StockAlert.query.filter_by(is_read=False).count()
    
    # Critical materials
    critical_materials = Material.query.filter(
        Material.current_stock <= Material.min_stock
    ).count()
    
    # Get recent activities
    recent_demands = SparePartsDemand.query.order_by(
        SparePartsDemand.created_at.desc()
    ).limit(5).all()
    
    recent_maintenance = MaintenanceSchedule.query.order_by(
        MaintenanceSchedule.created_at.desc()
    ).limit(5).all()
    
    # Preventive maintenance executions
    pending_executions = PreventiveMaintenanceExecution.query.filter_by(
        status='pending'
    ).count()
    
    in_progress_executions = PreventiveMaintenanceExecution.query.filter_by(
        status='in_progress'
    ).count()
    
    stats = {
        'total_machines': total_machines,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'pending_demands': pending_demands,
        'stock_alerts': stock_alerts,
        'critical_materials': critical_materials,
        'pending_executions': pending_executions,
        'in_progress_executions': in_progress_executions
    }
    
    return render_template(
        'main/dashboard.html',
        user=user,
        stats=stats,
        modules=all_modules,
        recent_demands=recent_demands,
        recent_maintenance=recent_maintenance,
        stock_alerts_count=stock_alerts
    )


@main_bp.route('/maintenance-kpis')
@login_required
@role_required('admin', 'supervisor')
def maintenance_kpis():
    """Compute maintenance KPIs for selected date range (defaults to last 30 days)"""
    from sqlalchemy import func
    # Date range
    end_date = request.args.get('end_date')
    start_date = request.args.get('start_date')
    if end_date and start_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            start = datetime.strptime(start_date, '%Y-%m-%d')
        except Exception:
            end = datetime.utcnow()
            start = end - timedelta(days=30)
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=30)

    # KPIs
    total_events = MaintenanceReport.query.filter(MaintenanceReport.created_at.between(start, end)).count()
    total_downtime_hours = db.session.query(func.coalesce(func.sum(MaintenanceReport.actual_duration_hours), 0)).filter(MaintenanceReport.created_at.between(start, end)).scalar() or 0
    canceled_events = MaintenanceReport.query.filter(MaintenanceReport.report_status == 'rejected', MaintenanceReport.created_at.between(start, end)).count()
    avg_downtime_seconds = (total_downtime_hours / total_events * 3600) if total_events > 0 else 0
    operational_hours = (end - start).total_seconds() / 3600
    availability_rate = (1 - (total_downtime_hours / operational_hours)) * 100 if operational_hours > 0 else 0
    availability_rate = max(0, min(100, availability_rate))
    failure_rate = (canceled_events / total_downtime_hours) if total_downtime_hours > 0 else 0
    mttr_seconds = (db.session.query(func.avg(MaintenanceReport.actual_duration_hours)).filter(MaintenanceReport.created_at.between(start, end), MaintenanceReport.actual_duration_hours.isnot(None)).scalar() or 0) * 3600
    mtbf_hours = ((end - start).days * 24 / canceled_events) if canceled_events > 0 else 0

    # Most common event type
    most_common = db.session.query(MaintenanceReport.report_type, func.count(MaintenanceReport.id).label('cnt')).filter(MaintenanceReport.created_at.between(start, end)).group_by(MaintenanceReport.report_type).order_by(func.count(MaintenanceReport.id).desc()).first()
    most_common_type = most_common.report_type if most_common else None

    # Most active user
    most_active = db.session.query(User.first_name, User.last_name, func.count(MaintenanceReport.id).label('cnt')).join(MaintenanceReport, User.id == MaintenanceReport.technician_id).filter(MaintenanceReport.created_at.between(start, end)).group_by(User.id).order_by(func.count(MaintenanceReport.id).desc()).first()

    # Events per machine
    events_per_machine = db.session.query(MaintenanceReport.machine_name, func.count(MaintenanceReport.id).label('cnt'), func.coalesce(func.sum(MaintenanceReport.actual_duration_hours), 0).label('total_hours')).filter(MaintenanceReport.created_at.between(start, end)).group_by(MaintenanceReport.machine_name).order_by(func.count(MaintenanceReport.id).desc()).limit(10).all()

    # Prepare chart data
    machine_labels = [m.machine_name for m in events_per_machine]
    machine_counts = [m.cnt for m in events_per_machine]

    # Report status distribution
    status_stats = db.session.query(MaintenanceReport.report_status, func.count(MaintenanceReport.id).label('cnt')).filter(MaintenanceReport.created_at.between(start, end)).group_by(MaintenanceReport.report_status).all()
    status_labels = [s.report_status for s in status_stats]
    status_counts = [s.cnt for s in status_stats]

    context = {
        'start': start,
        'end': end,
        'total_events': total_events,
        'total_downtime_hours': round(total_downtime_hours, 2),
        'canceled_events': canceled_events,
        'avg_downtime_seconds': int(avg_downtime_seconds),
        'availability_rate': round(availability_rate, 2),
        'failure_rate': round(failure_rate, 4),
        'mttr_seconds': int(mttr_seconds),
        'mtbf_hours': round(mtbf_hours, 2),
        'most_common_type': most_common_type,
        'most_active': most_active,
        'events_per_machine': events_per_machine
        , 'machine_labels': machine_labels, 'machine_counts': machine_counts,
        'status_labels': status_labels, 'status_counts': status_counts
    }

    return render_template('main/maintenance_kpis.html', **context)


# ============================================
# CORRECTIVE MAINTENANCE ITEMS
# ============================================
CORRECTIVE_MAINTENANCE_ITEMS = [
    # Mechanical (Mechanical)
    {'id': 'corr_001', 'name': 'Change fitted collar ear', 'category': 'Mechanical'},
    {'id': 'corr_002', 'name': 'Adjust straightening unit', 'category': 'Mechanical'},
    {'id': 'corr_003', 'name': 'Change roller', 'category': 'Mechanical'},
    {'id': 'corr_004', 'name': 'Adjust wire drive', 'category': 'Mechanical'},
    {'id': 'corr_005', 'name': 'Change toothed belts', 'category': 'Mechanical'},
    {'id': 'corr_006', 'name': 'Change measurement wheel', 'category': 'Mechanical'},
    {'id': 'corr_007', 'name': 'Change toothed wheels (Z32)', 'category': 'Mechanical'},
    {'id': 'corr_008', 'name': 'Change toothed wheels (Z18)', 'category': 'Mechanical'},
    {'id': 'corr_009', 'name': 'Change pressure roller', 'category': 'Mechanical'},
    {'id': 'corr_010', 'name': 'Change protective cover', 'category': 'Mechanical'},
    {'id': 'corr_011', 'name': 'Adjust measurement wheel', 'category': 'Mechanical'},
    {'id': 'corr_012', 'name': 'Change cable guide', 'category': 'Mechanical'},
    {'id': 'corr_013', 'name': 'Changement axe d\'encodeur', 'category': 'Mechanical'},
    {'id': 'corr_014', 'name': 'Change grooved bearing', 'category': 'Mechanical'},
    {'id': 'corr_015', 'name': 'Adjust jaws', 'category': 'Mechanical'},
    {'id': 'corr_016', 'name': 'Change jaws', 'category': 'Mechanical'},
    {'id': 'corr_017', 'name': 'Change Pivot CPL', 'category': 'Mechanical'},
    {'id': 'corr_018', 'name': 'Vérification bloc de lames après 150.000 coupes', 'category': 'Mechanical'},
    {'id': 'corr_019', 'name': 'Change stripping blades', 'category': 'Mechanical'},
    {'id': 'corr_020', 'name': 'Change cutting blades', 'category': 'Mechanical'},
    {'id': 'corr_021', 'name': 'Adjust cutting head', 'category': 'Mechanical'},
    {'id': 'corr_022', 'name': 'Changement tole bloc d\'arret', 'category': 'Mechanical'},
    {'id': 'corr_023', 'name': 'Change centering guide plate (V-centering)', 'category': 'Mechanical'},
    {'id': 'corr_024', 'name': 'Change guide plate cylinder', 'category': 'Mechanical'},
    {'id': 'corr_025', 'name': 'Change CPL support', 'category': 'Mechanical'},
    {'id': 'corr_026', 'name': 'Change fixing lever', 'category': 'Mechanical'},
    {'id': 'corr_027', 'name': 'Change tool fixing sleeve', 'category': 'Mechanical'},
    {'id': 'corr_028', 'name': 'Change band cutter', 'category': 'Mechanical'},
    {'id': 'corr_029', 'name': 'Change band cutting blade', 'category': 'Mechanical'},
    {'id': 'corr_030', 'name': 'Change band cutter housing', 'category': 'Mechanical'},
    {'id': 'corr_031', 'name': 'Change band cutter joint', 'category': 'Mechanical'},
    {'id': 'corr_032', 'name': 'Change band cutter piston', 'category': 'Mechanical'},
    {'id': 'corr_033', 'name': 'Change front roller', 'category': 'Mechanical'},
    {'id': 'corr_034', 'name': 'Change rear roller', 'category': 'Mechanical'},
    {'id': 'corr_035', 'name': 'Adjust tensioner', 'category': 'Mechanical'},
    {'id': 'corr_036', 'name': 'Change front plate', 'category': 'Mechanical'},
    {'id': 'corr_037', 'name': 'Change rear plate', 'category': 'Mechanical'},
    {'id': 'corr_038', 'name': 'Reglage tapis transporteuse', 'category': 'Mechanical'},
    {'id': 'corr_039', 'name': 'Rinse and center IMS', 'category': 'Mechanical'},
    {'id': 'corr_040', 'name': 'Adjust K26', 'category': 'Mechanical'},
    {'id': 'corr_041', 'name': 'Pb unitée d\'entrainement', 'category': 'Mechanical'},
    {'id': 'corr_042', 'name': 'Centrage d\'applicateur seal', 'category': 'Mechanical'},
    {'id': 'corr_043', 'name': 'Change vibrator', 'category': 'Mechanical'},
    {'id': 'corr_044', 'name': 'Reglage vibration seal', 'category': 'Mechanical'},
    {'id': 'corr_045', 'name': 'Change chuck', 'category': 'Mechanical'},
    {'id': 'corr_046', 'name': 'Change dornpin', 'category': 'Mechanical'},
    {'id': 'corr_047', 'name': 'Adjust Touniquer', 'category': 'Mechanical'},
    {'id': 'corr_048', 'name': 'Ajustement tete d\'insertion', 'category': 'Mechanical'},
    {'id': 'corr_049', 'name': 'Patinage', 'category': 'Mechanical'},
    {'id': 'corr_050', 'name': 'Adjust band cutter', 'category': 'Mechanical'},
    {'id': 'corr_051', 'name': 'Adjust stripping variation', 'category': 'Mechanical'},
    {'id': 'corr_052', 'name': 'Adjust centering V-block', 'category': 'Mechanical'},
    {'id': 'corr_053', 'name': 'Réparation tole bloc d\'arrét', 'category': 'Mechanical'},
    {'id': 'corr_054', 'name': 'Change insertion sleeve', 'category': 'Mechanical'},
    {'id': 'corr_055', 'name': 'Adjust paper reel', 'category': 'Mechanical'},
    {'id': 'corr_056', 'name': 'Adjust pivot arm side 1', 'category': 'Mechanical'},
    {'id': 'corr_057', 'name': 'Adjust pivot arm side 2', 'category': 'Mechanical'},
    {'id': 'corr_058', 'name': 'Change seal sleeve', 'category': 'Mechanical'},
    {'id': 'corr_059', 'name': 'Adjust conveyor', 'category': 'Mechanical'},
    {'id': 'corr_060', 'name': 'Adjust retractable chute', 'category': 'Mechanical'},
    {'id': 'corr_061', 'name': 'Calibrage machine de traction', 'category': 'Mechanical'},
    {'id': 'corr_062', 'name': 'Adjust conveyor belt', 'category': 'Mechanical'},
    {'id': 'corr_063', 'name': 'Reglage unité de torsadage (twist)', 'category': 'Mechanical'},
    {'id': 'corr_064', 'name': 'Module d\'orientation', 'category': 'Mechanical'},
    {'id': 'corr_065', 'name': 'Replace double joint sealing station', 'category': 'Mechanical'},
    {'id': 'corr_066', 'name': 'Probleme unité bandage sigma', 'category': 'Mechanical'},
    {'id': 'corr_067', 'name': 'Probleme gulotte rettractable', 'category': 'Mechanical'},
    
    # Electrical (Electrical)
    {'id': 'corr_101', 'name': 'Change encoder', 'category': 'Electrical'},
    {'id': 'corr_102', 'name': 'Adjust micro switch', 'category': 'Electrical'},
    {'id': 'corr_103', 'name': 'Change micro switch', 'category': 'Electrical'},
    {'id': 'corr_104', 'name': 'Change ACS116 (servomotor)', 'category': 'Electrical'},
    {'id': 'corr_105', 'name': 'Change gripper sensor', 'category': 'Electrical'},
    {'id': 'corr_106', 'name': 'Change linear movement sensor', 'category': 'Electrical'},
    {'id': 'corr_107', 'name': 'Change rotational movement sensor', 'category': 'Electrical'},
    {'id': 'corr_108', 'name': 'Change motor', 'category': 'Electrical'},
    {'id': 'corr_109', 'name': 'Change ACS108', 'category': 'Electrical'},
    {'id': 'corr_110', 'name': 'Change optical detector guide plate', 'category': 'Electrical'},
    {'id': 'corr_111', 'name': 'Changement Barrage photoelectrique d\'enrouleur papier', 'category': 'Electrical'},
    {'id': 'corr_112', 'name': 'Adjust MCD', 'category': 'Electrical'},
    {'id': 'corr_113', 'name': 'Adjust pivot arm sensor side 1', 'category': 'Electrical'},
    {'id': 'corr_114', 'name': 'Adjust pivot arm sensor side 2', 'category': 'Electrical'},
    {'id': 'corr_115', 'name': 'Reglage capteur de présence seal', 'category': 'Electrical'},
    {'id': 'corr_116', 'name': 'Change seal presence sensor', 'category': 'Electrical'},
    {'id': 'corr_117', 'name': 'Reglage SPM', 'category': 'Electrical'},
    {'id': 'corr_118', 'name': 'Change retractable chute sensor', 'category': 'Electrical'},
    {'id': 'corr_119', 'name': 'Probléme ACS116 (servomoteur)', 'category': 'Electrical'},
    {'id': 'corr_120', 'name': 'Probléme ACS108 (servomoteur)', 'category': 'Electrical'},
    {'id': 'corr_121', 'name': 'Probléme ACS204 (servomoteur)', 'category': 'Electrical'},
    {'id': 'corr_122', 'name': 'Change ACS204 (servomotor)', 'category': 'Electrical'},
    {'id': 'corr_123', 'name': 'Problème servoregulateur', 'category': 'Electrical'},
    {'id': 'corr_124', 'name': 'Change MCI RG45 cable', 'category': 'Electrical'},
    {'id': 'corr_125', 'name': 'Change sensor cable', 'category': 'Electrical'},
    
    # IT/Software
    {'id': 'corr_201', 'name': 'Update ACS 116', 'category': 'IT/Software'},
    {'id': 'corr_202', 'name': 'Zero positioning', 'category': 'IT/Software'},
    {'id': 'corr_203', 'name': 'Update ACS 108', 'category': 'IT/Software'},
    {'id': 'corr_204', 'name': 'Press calibration', 'category': 'IT/Software'},
    {'id': 'corr_205', 'name': 'Press zero positioning', 'category': 'IT/Software'},
    {'id': 'corr_206', 'name': 'Adjust and calibrate SQC', 'category': 'IT/Software'},
    {'id': 'corr_207', 'name': 'CAD installation', 'category': 'IT/Software'},
    {'id': 'corr_208', 'name': 'Topwin installation', 'category': 'IT/Software'},
    {'id': 'corr_209', 'name': 'Camera installation', 'category': 'IT/Software'},
    {'id': 'corr_210', 'name': 'Topwin issue', 'category': 'IT/Software'},
    
    # Pneumatic (Pneumatic)
    {'id': 'corr_301', 'name': 'Reglage pneumatique d\'applicateur seal', 'category': 'Pneumatic'},
]


@main_bp.route('/maintenance-report', methods=['GET', 'POST'])
@login_required
@role_required('technician')
def maintenance_report_card():
    """Display and handle the maintenance report card"""
    user = User.query.get(session['user_id'])
    
    # Handle AJAX auto-save of task data
    if request.method == 'POST' and request.is_json:
        try:
            data = request.get_json()
            task_num = data.get('task_num')
            report_id = data.get('report_id')
            action = data.get('action')  # 'start' or 'stop'
            duration = data.get('duration', 0)
            status = data.get('status')
            remarks = data.get('remarks')
            
            # Get or create maintenance report
            if report_id:
                report = MaintenanceReport.query.get(report_id)
            else:
                report = MaintenanceReport()
                report.technician_id = user.id
                report.machine_name = data.get('machine_name', 'Unknown')
                report.report_status = 'draft'
                report.created_at = datetime.utcnow()
                db.session.add(report)
                db.session.flush()
                report_id = report.id
            
            # Update task execution data
            if report_id and task_num:
                # Store task data in JSON format in checklist_data
                if not report.checklist_data:
                    checklist = {}
                else:
                    try:
                        import json
                        checklist = json.loads(report.checklist_data)
                    except:
                        checklist = {}
                
                task_key = f'task_{task_num}'
                if task_key not in checklist:
                    checklist[task_key] = {}
                
                checklist[task_key]['status'] = status or '-'
                checklist[task_key]['duration'] = duration
                checklist[task_key]['remarks'] = remarks or ''
                if action == 'start':
                    checklist[task_key]['start_time'] = datetime.utcnow().isoformat()
                elif action == 'stop':
                    checklist[task_key]['end_time'] = datetime.utcnow().isoformat()
                    checklist[task_key]['duration'] = duration
                
                report.checklist_data = json.dumps(checklist)
                report.updated_at = datetime.utcnow()
                db.session.commit()
                
                return {'success': True, 'report_id': report_id, 'message': f'Task {task_num} saved'}
            
            return {'success': False, 'message': 'Invalid task data'}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error saving task data: {str(e)}')
            return {'success': False, 'message': str(e)}, 400
    
    # Handle final form submission
    if request.method == 'POST' and not request.is_json:
        try:
            logger.info("=" * 80)
            logger.info("MAINTENANCE REPORT SAVE PROCESS STARTED")
            logger.info("=" * 80)
            
            report_id = request.form.get('report_id')
            logger.info(f"Processing report - Report ID: {report_id if report_id else 'NEW'}")
            
            # Get existing report or create new
            if report_id:
                try:
                    report = MaintenanceReport.query.get(int(report_id))
                    logger.info(f"Found existing report: {report_id}")
                except:
                    report = None
                    logger.warning(f"Could not find report with ID: {report_id}")
            else:
                report = None
            
            if not report:
                report = MaintenanceReport()
                report.technician_id = user.id
                report.report_status = 'draft'
                report.created_at = datetime.utcnow()
                logger.info(f"Creating new maintenance report for technician: {user.full_name} (ID: {user.id})")
            
            # Update report with form data
            machine_id = request.form.get('machine_id')
            if machine_id:
                machine = Machine.query.get(int(machine_id))
                if machine:
                    report.machine_name = machine.name
                    logger.info(f"Machine assigned: {machine.name}")
            
            report.work_description = request.form.get('equipment', '')
            report.technician_zone = request.form.get('serial_number', '')
            report.environmental_conditions = request.form.get('inventory_number', '')
            report.safety_observations = request.form.get('technician_observations', '')
            report.report_status = 'submitted'
            report.actual_end_time = datetime.utcnow()
            report.updated_at = datetime.utcnow()
            
            logger.info(f"Report data populated - Status: {report.report_status}")
            
            # Save to database
            db.session.add(report)
            db.session.commit()
            logger.info(f"✓ Report SAVED to database - Report ID: {report.id}")
            
            # Find supervisor and send email with PDF
            supervisor = user.supervisor
            if supervisor and supervisor.email:
                logger.info(f"Attempting to send email to supervisor: {supervisor.full_name} ({supervisor.email})")
                
                try:
                    # Generate PDF HTML
                    pdf_html = render_template(
                        'maintenance_report_card.html',
                        report=report,
                        current_user=user
                    )
                    
                    logger.info("PDF HTML template rendered successfully")
                    
                    # Send report to supervisor
                    email_sent = EmailService.send_maintenance_report_to_supervisor(
                        report=report,
                        supervisor=supervisor,
                        pdf_html=pdf_html,
                        report_type='corrective'
                    )
                    
                    if email_sent:
                        logger.info(f"✓ Email SENT to supervisor successfully - Report ID: {report.id}")
                    else:
                        logger.warning(f"Email sending returned False for Report ID: {report.id}")
                        
                except Exception as email_error:
                    logger.error(f"✗ Failed to send email to supervisor: {type(email_error).__name__}: {str(email_error)}")
                    logger.error("Email sending failed but report was saved successfully")
            else:
                logger.warning(f"No supervisor found or supervisor has no email - Report will not be sent to anyone")
            
            logger.info("=" * 80)
            logger.info("MAINTENANCE REPORT SAVE PROCESS COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            flash('Maintenance report saved and sent to supervisor for approval!', 'success')
            return redirect(url_for('main.maintenance_reports_archive'))
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("MAINTENANCE REPORT SAVE PROCESS FAILED")
            logger.error("=" * 80)
            logger.error(f"✗ Error type: {type(e).__name__}")
            logger.error(f"✗ Error message: {str(e)}")
            logger.error("Full traceback:", exc_info=True)
            
            db.session.rollback()
            current_app.logger.error(f'Error submitting maintenance report: {str(e)}')
            flash(f'Error submitting report: {str(e)}', 'danger')
            return redirect(url_for('main.maintenance_report_card'))
    
    # Handle GET request (display form)
    machines = Machine.query.filter_by(status='active').all()
    
    # Check if there's a draft report to resume
    draft_report = MaintenanceReport.query.filter_by(
        technician_id=user.id,
        report_status='draft'
    ).order_by(MaintenanceReport.created_at.desc()).first()
    
    # Get unique categories for corrective maintenance
    corrective_categories = sorted(list(set([item['category'] for item in CORRECTIVE_MAINTENANCE_ITEMS])))
    
    return render_template(
        'maintenance_report_card.html',
        machines=machines,
        current_user=user,
        draft_report=draft_report,
        corrective_items=CORRECTIVE_MAINTENANCE_ITEMS,
        corrective_categories=corrective_categories
    )


@main_bp.route('/machine-status')
@login_required
@role_required('admin', 'supervisor', 'technician')
def machine_status_view():
    """Display machine status monitoring card view"""
    user = User.query.get(session['user_id'])
    machines = Machine.query.filter_by(status='active').all()
    
    # Get current status for all machines
    machine_statuses = {}
    for machine in machines:
        status = MachineStatus.query.filter_by(machine_id=machine.id).first()
        if status:
            machine_statuses[machine.id] = {
                'current_status': status.current_status,
                'status_since': status.status_since,
                'downtime_today': status.cumulative_downtime_today
            }
    
    return render_template(
        'machine_status_card_view.html',
        machines=machines,
        machine_statuses=machine_statuses,
        current_user=user
    )


@main_bp.route('/event-details/<int:event_id>')
@login_required
@role_required('admin', 'supervisor', 'technician')
def event_details(event_id):
    """Display detailed information about a specific event"""
    from app.models import MachineEvent
    
    event = MachineEvent.query.get_or_404(event_id)
    machine = Machine.query.get(event.machine_id)
    
    # Calculate additional metrics
    is_active = event.event_status == 'started'
    
    return render_template(
        'event_details.html',
        event=event,
        machine=machine,
        is_active=is_active
    )


@main_bp.route('/preventive-reports')
@login_required
@role_required('admin', 'supervisor', 'technician')
def preventive_reports_view():
    """Display preventive maintenance reports card view"""
    user = User.query.get(session['user_id'])
    
    # Get all preventive maintenance executions
    executions = PreventiveMaintenanceExecution.query.order_by(
        PreventiveMaintenanceExecution.created_at.desc()
    ).all()
    
    # Filter based on user role
    if user.role == 'technician':
        executions = [
            e for e in executions 
            if e.assigned_technician_id == user.id
        ]
    
    # Get preventive maintenance reports (newly saved from monthly/semi-annual)
    preventive_reports = MaintenanceReport.query.filter(
        MaintenanceReport.report_type == 'preventive'
    ).order_by(MaintenanceReport.created_at.desc()).all()
    
    # Filter preventive reports based on user role
    if user.role == 'technician':
        preventive_reports = [
            r for r in preventive_reports 
            if r.technician_id == user.id
        ]
    
    # Get corrective maintenance reports
    corrective_reports = MaintenanceReport.query.filter(
        MaintenanceReport.report_type.ilike('%corrective%')
    ).order_by(MaintenanceReport.created_at.desc()).all()
    
    # Filter corrective reports based on user role
    if user.role == 'technician':
        corrective_reports = [
            r for r in corrective_reports 
            if r.technician_id == user.id
        ]
    
    return render_template(
        'preventive_reports_card_view.html',
        executions=executions,
        preventive_reports=preventive_reports,
        corrective_reports=corrective_reports,
        current_user=user
    )


@main_bp.route('/new-maintenance-report', methods=['GET'])
@login_required
@role_required('technician')
def new_maintenance_report_wizard():
    """Wizard for creating a new maintenance report - Zone → Machine → Category → Type"""
    zones = Zone.query.all()
    return render_template(
        'new_report_wizard.html',
        zones=zones,
        current_user=User.query.get(session['user_id'])
    )


@main_bp.route('/api/machines-by-zone/<int:zone_id>', methods=['GET'])
@login_required
def get_machines_by_zone(zone_id):
    """API endpoint to fetch machines by zone"""
    try:
        machines = Machine.query.filter_by(zone_id=zone_id, status='active').all()
        logger.info(f"Fetching machines for zone {zone_id}: Found {len(machines)} active machines")
        response = [
            {
                'id': m.id,
                'name': m.name,
                'code': m.machine_code
            }
            for m in machines
        ]
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error fetching machines for zone {zone_id}: {str(e)}")
        return jsonify({'error': 'Failed to load machines'}), 500


@main_bp.route('/corrective-maintenance-tasks', methods=['GET', 'POST'])
@login_required
def corrective_maintenance_tasks():
    """Display corrective maintenance tasks with form interface or handle form submission"""
    user = User.query.get(session['user_id'])
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        try:
            logger.info("=" * 80)
            logger.info("CORRECTIVE MAINTENANCE REPORT SAVE PROCESS STARTED")
            logger.info("=" * 80)
            
            execution_date = request.form.get('executionDate')
            
            # Get selected machines from form (can be multiple)
            import json as json_module
            selected_machines_json = request.form.get('selected_machines', '[]')
            try:
                selected_machine_ids = json_module.loads(selected_machines_json)
            except:
                selected_machine_ids = []
            
            # Fallback to single machineSelect if multiple not found
            if not selected_machine_ids:
                single_machine_id = request.form.get('machineSelect')
                if single_machine_id:
                    selected_machine_ids = [int(single_machine_id)]
            
            if not selected_machine_ids:
                logger.warning("No machines selected for corrective maintenance report")
                flash('Please select at least one machine', 'warning')
                return redirect(url_for('main.corrective_maintenance_tasks'))
            
            logger.info(f"Processing corrective maintenance report for {len(selected_machine_ids)} machine(s), Date: {execution_date}")
            
            # Collect task data once (will apply to all machines)
            import json
            task_data = {}
            for item in CORRECTIVE_MAINTENANCE_ITEMS:
                task_id = item['id']
                check_key = f'task_{task_id}_check'
                time_key = f'task_{task_id}_time'
                remarks_key = f'task_{task_id}_remarks'
                
                # Check if task was performed (checkbox)
                is_checked = request.form.get(check_key) == '1'
                duration_str = request.form.get(time_key, '0')
                remarks = request.form.get(remarks_key, '').strip()
                
                # Convert duration to int, default to 0
                try:
                    duration = int(duration_str)
                except (ValueError, TypeError):
                    duration = 0
                
                # Only save if task was checked or has remarks
                if is_checked or remarks:
                    task_data[f'task_{task_id}'] = {
                        'name': item['name'],
                        'category': item['category'],
                        'checked': is_checked,
                        'duration': duration,
                        'remarks': remarks
                    }
            
            task_count = len(task_data)
            logger.info(f"Collected data from {task_count} corrective tasks")
            
            # Create a report for each selected machine
            reports_created = []
            for machine_id in selected_machine_ids:
                # Create new maintenance report
                report = MaintenanceReport()
                report.technician_id = user.id
                report.report_type = 'corrective'
                report.report_status = 'submitted'
                report.created_at = datetime.utcnow()
                report.actual_end_time = datetime.utcnow()
                report.updated_at = datetime.utcnow()
                
                # Get machine info
                machine = Machine.query.get(int(machine_id))
                if machine:
                    report.machine_name = machine.name
                    report.machine_id = machine.id
                    logger.info(f"Machine assigned: {machine.name} (ID: {machine.id})")
                
                # Save checklist data as JSON
                report.checklist_data = json.dumps(task_data)
                
                # Save to database
                db.session.add(report)
                db.session.flush()
                reports_created.append(report.id)
                
                logger.info(f"✓ Report created for machine {machine.name} - Report ID: {report.id}")
            
            # Commit all reports
            db.session.commit()
            logger.info(f"✓ {len(reports_created)} Corrective Maintenance Report(s) SAVED")
            
            # Send emails to supervisor for each report
            supervisor = user.supervisor
            if supervisor and supervisor.email:
                logger.info(f"Attempting to send emails to supervisor: {supervisor.full_name} ({supervisor.email})")
                
                for report_id in reports_created:
                    report = MaintenanceReport.query.get(report_id)
                    try:
                        # Generate PDF HTML
                        pdf_html = render_template(
                            'maintenance_report_card.html',
                            report=report,
                            current_user=user
                        )
                        
                        logger.info("PDF HTML template rendered successfully")
                        
                        # Send report to supervisor
                        email_sent = EmailService.send_maintenance_report_to_supervisor(
                            report=report,
                            supervisor=supervisor,
                            pdf_html=pdf_html,
                            report_type='corrective'
                        )
                        
                        if email_sent:
                            logger.info(f"✓ Email SENT to supervisor for Report ID: {report_id}")
                        else:
                            logger.warning(f"Email sending returned False for Report ID: {report_id}")
                            
                    except Exception as email_error:
                        logger.error(f"✗ Failed to send email for Report ID {report_id}: {type(email_error).__name__}: {str(email_error)}")
            else:
                logger.warning(f"No supervisor found or supervisor has no email")
            
            logger.info("=" * 80)
            logger.info(f"CORRECTIVE MAINTENANCE REPORT SAVE PROCESS COMPLETED - {len(reports_created)} report(s) created")
            logger.info("=" * 80)
            
            flash(f'Corrective maintenance report(s) saved for {len(selected_machine_ids)} machine(s) and sent to supervisor!', 'success')
            return redirect(url_for('main.maintenance_reports_archive'))
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("CORRECTIVE MAINTENANCE REPORT SAVE PROCESS FAILED")
            logger.error("=" * 80)
            logger.error(f"✗ Error type: {type(e).__name__}")
            logger.error(f"✗ Error message: {str(e)}")
            logger.error("Full traceback:", exc_info=True)
            
            db.session.rollback()
            flash(f'Error submitting corrective maintenance report: {str(e)}', 'danger')
            return redirect(url_for('main.corrective_maintenance_tasks'))
    
    # Handle GET request (display form)
    # Get active machines
    machines = Machine.query.filter_by(status='active').all()
    
    # Get machine(s) from query parameters (passed from wizard)
    machine_id_param = request.args.get('machine_id', type=int)
    machine_ids_param = request.args.get('machine_ids', '')
    
    # Build list of selected machines
    selected_machine_ids = []
    if machine_id_param:
        # Single machine from old wizard flow
        selected_machine_ids = [machine_id_param]
    elif machine_ids_param:
        # Multiple machines from new wizard flow
        try:
            selected_machine_ids = [int(m_id) for m_id in machine_ids_param.split(',') if m_id.strip()]
        except (ValueError, AttributeError):
            selected_machine_ids = []
    
    # Get unique categories from corrective items
    corrective_categories = sorted(list(set([item['category'] for item in CORRECTIVE_MAINTENANCE_ITEMS])))
    
    logger.info(f"User {user.full_name} viewing corrective maintenance tasks - {len(CORRECTIVE_MAINTENANCE_ITEMS)} items in {len(corrective_categories)} categories")
    
    return render_template(
        'corrective_maintenance_tasks.html',
        machines=machines,
        corrective_items=CORRECTIVE_MAINTENANCE_ITEMS,
        corrective_categories=corrective_categories,
        current_user=user,
        selected_machine_ids=selected_machine_ids
    )


@main_bp.route('/maintenance-reports/archive')
@login_required
def maintenance_reports_archive():
    """View archive of submitted maintenance reports"""
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    logger.info(f"Loading maintenance reports archive for user: {user.full_name} (ID: {user.id})")
    
    # Base query
    query = MaintenanceReport.query
    
    # Filter by status if specified
    if status != 'all':
        query = query.filter_by(report_status=status)
        logger.info(f"Filtering reports by status: {status}")
    
    # Filter based on user role
    if user.role == 'technician':
        query = query.filter_by(technician_id=user.id)
        logger.info(f"Filtering reports for technician")
    elif user.role == 'supervisor':
        # Supervisors see reports from their subordinates
        subordinate_ids = [s.id for s in user.subordinates]
        if subordinate_ids:
            query = query.filter(MaintenanceReport.technician_id.in_(subordinate_ids))
            logger.info(f"Filtering reports for supervisor's subordinates: {subordinate_ids}")
    
    # Order by most recent first
    reports = query.order_by(
        MaintenanceReport.updated_at.desc()
    ).paginate(page=page, per_page=20)
    
    logger.info(f"Retrieved {reports.total} total reports, showing page {page} ({len(reports.items)} items)")
    
    return render_template(
        'maintenance_reports_archive.html',
        reports=reports,
        status_filter=status,
        current_user=user
    )


@main_bp.route('/reports/<int:report_id>')
@login_required
def report_detail(report_id):
    """Display detailed view of a maintenance report"""
    report = MaintenanceReport.query.get_or_404(report_id)
    user = User.query.get(session['user_id'])
    
    # Check authorization
    # Allow: admins (all reports), supervisors (reports from their technicians), technicians (their own reports)
    is_authorized = False
    
    if user.role == 'admin':
        is_authorized = True
    elif user.role == 'supervisor' and report.technician and report.technician.supervisor_id == user.id:
        is_authorized = True
    elif report.technician_id == user.id:
        is_authorized = True
    
    if not is_authorized:
        flash('You are not authorized to view this report.', 'danger')
        return redirect(url_for('main.preventive_reports_view'))
    
    # Parse checklist data if available
    checklist_items = []
    if report.checklist_data:
        try:
            import json
            checklist_data = json.loads(report.checklist_data)
            for key, value in checklist_data.items():
                if isinstance(value, dict):
                    # Get duration and convert to minutes if needed
                    duration = value.get('duration', '0')
                    try:
                        duration_float = float(duration)
                        # If duration is > 60, it might be in seconds, convert to minutes
                        if duration_float > 60:
                            duration_minutes = round(duration_float / 60, 1)
                        else:
                            duration_minutes = duration_float
                    except (ValueError, TypeError):
                        duration_minutes = 0
                    
                    checklist_items.append({
                        'key': key,
                        'description': value.get('description', key),
                        'status': value.get('status', '-'),
                        'duration': str(duration_minutes),
                        'remarks': value.get('remarks', '')
                    })
        except (json.JSONDecodeError, TypeError):
            checklist_items = []
    
    return render_template(
        'report_detail.html',
        report=report,
        checklist_items=checklist_items,
        current_user=user
    )


@main_bp.route('/pending-approvals')
@login_required
def pending_approvals():
    """Display maintenance reports awaiting supervisor approval"""
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    
    # Allow admins and supervisors to see pending reports for their subordinates
    if user.role == 'supervisor':
        # Show reports from technicians under this supervisor
        pending_reports = MaintenanceReport.query.join(
            User, MaintenanceReport.technician_id == User.id
        ).filter(
            User.supervisor_id == user.id,
            MaintenanceReport.report_status == 'submitted'
        ).order_by(MaintenanceReport.created_at.desc()).paginate(page=page, per_page=12)
    elif user.role == 'admin':
        # Show all pending reports
        pending_reports = MaintenanceReport.query.filter(
            MaintenanceReport.report_status == 'submitted'
        ).order_by(MaintenanceReport.created_at.desc()).paginate(page=page, per_page=12)
    else:
        flash('You do not have permission to view pending approvals.', 'danger')
        return redirect(url_for('main.preventive_reports_view'))
    
    return render_template(
        'pending_approvals.html',
        reports=pending_reports,
        current_user=user
    )


@main_bp.route('/stock-kpis')
@login_required
@role_required('admin', 'supervisor', 'stock_agent')
def stock_kpis():
    """Compute stock KPIs"""
    from sqlalchemy import func
    # Date range for movement-based KPIs
    end_date = request.args.get('end_date')
    start_date = request.args.get('start_date')
    if end_date and start_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            start = datetime.strptime(start_date, '%Y-%m-%d')
        except Exception:
            end = datetime.utcnow()
            start = end - timedelta(days=30)
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=30)

    total_spare_parts = Material.query.count()
    total_stock_value = db.session.query(func.coalesce(func.sum(Material.current_stock * Material.unit_cost), 0)).scalar() or 0
    low_stock_items = Material.query.filter(Material.current_stock <= Material.min_stock).count()
    overstock_items = Material.query.filter(Material.current_stock >= Material.max_stock).count()
    critical_items = Material.query.filter((Material.current_stock == 0) | (Material.current_stock <= Material.reorder_point)).count()
    avg_stock_level = (db.session.query(func.coalesce(func.avg(Material.current_stock), 0)).scalar() or 0)
    stock_in = db.session.query(func.coalesce(func.sum(StockMovement.quantity), 0)).filter(StockMovement.movement_type.in_(['in', 'receipt']), StockMovement.created_at.between(start, end)).scalar() or 0
    stock_out = db.session.query(func.coalesce(func.sum(StockMovement.quantity), 0)).filter(StockMovement.movement_type.in_(['out', 'issue', 'allocated']), StockMovement.created_at.between(start, end)).scalar() or 0
    most_used = db.session.query(Material.name, func.sum(StockMovement.quantity).label('total_moved')).join(Material, Material.id == StockMovement.material_id).filter(StockMovement.created_at.between(start, end)).group_by(Material.id).order_by(func.sum(StockMovement.quantity).desc()).first()
    top_value = db.session.query(Material.name, (Material.current_stock * Material.unit_cost).label('value')).filter(Material.unit_cost.isnot(None)).order_by((Material.current_stock * Material.unit_cost).desc()).first()
    active_alerts = StockAlert.query.filter_by(is_read=False).count()
    materials_by_category = db.session.query(Material.category, func.count(Material.id).label('count'), func.coalesce(func.sum(Material.current_stock), 0).label('total_stock')).filter(Material.category.isnot(None)).group_by(Material.category).order_by(func.count(Material.id).desc()).all()
    movement_summary = db.session.query(StockMovement.movement_type, func.count(StockMovement.id).label('count'), func.coalesce(func.sum(StockMovement.quantity), 0).label('total_quantity')).filter(StockMovement.created_at.between(start, end)).group_by(StockMovement.movement_type).all()

    # Prepare chart data
    category_labels = [c.category for c in materials_by_category]
    category_counts = [c.count for c in materials_by_category]

    movement_labels = [m.movement_type for m in movement_summary]
    movement_counts = [m.count for m in movement_summary]

    context = {
        'start': start,
        'end': end,
        'total_spare_parts': total_spare_parts,
        'total_stock_value': round(total_stock_value, 2),
        'low_stock_items': low_stock_items,
        'overstock_items': overstock_items,
        'critical_items': critical_items,
        'avg_stock_level': round(avg_stock_level, 2),
        'stock_in': stock_in,
        'stock_out': stock_out,
        'most_used': most_used,
        'top_value': top_value,
        'active_alerts': active_alerts,
        'materials_by_category': materials_by_category,
        'movement_summary': movement_summary,
        'category_labels': category_labels, 'category_counts': category_counts,
        'movement_labels': movement_labels, 'movement_counts': movement_counts
    }

    return render_template('main/stock_kpis.html', **context)

@main_bp.route('/analytics')
@login_required
@role_required('admin')
def analytics():
    """Admin analytics dashboard showing technician performance metrics"""
    from sqlalchemy import func, desc
    
    # Get all technicians and their performance metrics
    technician_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.zone,
        func.count(MaintenanceReport.id).label('total_reports'),
        func.sum(MaintenanceReport.actual_duration_hours).label('total_hours'),
        func.avg(MaintenanceReport.actual_duration_hours).label('avg_hours')
    ).outerjoin(MaintenanceReport, User.id == MaintenanceReport.technician_id)\
     .filter(User.role == 'technician')\
     .group_by(User.id)\
     .all()
    
    # Convert to list of dicts for easier template processing
    technicians = []
    for stat in technician_stats:
        technicians.append({
            'id': stat.id,
            'name': f"{stat.first_name} {stat.last_name}",
            'zone': stat.zone or 'No Zone',
            'total_reports': stat.total_reports or 0,
            'total_hours': stat.total_hours or 0,
            'avg_hours': round(stat.avg_hours, 2) if stat.avg_hours else 0
        })
    
    # Sort to get top performers
    most_reports = sorted(technicians, key=lambda x: x['total_reports'], reverse=True)[:5]
    most_time = sorted(technicians, key=lambda x: x['total_hours'], reverse=True)[:5]
    fastest = sorted(technicians, key=lambda x: x['avg_hours'])[:5]
    
    # Get stats by zone
    zone_stats = db.session.query(
        User.zone,
        func.count(MaintenanceReport.id).label('total_reports'),
        func.sum(MaintenanceReport.actual_duration_hours).label('total_hours'),
        func.count(func.distinct(User.id)).label('technicians')
    ).join(User, User.id == MaintenanceReport.technician_id)\
     .filter(User.zone.isnot(None))\
     .group_by(User.zone)\
     .all()
    
    zones = [{
        'name': stat.zone or 'Unassigned',
        'total_reports': stat.total_reports or 0,
        'total_hours': stat.total_hours or 0,
        'avg_hours': round((stat.total_hours or 0) / (stat.total_reports or 1), 2),
        'technicians': stat.technicians or 0
    } for stat in zone_stats]
    
    # Overall statistics
    total_reports = MaintenanceReport.query.count()
    total_technicians = User.query.filter_by(role='technician').count()
    total_hours = db.session.query(func.sum(MaintenanceReport.actual_duration_hours)).scalar() or 0
    avg_report_duration = round(total_hours / total_reports, 2) if total_reports > 0 else 0
    
    return render_template('main/analytics.html',
                         technicians=technicians,
                         most_reports=most_reports,
                         most_time=most_time,
                         fastest=fastest,
                         zones=zones,
                         total_reports=total_reports,
                         total_technicians=total_technicians,
                         total_hours=round(total_hours, 2),
                         avg_report_duration=avg_report_duration)

@main_bp.route('/modules')
@login_required
def modules():
    user = User.query.get(session['user_id'])
    
    # Define available modules based on user role
    modules_available = {
        'admin': ['stock', 'maintenance', 'demands', 'dashboard', 'users'],
        'supervisor': ['stock', 'maintenance', 'demands', 'dashboard'],
        'technician': ['stock', 'demands'],
        'stock_agent': ['stock', 'demands']
    }
    
    available = modules_available.get(user.role, [])
    
    return render_template('main/modules.html', user=user, available_modules=available)

# Zone & User Management Routes
# Zone Management Routes
@main_bp.route('/zones')
@login_required
@role_required('admin', 'supervisor')
def manage_zones():
    """Manage zones (view all zones and assign to technicians)"""
    page = request.args.get('page', 1, type=int)
    
    zones = Zone.query.paginate(page=page, per_page=20)
    technicians = User.query.filter_by(role='technician').all()
    
    return render_template('main/manage_zones.html', zones=zones, technicians=technicians)

@main_bp.route('/zones/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def add_zone():
    """Add new zone"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        
        if not name:
            flash('Zone name cannot be empty', 'danger')
            return redirect(url_for('main.add_zone'))
        
        # Check if zone already exists
        existing = Zone.query.filter_by(name=name).first()
        if existing:
            flash(f'Zone "{name}" already exists', 'warning')
            return redirect(url_for('main.add_zone'))
        
        zone = Zone(
            name=name,
            description=description,
            location=location,
            created_by_id=session['user_id']
        )
        
        db.session.add(zone)
        db.session.commit()
        flash(f'Zone "{name}" created successfully!', 'success')
        return redirect(url_for('main.manage_zones'))
    
    return render_template('main/add_zone.html')

@main_bp.route('/zones/<int:zone_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def edit_zone(zone_id):
    """Edit existing zone"""
    zone = Zone.query.get_or_404(zone_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        
        if not name:
            flash('Zone name cannot be empty', 'danger')
            return redirect(url_for('main.edit_zone', zone_id=zone_id))
        
        # Check if new name conflicts with another zone
        if name != zone.name:
            existing = Zone.query.filter_by(name=name).first()
            if existing:
                flash(f'Zone "{name}" already exists', 'warning')
                return redirect(url_for('main.edit_zone', zone_id=zone_id))
        
        zone.name = name
        zone.description = description
        zone.location = location
        db.session.commit()
        flash(f'Zone "{name}" updated successfully!', 'success')
        return redirect(url_for('main.manage_zones'))
    
    return render_template('main/edit_zone.html', zone=zone)

@main_bp.route('/zones/<int:zone_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def delete_zone(zone_id):
    """Delete zone"""
    zone = Zone.query.get_or_404(zone_id)
    zone_name = zone.name
    
    # Remove zone from technicians
    technicians = User.query.filter(User.zone == zone_name).all()
    for tech in technicians:
        tech.zone = None
    
    db.session.delete(zone)
    db.session.commit()
    flash(f'Zone "{zone_name}" deleted successfully!', 'success')
    return redirect(url_for('main.manage_zones'))

@main_bp.route('/zones/<int:zone_id>/assign/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def assign_zone_to_technician(zone_id, user_id):
    """Assign zone to technician"""
    zone = Zone.query.get_or_404(zone_id)
    user = User.query.get_or_404(user_id)
    
    if user.role != 'technician':
        flash('Only technicians can be assigned zones.', 'danger')
        return redirect(url_for('main.manage_zones'))
    
    user.zone = zone.name
    db.session.commit()
    flash(f'Zone "{zone.name}" assigned to {user.full_name} successfully!', 'success')
    return redirect(url_for('main.manage_zones'))

@main_bp.route('/technicians')
@login_required
@role_required('admin', 'supervisor')
def list_technicians():
    """List all technicians with their zones"""
    page = request.args.get('page', 1, type=int)
    zone_filter = request.args.get('zone', '')
    
    query = User.query.filter_by(role='technician')
    
    if zone_filter:
        query = query.filter_by(zone=zone_filter)
    
    technicians = query.paginate(page=page, per_page=20)
    
    # Get unique zones
    zones = db.session.query(User.zone).filter(
        User.role == 'technician',
        User.zone.isnot(None)
    ).distinct().all()
    
    return render_template(
        'main/technicians_list.html',
        technicians=technicians,
        zones=[z[0] for z in zones],
        zone_filter=zone_filter
    )

# Stock Management Routes
stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

@stock_bp.route('/')
@login_required
def inventory():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Material.query
    
    if search:
        query = query.filter(
            (Material.code.ilike(f'%{search}%')) |
            (Material.name.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter_by(category=category)
    
    materials = query.paginate(page=page, per_page=20)
    categories = db.session.query(Material.category).distinct().all()
    
    return render_template(
        'stock/inventory.html',
        materials=materials,
        categories=[cat[0] for cat in categories],
        search=search,
        category=category
    )

@stock_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'stock_agent')
def add_material():
    if request.method == 'POST':
        material = Material(
            code=request.form.get('code'),
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            unit=request.form.get('unit'),
            min_stock=int(request.form.get('min_stock', 10)),
            max_stock=int(request.form.get('max_stock', 100)),
            current_stock=int(request.form.get('current_stock', 0)),
            unit_cost=float(request.form.get('unit_cost', 0)),
            supplier=request.form.get('supplier')
        )
        
        db.session.add(material)
        db.session.commit()
        
        flash(f'Material {material.code} added successfully!', 'success')
        return redirect(url_for('stock.inventory'))
    
    return render_template('stock/add_material.html')

@stock_bp.route('/edit/<int:material_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'stock_agent')
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    if request.method == 'POST':
        material.name = request.form.get('name', material.name)
        material.description = request.form.get('description', material.description)
        material.category = request.form.get('category', material.category)
        material.unit = request.form.get('unit', material.unit)
        material.min_stock = int(request.form.get('min_stock', material.min_stock))
        material.max_stock = int(request.form.get('max_stock', material.max_stock))
        material.unit_cost = float(request.form.get('unit_cost', material.unit_cost))
        material.supplier = request.form.get('supplier', material.supplier)
        
        db.session.commit()
        flash(f'Material {material.code} updated successfully!', 'success')
        return redirect(url_for('stock.inventory'))
    
    return render_template('stock/edit_material.html', material=material)

@stock_bp.route('/detail/<int:material_id>')
@login_required
def material_detail(material_id):
    material = Material.query.get_or_404(material_id)
    movements = material.movements
    recent_demands = SparePartsDemand.query.filter_by(material_id=material_id).order_by(
        SparePartsDemand.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'stock/material_detail.html',
        material=material,
        movements=movements,
        recent_demands=recent_demands
    )

@stock_bp.route('/alerts')
@login_required
@role_required('admin', 'supervisor', 'stock_agent')
def stock_alerts():
    page = request.args.get('page', 1, type=int)
    unread_only = request.args.get('unread', 'true').lower() == 'true'
    
    query = StockAlert.query
    if unread_only:
        query = query.filter_by(is_read=False)
    
    alerts = query.order_by(StockAlert.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('stock/alerts.html', alerts=alerts, unread_only=unread_only)

@stock_bp.route('/alert/<int:alert_id>/mark-read', methods=['POST'])
@login_required
@role_required('admin', 'supervisor', 'stock_agent')
def mark_alert_read(alert_id):
    alert = StockAlert.query.get_or_404(alert_id)
    alert.is_read = True
    alert.read_at = datetime.utcnow()
    db.session.commit()
    
    flash('Alert marked as read.', 'success')
    return redirect(url_for('stock.stock_alerts'))

@stock_bp.route('/alert/<int:alert_id>/skip')
@login_required
@role_required('admin', 'supervisor', 'stock_agent')
def skip_alert(alert_id):
    """Quick action to skip/acknowledge a stock alert from an email link."""
    alert = StockAlert.query.get_or_404(alert_id)
    alert.is_read = True
    alert.read_at = datetime.utcnow()
    db.session.commit()

    flash('Alert skipped.', 'success')
    return redirect(url_for('stock.stock_alerts'))

@stock_bp.route('/movement-history')
@login_required
def movement_history():
    """View complete stock movement history"""
    page = request.args.get('page', 1, type=int)
    material_id = request.args.get('material_id', '')
    movement_type = request.args.get('type', '')
    
    from app.models import StockMovement
    query = StockMovement.query
    
    if material_id:
        query = query.filter_by(material_id=material_id)
    
    if movement_type:
        query = query.filter_by(movement_type=movement_type)
    
    movements = query.order_by(StockMovement.created_at.desc()).paginate(page=page, per_page=50)
    materials = Material.query.all()
    
    return render_template(
        'stock/movement_history.html',
        movements=movements,
        materials=materials,
        material_id=material_id,
        movement_type=movement_type
    )

@stock_bp.route('/return-material', methods=['GET', 'POST'])
@login_required
def return_material():
    """Return material to stock from a demand"""
    if request.method == 'POST':
        from app.models import MaterialReturn, StockMovement, SparePartsDemand
        
        demand_id = request.form.get('demand_id')
        quantity = int(request.form.get('quantity', 0))
        reason = request.form.get('reason', '')
        condition = request.form.get('condition', 'new')
        
        demand = SparePartsDemand.query.get_or_404(demand_id)
        material = Material.query.get(demand.material_id)
        
        if quantity <= 0 or quantity > (demand.quantity_allocated - demand.quantity_returned):
            flash('Invalid return quantity.', 'danger')
            return redirect(url_for('stock.return_material'))
        
        # Create return record
        material_return = MaterialReturn(
            demand_id=demand_id,
            material_id=demand.material_id,
            quantity_returned=quantity,
            return_reason=reason,
            condition_of_material=condition,
            returned_by_id=session['user_id'],
            return_status='pending'
        )
        
        db.session.add(material_return)
        db.session.commit()
        
        flash('Return request created successfully. Awaiting stock agent approval.', 'success')
        return redirect(url_for('stock.return_material'))
    
    # Get pending demands for the user
    from app.models import SparePartsDemand
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    pending_demands = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_status == 'fulfilled') |
        (SparePartsDemand.demand_status == 'approved_stock_agent'),
        SparePartsDemand.requestor_id == user_id,
        SparePartsDemand.quantity_returned < SparePartsDemand.quantity_allocated
    ).all()
    
    return render_template('stock/return_material.html', demands=pending_demands)

@stock_bp.route('/returns-pending')
@login_required
@role_required('stock_agent', 'admin')
def pending_returns():
    """View pending material returns"""
    from app.models import MaterialReturn
    
    page = request.args.get('page', 1, type=int)
    returns = MaterialReturn.query.filter_by(return_status='pending').order_by(
        MaterialReturn.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('stock/pending_returns.html', returns=returns)

@stock_bp.route('/return/<int:return_id>/accept', methods=['POST'])
@login_required
@role_required('stock_agent', 'admin')
def accept_return(return_id):
    """Accept a returned material"""
    from app.models import MaterialReturn, StockMovement
    
    material_return = MaterialReturn.query.get_or_404(return_id)
    material = Material.query.get(material_return.material_id)
    
    if material_return.return_status != 'pending':
        flash('This return has already been processed.', 'warning')
        return redirect(url_for('stock.pending_returns'))
    
    # Update material stock
    material.current_stock += material_return.quantity_returned
    
    # Record stock movement
    movement = StockMovement(
        material_id=material.id,
        movement_type='returned',
        quantity=material_return.quantity_returned,
        reference_id=f"return-{material_return.id}",
        user_id=session['user_id'],
        notes=f'Material returned - {material_return.return_reason}'
    )
    db.session.add(movement)
    
    # Update return status
    material_return.return_status = 'accepted'
    material_return.received_by_id = session['user_id']
    material_return.processed_at = datetime.utcnow()
    
    # Update demand
    demand = SparePartsDemand.query.get(material_return.demand_id)
    if demand:
        demand.quantity_returned += material_return.quantity_returned
        demand.return_date = datetime.utcnow()
    
    db.session.commit()
    flash(f'{material_return.quantity_returned} units of {material.name} accepted and added to stock.', 'success')
    return redirect(url_for('stock.pending_returns'))

@stock_bp.route('/return/<int:return_id>/reject', methods=['POST'])
@login_required
@role_required('stock_agent', 'admin')
def reject_return(return_id):
    """Reject a returned material"""
    from app.models import MaterialReturn
    
    material_return = MaterialReturn.query.get_or_404(return_id)
    
    if material_return.return_status != 'pending':
        flash('This return has already been processed.', 'warning')
        return redirect(url_for('stock.pending_returns'))
    
    material_return.return_status = 'rejected'
    material_return.received_by_id = session['user_id']
    material_return.processed_at = datetime.utcnow()
    material_return.notes = request.form.get('notes', '')
    
    db.session.commit()
    flash('Return request rejected.', 'warning')
    return redirect(url_for('stock.pending_returns'))