from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.models import db, Material, Machine, MaintenanceSchedule, SparePartsDemand, StockAlert, User, MaterialReturn, Zone, MaintenanceReport, StockMovement, PreventiveMaintenanceExecution, PreventiveMaintenanceTaskExecution, MachineStatus
from app.routes.auth import login_required, role_required
from datetime import datetime, timedelta
import json

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
            'title': 'Preventive Maintenance Reports',
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
    
    # Stock alerts
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
        recent_maintenance=recent_maintenance
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
    # Mécanique (Mechanical)
    {'id': 'corr_001', 'name': 'Changement oreil a collet enduit', 'category': 'Mécanique'},
    {'id': 'corr_002', 'name': 'Ajustement unité redressement', 'category': 'Mécanique'},
    {'id': 'corr_003', 'name': 'Changement galet', 'category': 'Mécanique'},
    {'id': 'corr_004', 'name': 'Ajustement wire drive', 'category': 'Mécanique'},
    {'id': 'corr_005', 'name': 'Changement courroies crantées', 'category': 'Mécanique'},
    {'id': 'corr_006', 'name': 'Changement roue de mesure', 'category': 'Mécanique'},
    {'id': 'corr_007', 'name': 'Changement roues dentées (Z32)', 'category': 'Mécanique'},
    {'id': 'corr_008', 'name': 'Changement roues dentées (Z18)', 'category': 'Mécanique'},
    {'id': 'corr_009', 'name': 'Changement galet de pression', 'category': 'Mécanique'},
    {'id': 'corr_010', 'name': 'Changement capot de protection', 'category': 'Mécanique'},
    {'id': 'corr_011', 'name': 'Réglage roue de mesure', 'category': 'Mécanique'},
    {'id': 'corr_012', 'name': 'Changement guide cable', 'category': 'Mécanique'},
    {'id': 'corr_013', 'name': 'Changement axe d\'encodeur', 'category': 'Mécanique'},
    {'id': 'corr_014', 'name': 'Changement roullement rainurée', 'category': 'Mécanique'},
    {'id': 'corr_015', 'name': 'Ajustement des machoires', 'category': 'Mécanique'},
    {'id': 'corr_016', 'name': 'Changement machoires', 'category': 'Mécanique'},
    {'id': 'corr_017', 'name': 'Changement Pivotement CPL', 'category': 'Mécanique'},
    {'id': 'corr_018', 'name': 'Vérification bloc de lames après 150.000 coupes', 'category': 'Mécanique'},
    {'id': 'corr_019', 'name': 'Changement lames a dénudés', 'category': 'Mécanique'},
    {'id': 'corr_020', 'name': 'Changement lames de coupe', 'category': 'Mécanique'},
    {'id': 'corr_021', 'name': 'Ajustement tete de coupe', 'category': 'Mécanique'},
    {'id': 'corr_022', 'name': 'Changement tole bloc d\'arret', 'category': 'Mécanique'},
    {'id': 'corr_023', 'name': 'Changemnt tole de guidage (vé de centrage)', 'category': 'Mécanique'},
    {'id': 'corr_024', 'name': 'Changement vérin tole de guidage', 'category': 'Mécanique'},
    {'id': 'corr_025', 'name': 'Changement appui cpl', 'category': 'Mécanique'},
    {'id': 'corr_026', 'name': 'Changement levier de fixation', 'category': 'Mécanique'},
    {'id': 'corr_027', 'name': 'Changement manchon de fixation outil', 'category': 'Mécanique'},
    {'id': 'corr_028', 'name': 'Changement coupe bande', 'category': 'Mécanique'},
    {'id': 'corr_029', 'name': 'Changement lame de coupe bande', 'category': 'Mécanique'},
    {'id': 'corr_030', 'name': 'Changement boitier de coupe bande', 'category': 'Mécanique'},
    {'id': 'corr_031', 'name': 'Changement joint de coupe bande', 'category': 'Mécanique'},
    {'id': 'corr_032', 'name': 'Changement piston de coupe bande', 'category': 'Mécanique'},
    {'id': 'corr_033', 'name': 'Changement galet devant', 'category': 'Mécanique'},
    {'id': 'corr_034', 'name': 'Changement galet en arriére', 'category': 'Mécanique'},
    {'id': 'corr_035', 'name': 'Réglage tandeur', 'category': 'Mécanique'},
    {'id': 'corr_036', 'name': 'Changement palque devant', 'category': 'Mécanique'},
    {'id': 'corr_037', 'name': 'Changement plaque en arriére', 'category': 'Mécanique'},
    {'id': 'corr_038', 'name': 'Reglage tapis transporteuse', 'category': 'Mécanique'},
    {'id': 'corr_039', 'name': 'Rincage+centrage IMS', 'category': 'Mécanique'},
    {'id': 'corr_040', 'name': 'Réglage K26', 'category': 'Mécanique'},
    {'id': 'corr_041', 'name': 'Pb unitée d\'entrainement', 'category': 'Mécanique'},
    {'id': 'corr_042', 'name': 'Centrage d\'applicateur seal', 'category': 'Mécanique'},
    {'id': 'corr_043', 'name': 'Changement vibreur', 'category': 'Mécanique'},
    {'id': 'corr_044', 'name': 'Reglage vibration seal', 'category': 'Mécanique'},
    {'id': 'corr_045', 'name': 'Changement mondrin', 'category': 'Mécanique'},
    {'id': 'corr_046', 'name': 'Changement dornpin', 'category': 'Mécanique'},
    {'id': 'corr_047', 'name': 'Ajustement Touniquer', 'category': 'Mécanique'},
    {'id': 'corr_048', 'name': 'Ajustement tete d\'insertion', 'category': 'Mécanique'},
    {'id': 'corr_049', 'name': 'Patinage', 'category': 'Mécanique'},
    {'id': 'corr_050', 'name': 'Ajustement coupe Bande', 'category': 'Mécanique'},
    {'id': 'corr_051', 'name': 'Réglage variation denudage', 'category': 'Mécanique'},
    {'id': 'corr_052', 'name': 'Réglage vé de centrage', 'category': 'Mécanique'},
    {'id': 'corr_053', 'name': 'Réparation tole bloc d\'arrét', 'category': 'Mécanique'},
    {'id': 'corr_054', 'name': 'Changement insertion sleeve', 'category': 'Mécanique'},
    {'id': 'corr_055', 'name': 'Réglage enrouleur papier', 'category': 'Mécanique'},
    {'id': 'corr_056', 'name': 'Réglage bras de pivotement coté 1', 'category': 'Mécanique'},
    {'id': 'corr_057', 'name': 'Réglage bras de pivotement coté 2', 'category': 'Mécanique'},
    {'id': 'corr_058', 'name': 'Changement manchant seal', 'category': 'Mécanique'},
    {'id': 'corr_059', 'name': 'Réglage convoyeur', 'category': 'Mécanique'},
    {'id': 'corr_060', 'name': 'Réglage goulette retractable', 'category': 'Mécanique'},
    {'id': 'corr_061', 'name': 'Calibrage machine de traction', 'category': 'Mécanique'},
    {'id': 'corr_062', 'name': 'Ajustement bande transporteuse', 'category': 'Mécanique'},
    {'id': 'corr_063', 'name': 'Reglage unité de torsadage (twist)', 'category': 'Mécanique'},
    {'id': 'corr_064', 'name': 'Module d\'orientation', 'category': 'Mécanique'},
    {'id': 'corr_065', 'name': 'Remplacement Joint double station seal', 'category': 'Mécanique'},
    {'id': 'corr_066', 'name': 'Probleme unité bandage sigma', 'category': 'Mécanique'},
    {'id': 'corr_067', 'name': 'Probleme gulotte rettractable', 'category': 'Mécanique'},
    
    # Électrique (Electrical)
    {'id': 'corr_101', 'name': 'Changement encodeur', 'category': 'Électrique'},
    {'id': 'corr_102', 'name': 'Ajustement micro switch', 'category': 'Électrique'},
    {'id': 'corr_103', 'name': 'Changement micro switch', 'category': 'Électrique'},
    {'id': 'corr_104', 'name': 'Changement ACS116 (servomoteur)', 'category': 'Électrique'},
    {'id': 'corr_105', 'name': 'Changement capteur des machoires', 'category': 'Électrique'},
    {'id': 'corr_106', 'name': 'Changement capteur mouvement linéaire', 'category': 'Électrique'},
    {'id': 'corr_107', 'name': 'Changement capteur mouvement rotationnelle', 'category': 'Électrique'},
    {'id': 'corr_108', 'name': 'Changement moteur', 'category': 'Électrique'},
    {'id': 'corr_109', 'name': 'Changement ACS108', 'category': 'Électrique'},
    {'id': 'corr_110', 'name': 'Changement détecteur optique tole de guidage', 'category': 'Électrique'},
    {'id': 'corr_111', 'name': 'Changement Barrage photoelectrique d\'enrouleur papier', 'category': 'Électrique'},
    {'id': 'corr_112', 'name': 'Réglage MCD', 'category': 'Électrique'},
    {'id': 'corr_113', 'name': 'Ajustement capteur bras de pivotement coté 1', 'category': 'Électrique'},
    {'id': 'corr_114', 'name': 'Ajustement capteur bras de pivotement coté 2', 'category': 'Électrique'},
    {'id': 'corr_115', 'name': 'Reglage capteur de présence seal', 'category': 'Électrique'},
    {'id': 'corr_116', 'name': 'Changement capteur de présence seal', 'category': 'Électrique'},
    {'id': 'corr_117', 'name': 'Reglage SPM', 'category': 'Électrique'},
    {'id': 'corr_118', 'name': 'Changement capteur goulette retractable', 'category': 'Électrique'},
    {'id': 'corr_119', 'name': 'Probléme ACS116 (servomoteur)', 'category': 'Électrique'},
    {'id': 'corr_120', 'name': 'Probléme ACS108 (servomoteur)', 'category': 'Électrique'},
    {'id': 'corr_121', 'name': 'Probléme ACS204 (servomoteur)', 'category': 'Électrique'},
    {'id': 'corr_122', 'name': 'Changement ACS204 (servomoteur)', 'category': 'Électrique'},
    {'id': 'corr_123', 'name': 'Problème servoregulateur', 'category': 'Électrique'},
    {'id': 'corr_124', 'name': 'Changement cable MCI rg 45', 'category': 'Électrique'},
    {'id': 'corr_125', 'name': 'Changement cable capteur', 'category': 'Électrique'},
    
    # Informatique/Soft
    {'id': 'corr_201', 'name': 'Mise a jour ACS 116', 'category': 'Informatique/Soft'},
    {'id': 'corr_202', 'name': 'Positionnement zéro', 'category': 'Informatique/Soft'},
    {'id': 'corr_203', 'name': 'Mise a jour ACS 108', 'category': 'Informatique/Soft'},
    {'id': 'corr_204', 'name': 'Étalonnage de presse', 'category': 'Informatique/Soft'},
    {'id': 'corr_205', 'name': 'Positionnement zéro de presse', 'category': 'Informatique/Soft'},
    {'id': 'corr_206', 'name': 'Ajustement et calibrage SQC', 'category': 'Informatique/Soft'},
    {'id': 'corr_207', 'name': 'Installation CAO', 'category': 'Informatique/Soft'},
    {'id': 'corr_208', 'name': 'Installation Topwin', 'category': 'Informatique/Soft'},
    {'id': 'corr_209', 'name': 'Instattation Caméra', 'category': 'Informatique/Soft'},
    {'id': 'corr_210', 'name': 'Probleme Topwin', 'category': 'Informatique/Soft'},
    
    # Pneumatique (Pneumatic)
    {'id': 'corr_301', 'name': 'Reglage pneumatique d\'applicateur seal', 'category': 'Pneumatique'},
]


@main_bp.route('/maintenance-report', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor', 'technician')
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
            report_id = request.form.get('report_id')
            
            # Get existing report or create new
            if report_id:
                try:
                    report = MaintenanceReport.query.get(int(report_id))
                except:
                    report = None
            else:
                report = None
            
            if not report:
                report = MaintenanceReport()
                report.technician_id = user.id
                report.report_status = 'draft'
                report.created_at = datetime.utcnow()
            
            # Update report with form data
            machine_id = request.form.get('machine_id')
            if machine_id:
                machine = Machine.query.get(int(machine_id))
                if machine:
                    report.machine_name = machine.name
            
            report.work_description = request.form.get('equipment', '')
            report.technician_zone = request.form.get('serial_number', '')
            report.environmental_conditions = request.form.get('inventory_number', '')
            report.safety_observations = request.form.get('technician_observations', '')
            report.report_status = 'submitted'
            report.actual_end_time = datetime.utcnow()
            report.updated_at = datetime.utcnow()
            
            db.session.add(report)
            db.session.commit()
            
            flash('Rapport de maintenance enregistré et archivé avec succès!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error submitting maintenance report: {str(e)}')
            flash(f'Erreur lors de la soumission: {str(e)}', 'danger')
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
    
    return render_template(
        'preventive_reports_card_view.html',
        executions=executions,
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
def mark_alert_read(alert_id):
    alert = StockAlert.query.get_or_404(alert_id)
    alert.is_read = True
    alert.read_at = datetime.utcnow()
    db.session.commit()
    
    flash('Alert marked as read.', 'success')
    return redirect(url_for('stock.stock_alerts'))

@stock_bp.route('/alert/<int:alert_id>/skip')
@login_required
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