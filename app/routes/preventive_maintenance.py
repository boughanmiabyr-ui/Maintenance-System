from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from app.models import (
    db, Machine, User, PreventiveMaintenancePlan, PreventiveMaintenanceTask,
    PreventiveMaintenanceExecution, PreventiveMaintenanceTaskExecution, SparePartsDemand, Zone
)
from app.routes.auth import login_required, role_required
from datetime import datetime, timedelta, date
import json

preventive_bp = Blueprint('preventive', __name__, url_prefix='/preventive-maintenance')

# ============================================
# PREVENTIVE MAINTENANCE PLANS MANAGEMENT
# ============================================

@preventive_bp.route('/')
@login_required
def index():
    """List all preventive maintenance plans"""
    user = User.query.get(session['user_id'])
    
    # Filter plans based on role
    if user.role == 'technician':
        # Show all active plans for their machines
        plans = PreventiveMaintenancePlan.query.filter_by(is_active=True).all()
    else:
        # Supervisors/Admins see all plans
        plans = PreventiveMaintenancePlan.query.all()
    
    machines = Machine.query.filter_by(status='active').all()
    
    return render_template('preventive_maintenance/index.html', plans=plans, machines=machines)

@preventive_bp.route('/plan/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def create_plan():
    """Create a new preventive maintenance plan"""
    if request.method == 'POST':
        machine_id = request.form.get('machine_id')
        plan_name = request.form.get('plan_name')
        frequency_type = request.form.get('frequency_type')  # monthly, semi-annual, annual
        description = request.form.get('description')
        
        # Calculate frequency_days
        frequency_mapping = {
            'monthly': 30,
            'semi-annual': 180,
            'annual': 365
        }
        frequency_days = frequency_mapping.get(frequency_type, 30)
        
        plan = PreventiveMaintenancePlan(
            plan_name=plan_name,
            machine_id=machine_id,
            frequency_type=frequency_type,
            frequency_days=frequency_days,
            description=description,
            is_active=True,
            created_by_id=session['user_id'],
            next_planned=date.today()
        )
        
        db.session.add(plan)
        db.session.commit()
        
        flash(f'Preventive maintenance plan "{plan_name}" created successfully!', 'success')
        return redirect(url_for('preventive.plan_detail', plan_id=plan.id))
    
    machines = Machine.query.filter_by(status='active').all()
    return render_template('preventive_maintenance/create_plan.html', machines=machines)

@preventive_bp.route('/plan/<int:plan_id>')
@login_required
def plan_detail(plan_id):
    """View plan details and its tasks"""
    plan = PreventiveMaintenancePlan.query.get_or_404(plan_id)
    tasks = PreventiveMaintenanceTask.query.filter_by(plan_id=plan_id).order_by(
        PreventiveMaintenanceTask.task_number
    ).all()
    
    return render_template(
        'preventive_maintenance/plan_detail.html',
        plan=plan,
        tasks=tasks
    )

@preventive_bp.route('/plan/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def edit_plan(plan_id):
    """Edit a preventive maintenance plan"""
    plan = PreventiveMaintenancePlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        plan.plan_name = request.form.get('plan_name')
        plan.frequency_type = request.form.get('frequency_type')
        plan.description = request.form.get('description')
        plan.is_active = request.form.get('is_active') == 'on'
        
        frequency_mapping = {'monthly': 30, 'semi-annual': 180, 'annual': 365}
        plan.frequency_days = frequency_mapping.get(plan.frequency_type, 30)
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Plan updated successfully!', 'success')
        return redirect(url_for('preventive.plan_detail', plan_id=plan.id))
    
    return render_template('preventive_maintenance/edit_plan.html', plan=plan)

# ============================================
# PREVENTIVE MAINTENANCE TASKS MANAGEMENT
# ============================================

@preventive_bp.route('/plan/<int:plan_id>/task/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def create_task(plan_id):
    """Add a new task to a plan"""
    plan = PreventiveMaintenancePlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Get the next task number
        max_task_number = db.session.query(db.func.max(PreventiveMaintenanceTask.task_number)).filter_by(plan_id=plan_id).scalar() or 0
        
        task = PreventiveMaintenanceTask(
            plan_id=plan_id,
            task_number=max_task_number + 1,
            task_description=request.form.get('task_description'),
            category=request.form.get('category'),
            estimated_duration_minutes=int(request.form.get('estimated_duration_minutes', 15)),
            required_materials=request.form.get('required_materials'),
            safety_precautions=request.form.get('safety_precautions'),
            notes=request.form.get('notes')
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('preventive.plan_detail', plan_id=plan_id))
    
    return render_template('preventive_maintenance/create_task.html', plan=plan)

@preventive_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def edit_task(task_id):
    """Edit a task"""
    task = PreventiveMaintenanceTask.query.get_or_404(task_id)
    plan = task.plan
    
    if request.method == 'POST':
        task.task_description = request.form.get('task_description')
        task.category = request.form.get('category')
        task.estimated_duration_minutes = int(request.form.get('estimated_duration_minutes', 15))
        task.required_materials = request.form.get('required_materials')
        task.safety_precautions = request.form.get('safety_precautions')
        task.notes = request.form.get('notes')
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('preventive.plan_detail', plan_id=plan.id))
    
    return render_template('preventive_maintenance/edit_task.html', task=task, plan=plan)

@preventive_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def delete_task(task_id):
    """Delete a task"""
    task = PreventiveMaintenanceTask.query.get_or_404(task_id)
    plan_id = task.plan_id
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('preventive.plan_detail', plan_id=plan_id))

# ============================================
# PREVENTIVE MAINTENANCE EXECUTION
# ============================================

@preventive_bp.route('/executions')
@login_required
def executions():
    """List all preventive maintenance executions"""
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    machine_id = request.args.get('machine_id', '')
    
    query = PreventiveMaintenanceExecution.query
    
    # Role-based filtering
    if user.role == 'technician':
        query = query.filter_by(assigned_technician_id=user.id)
    elif user.role == 'supervisor':
        query = query.filter_by(assigned_supervisor_id=user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if machine_id:
        query = query.filter_by(machine_id=machine_id)
    
    executions = query.order_by(
        PreventiveMaintenanceExecution.scheduled_date.desc()
    ).paginate(page=page, per_page=20)
    
    machines = Machine.query.filter_by(status='active').all()
    
    return render_template(
        'preventive_maintenance/executions.html',
        executions=executions,
        machines=machines,
        status_filter=status_filter,
        machine_id=machine_id
    )

@preventive_bp.route('/plan/<int:plan_id>/schedule', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def schedule_execution(plan_id):
    """Schedule an execution of a preventive maintenance plan"""
    plan = PreventiveMaintenancePlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d').date()
        assigned_technician_id = request.form.get('assigned_technician_id')
        assigned_supervisor_id = request.form.get('assigned_supervisor_id', session['user_id'])
        machine_id = request.form.get('machine_id')  # Get machine from form selection
        
        execution = PreventiveMaintenanceExecution(
            plan_id=plan_id,
            machine_id=machine_id,  # Use selected machine, not plan's machine
            scheduled_date=scheduled_date,
            assigned_supervisor_id=assigned_supervisor_id or None,
            assigned_technician_id=assigned_technician_id or None,
            status='scheduled'
        )
        
        db.session.add(execution)
        db.session.flush()  # Get the execution ID
        
        # Create task execution records for each task in the plan
        for task in plan.tasks:
            task_exec = PreventiveMaintenanceTaskExecution(
                execution_id=execution.id,
                task_id=task.id,
                order_number=task.task_number,
                status='pending'
            )
            db.session.add(task_exec)
        
        db.session.commit()
        
        flash('Preventive maintenance execution scheduled successfully!', 'success')
        return redirect(url_for('preventive.execution_detail', execution_id=execution.id))
    
    # Get available technicians, supervisors, and machines
    technicians = User.query.filter_by(role='technician', status='active').all()
    supervisors = User.query.filter_by(role='supervisor', status='active').all()
    machines = Machine.query.filter_by(status='active').all()
    
    return render_template(
        'preventive_maintenance/schedule_execution.html',
        plan=plan,
        technicians=technicians,
        supervisors=supervisors,
        machines=machines
    )

@preventive_bp.route('/execution/<int:execution_id>')
@login_required
def execution_detail(execution_id):
    """View execution details and task list (Report View)"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    user = User.query.get(session['user_id'])
    
    # Permission check
    if user.role == 'technician' and execution.assigned_technician_id != user.id:
        if user.role != 'supervisor' or execution.assigned_supervisor_id != user.id:
            flash('You do not have access to this execution.', 'danger')
            return redirect(url_for('preventive.executions'))
    
    task_executions = PreventiveMaintenanceTaskExecution.query.filter_by(
        execution_id=execution_id
    ).order_by(PreventiveMaintenanceTaskExecution.order_number).all()
    
    return render_template(
        'preventive_maintenance/execution_detail.html',
        execution=execution,
        task_executions=task_executions,
        can_edit=(user.role == 'technician' and execution.assigned_technician_id == user.id)
    )

# ============================================
# TASK EXECUTION OPERATIONS (API)
# ============================================

@preventive_bp.route('/task-execution/<int:task_exec_id>/start', methods=['POST'])
@login_required
def start_task(task_exec_id):
    """Start a task (begin timing)"""
    task_exec = PreventiveMaintenanceTaskExecution.query.get_or_404(task_exec_id)
    execution = task_exec.execution
    user = User.query.get(session['user_id'])
    
    # Verify authorization
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    # Start the execution if not already started
    if execution.status == 'scheduled':
        execution.status = 'started'
        execution.actual_start_time = datetime.utcnow()
        execution.execution_date = date.today()
    
    task_exec.status = 'in_progress'
    task_exec.start_time = datetime.utcnow()
    task_exec.technician_id = user.id
    task_exec.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task started',
        'start_time': task_exec.start_time.isoformat()
    })

@preventive_bp.route('/task-execution/<int:task_exec_id>/end', methods=['POST'])
@login_required
def end_task(task_exec_id):
    """End a task (stop timing and record data)"""
    task_exec = PreventiveMaintenanceTaskExecution.query.get_or_404(task_exec_id)
    execution = task_exec.execution
    user = User.query.get(session['user_id'])
    
    # Verify authorization
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    # Get data from request
    data = request.get_json()
    
    task_exec.status = 'completed'
    task_exec.end_time = datetime.utcnow()
    task_exec.findings = data.get('findings', '')
    task_exec.actions_taken = data.get('actions_taken', '')
    task_exec.issues_encountered = data.get('issues_encountered', '')
    task_exec.materials_used = data.get('materials_used', '')
    task_exec.completion_notes = data.get('completion_notes', '')
    task_exec.quality_check = data.get('quality_check', 'passed')
    task_exec.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task completed',
        'end_time': task_exec.end_time.isoformat(),
        'duration_minutes': task_exec.duration_minutes
    })

@preventive_bp.route('/task-execution/<int:task_exec_id>/skip', methods=['POST'])
@login_required
def skip_task(task_exec_id):
    """Skip a task"""
    task_exec = PreventiveMaintenanceTaskExecution.query.get_or_404(task_exec_id)
    execution = task_exec.execution
    user = User.query.get(session['user_id'])
    
    # Verify authorization
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    data = request.get_json()
    
    task_exec.status = 'skipped'
    task_exec.completion_notes = data.get('reason', 'Task skipped')
    task_exec.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task skipped'})

@preventive_bp.route('/task-execution/<int:task_exec_id>/duration', methods=['GET'])
@login_required
def get_task_duration(task_exec_id):
    """Get current elapsed duration for a running task (server-side calculation)"""
    task_exec = PreventiveMaintenanceTaskExecution.query.get_or_404(task_exec_id)
    execution = task_exec.execution
    user = User.query.get(session['user_id'])
    
    # Verify authorization
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    if task_exec.status == 'completed':
        # Return the recorded duration
        return jsonify({
            'success': True,
            'status': 'completed',
            'duration_minutes': task_exec.actual_duration_minutes or task_exec.duration_minutes or 0,
            'elapsed_seconds': int((task_exec.end_time - task_exec.start_time).total_seconds()) if task_exec.start_time and task_exec.end_time else 0
        })
    elif task_exec.status == 'in_progress' and task_exec.start_time:
        # Calculate elapsed time from start to now
        elapsed = datetime.utcnow() - task_exec.start_time
        elapsed_seconds = int(elapsed.total_seconds())
        elapsed_minutes = elapsed_seconds // 60
        
        return jsonify({
            'success': True,
            'status': 'in_progress',
            'elapsed_seconds': elapsed_seconds,
            'elapsed_minutes': elapsed_minutes,
            'start_time': task_exec.start_time.isoformat()
        })
    else:
        # Task hasn't started
        return jsonify({
            'success': True,
            'status': task_exec.status,
            'elapsed_seconds': 0,
            'elapsed_minutes': 0
        })

# ============================================
# EXECUTION COMPLETION
# ============================================

@preventive_bp.route('/execution/<int:execution_id>/submit', methods=['POST'])
@login_required
def submit_execution(execution_id):
    """Submit a completed execution for supervisor approval"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    user = User.query.get(session['user_id'])
    
    # Verify authorization - only technician or admin can submit
    if execution.assigned_technician_id != user.id and user.role != 'admin':
        flash('You are not authorized to submit this execution.', 'danger')
        return redirect(url_for('preventive.execution_detail', execution_id=execution_id))
    
    # Get data from request
    data = request.form
    
    execution.overall_findings = data.get('overall_findings', '')
    execution.machine_condition = data.get('machine_condition', '')
    execution.issues_found = data.get('issues_found') == 'on'
    execution.issues_description = data.get('issues_description', '')
    execution.recommendations = data.get('recommendations', '')
    execution.spare_parts_needed = data.get('spare_parts_needed') == 'on'
    
    # Calculate total duration
    total_minutes = 0
    for task_exec in execution.task_executions:
        if task_exec.duration_minutes:
            total_minutes += task_exec.duration_minutes
    
    execution.total_duration_minutes = total_minutes
    execution.actual_end_time = datetime.utcnow()
    execution.status = 'completed'
    execution.report_status = 'submitted'
    execution.updated_at = datetime.utcnow()
    
    # Calculate next planned maintenance
    if execution.plan.frequency_days:
        execution.plan.next_planned = date.today() + timedelta(days=execution.plan.frequency_days)
        execution.plan.last_execution = datetime.utcnow()
    
    db.session.commit()
    
    flash('Maintenance execution submitted for supervisor approval!', 'success')
    return redirect(url_for('preventive.execution_detail', execution_id=execution_id))

@preventive_bp.route('/execution/<int:execution_id>/approve', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def approve_execution(execution_id):
    """Supervisor approves a completed execution"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    user = User.query.get(session['user_id'])
    
    data = request.form
    
    execution.supervision_status = 'approved'
    execution.supervisor_approval_date = datetime.utcnow()
    execution.supervisor_notes = data.get('supervisor_notes', '')
    execution.report_status = 'approved'
    execution.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Execution approved!', 'success')
    return redirect(url_for('preventive.execution_detail', execution_id=execution_id))

@preventive_bp.route('/execution/<int:execution_id>/reject', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def reject_execution(execution_id):
    """Supervisor rejects an execution"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    user = User.query.get(session['user_id'])
    
    data = request.form
    
    execution.supervision_status = 'rejected'
    execution.supervisor_approval_date = datetime.utcnow()
    execution.supervisor_notes = data.get('supervisor_notes', '')
    execution.report_status = 'rejected'
    execution.status = 'scheduled'  # Reset to allow re-execution
    execution.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Execution rejected and reset for re-work.', 'warning')
    return redirect(url_for('preventive.execution_detail', execution_id=execution_id))

# ============================================
# CALENDAR VIEW
# ============================================

@preventive_bp.route('/calendar')
@login_required
def calendar_view():
    """Calendar view for preventive maintenance schedules with machine and zone filtering"""
    from sqlalchemy.orm import joinedload
    
    user = User.query.get(session['user_id'])
    machine_id = request.args.get('machine_id', '')
    zone_id = request.args.get('zone_id', '')
    
    machines = Machine.query.filter_by(status='active').all()
    zones = Zone.query.all()
    
    # Get all upcoming and past executions
    query = PreventiveMaintenanceExecution.query.options(
        joinedload(PreventiveMaintenanceExecution.machine),
        joinedload(PreventiveMaintenanceExecution.plan)
    )
    
    if machine_id:
        query = query.filter_by(machine_id=machine_id)
    
    if user.role == 'technician':
        query = query.filter_by(assigned_technician_id=user.id)
    elif user.role == 'supervisor':
        query = query.filter_by(assigned_supervisor_id=user.id)
    
    executions = query.order_by(PreventiveMaintenanceExecution.scheduled_date).all()
    
    return render_template(
        'preventive_maintenance/calendar.html',
        executions=executions,
        machines=machines,
        zones=zones,
        selected_machine=machine_id,
        selected_zone=zone_id,
        today=date.today()
    )

@preventive_bp.route('/calendar/api')
@login_required
def calendar_api():
    """API endpoint for calendar events"""
    from sqlalchemy.orm import joinedload
    
    user = User.query.get(session['user_id'])
    machine_id = request.args.get('machine_id', '')
    
    query = PreventiveMaintenanceExecution.query.options(
        joinedload(PreventiveMaintenanceExecution.machine),
        joinedload(PreventiveMaintenanceExecution.plan)
    )
    
    if machine_id:
        query = query.filter_by(machine_id=machine_id)
    
    if user.role == 'technician':
        query = query.filter_by(assigned_technician_id=user.id)
    elif user.role == 'supervisor':
        query = query.filter_by(assigned_supervisor_id=user.id)
    
    executions = query.all()
    
    events = []
    for exec in executions:
        machine_name = exec.machine.name if exec.machine else 'Unknown'
        status_color = {
            'scheduled': '#007bff',
            'started': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        }.get(exec.status, '#6c757d')
        
        event = {
            'id': exec.id,
            'title': f"{machine_name} - {exec.plan.plan_name if exec.plan else 'Maintenance'}",
            'start': exec.scheduled_date.isoformat(),
            'backgroundColor': status_color,
            'borderColor': status_color,
            'extendedProps': {
                'status': exec.status,
                'machine': machine_name,
                'executionId': exec.id
            }
        }
        events.append(event)
    
    return jsonify(events)

# ============================================
# ARCHIVE / REPORT HISTORY
# ============================================

@preventive_bp.route('/archive')
@login_required
def archive():
    """View archive of completed preventive maintenance reports"""
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    machine_id = request.args.get('machine_id', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = PreventiveMaintenanceExecution.query.filter(
        PreventiveMaintenanceExecution.status.in_(['completed', 'cancelled'])
    )
    
    # Role-based filtering
    if user.role == 'technician':
        query = query.filter_by(assigned_technician_id=user.id)
    elif user.role == 'supervisor':
        query = query.filter_by(assigned_supervisor_id=user.id)
    
    if machine_id:
        query = query.filter_by(machine_id=machine_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(PreventiveMaintenanceExecution.execution_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(PreventiveMaintenanceExecution.execution_date <= end_date_obj)
    
    archive = query.order_by(
        PreventiveMaintenanceExecution.execution_date.desc()
    ).paginate(page=page, per_page=20)
    
    machines = Machine.query.filter_by(status='active').all()
    
    return render_template(
        'preventive_maintenance/archive.html',
        archive=archive,
        machines=machines,
        selected_machine=machine_id,
        start_date=start_date,
        end_date=end_date
    )

@preventive_bp.route('/execution/<int:execution_id>/print')
@login_required
def print_execution(execution_id):
    """Print-friendly view of an execution report"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    task_executions = PreventiveMaintenanceTaskExecution.query.filter_by(
        execution_id=execution_id
    ).order_by(PreventiveMaintenanceTaskExecution.order_number).all()
    
    return render_template(
        'preventive_maintenance/print_report.html',
        execution=execution,
        task_executions=task_executions
    )

@preventive_bp.route('/execution/<int:execution_id>/export-json')
@login_required
def export_json(execution_id):
    """Export execution data as JSON"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    task_executions = PreventiveMaintenanceTaskExecution.query.filter_by(
        execution_id=execution_id
    ).all()
    
    data = {
        'execution': {
            'id': execution.id,
            'plan_name': execution.plan.plan_name if execution.plan else '',
            'machine': {'id': execution.machine.id, 'name': execution.machine.name} if execution.machine else None,
            'scheduled_date': execution.scheduled_date.isoformat(),
            'execution_date': execution.execution_date.isoformat() if execution.execution_date else None,
            'status': execution.status,
            'overall_findings': execution.overall_findings,
            'machine_condition': execution.machine_condition,
            'issues_found': execution.issues_found,
            'issues_description': execution.issues_description,
            'recommendations': execution.recommendations,
            'total_duration_minutes': execution.total_duration_minutes,
            'completion_percentage': execution.completion_percentage
        },
        'tasks': [
            {
                'order': te.order_number,
                'description': te.task.task_description if te.task else '',
                'status': te.status,
                'start_time': te.start_time.isoformat() if te.start_time else None,
                'end_time': te.end_time.isoformat() if te.end_time else None,
                'duration_minutes': te.duration_minutes,
                'findings': te.findings,
                'actions_taken': te.actions_taken,
                'issues_encountered': te.issues_encountered
            }
            for te in task_executions
        ]
    }
    
    return jsonify(data)

# ============================================
# PROFESSIONAL REPORT FORM & PDF EXPORT
# ============================================

@preventive_bp.route('/execution/<int:execution_id>/report-form')
@login_required
def report_form(execution_id):
    """Display the professional preventive maintenance report form"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    machine = execution.machine
    task_executions = PreventiveMaintenanceTaskExecution.query.filter_by(
        execution_id=execution_id
    ).order_by(PreventiveMaintenanceTaskExecution.order_number).all()
    
    # Check authorization
    user = User.query.get(session['user_id'])
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        flash('You are not authorized to view this report.', 'danger')
        return redirect(url_for('preventive.executions'))
    
    return render_template(
        'preventive_maintenance/report_form.html',
        execution=execution,
        machine=machine,
        task_executions=task_executions,
        current_user=user
    )

@preventive_bp.route('/execution/<int:execution_id>/save-report', methods=['POST'])
@login_required
def save_execution_report(execution_id):
    """Save the preventive maintenance report"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    user = User.query.get(session['user_id'])
    
    # Check authorization
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Update execution data
        execution.overall_findings = request.form.get('overall_findings', '')
        execution.machine_condition = request.form.get('machine_condition', '')
        execution.issues_found = request.form.get('issues_found') == 'on'
        execution.issues_description = request.form.get('issues_description', '')
        execution.recommendations = request.form.get('recommendations', '')
        execution.spare_parts_needed = request.form.get('spare_parts_needed') == 'on'
        execution.status = 'completed'
        execution.report_status = 'submitted'
        execution.execution_date = datetime.now().date()
        execution.actual_end_time = datetime.utcnow()
        
        # Parse task data
        tasks_json = request.form.get('tasks', '[]')
        tasks_data = json.loads(tasks_json)
        
        # Update task executions
        for task_data in tasks_data:
            task_exec = PreventiveMaintenanceTaskExecution.query.get(task_data['id'])
            if task_exec:
                if task_data['status'] == 'OK':
                    task_exec.quality_check = 'passed'
                elif task_data['status'] == 'NOK':
                    task_exec.quality_check = 'failed'
                else:
                    task_exec.quality_check = 'not_applicable'
                
                task_exec.findings = task_data.get('observation', '')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Report saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@preventive_bp.route('/execution/<int:execution_id>/export-pdf')
@login_required
def export_pdf(execution_id):
    """Export preventive maintenance report as PDF"""
    execution = PreventiveMaintenanceExecution.query.get_or_404(execution_id)
    machine = execution.machine
    task_executions = PreventiveMaintenanceTaskExecution.query.filter_by(
        execution_id=execution_id
    ).order_by(PreventiveMaintenanceTaskExecution.order_number).all()
    
    # Check authorization
    user = User.query.get(session['user_id'])
    if execution.assigned_technician_id != user.id and user.role not in ['admin', 'supervisor']:
        flash('You are not authorized to export this report.', 'danger')
        return redirect(url_for('preventive.executions'))
    
    # Render report for PDF output
    html_report = render_template(
        'preventive_maintenance/report_pdf.html',
        execution=execution,
        machine=machine,
        task_executions=task_executions,
        current_user=user
    )
    
    # Try to use WeasyPrint for better PDF generation
    try:
        from weasyprint import HTML, CSS
        from io import BytesIO
        
        pdf = HTML(string=html_report).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=maintenance_report_{machine.machine_code}_{execution.scheduled_date.strftime("%Y%m%d")}.pdf'
        return response
    except ImportError:
        # Fallback: Return HTML for client-side PDF generation
        flash('Note: PDF will be generated on your browser. Use the Print function and "Save as PDF" option.', 'info')
        return render_template(
            'preventive_maintenance/report_html_for_pdf.html',
            execution=execution,
            machine=machine,
            task_executions=task_executions,
            current_user=user,
            html_content=html_report
        )
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('preventive.execution_detail', execution_id=execution_id))

# ============================================
# STANDALONE PREVENTIVE MAINTENANCE REPORT
# ============================================

@preventive_bp.route('/report', methods=['GET'])
@login_required
def report():
    """Display the standalone preventive maintenance report form (not linked to any execution)"""
    user = User.query.get(session['user_id'])
    
    # Get machines for dropdown
    machines = Machine.query.filter_by(status='active').all()
    
    return render_template(
        'preventive_maintenance/report_form.html',
        machines=machines,
        current_user=user,
        machine=None,
        execution=None
    )

@preventive_bp.route('/report/save', methods=['POST'])
@login_required
def save_report():
    """Save standalone preventive maintenance report"""
    user = User.query.get(session['user_id'])
    
    try:
        # Collect form data
        machine_code = request.form.get('machine_code', '')
        machine_name = request.form.get('machine_name', '')
        execution_date = request.form.get('execution_date', '')
        department = request.form.get('department', '')
        zone = request.form.get('zone', '')
        technician = request.form.get('technician', user.full_name)
        
        overall_findings = request.form.get('overall_findings', '')
        machine_condition = request.form.get('machine_condition', '')
        issues_found = request.form.get('issues_found') == 'on'
        issues_description = request.form.get('issues_description', '')
        spare_parts_needed = request.form.get('spare_parts_needed') == 'on'
        recommendations = request.form.get('recommendations', '')
        
        technician_signature = request.form.get('technician_signature', '')
        supervisor_approval = request.form.get('supervisor_approval', '')
        report_date = request.form.get('report_date', '')
        
        # Parse task data (with user-entered descriptions and frequencies)
        tasks_json = request.form.get('tasks', '[]')
        tasks_data = json.loads(tasks_json)
        
        # Log the report (you can extend this to save to database if needed)
        report_data = {
            'machine_code': machine_code,
            'machine_name': machine_name,
            'execution_date': execution_date,
            'department': department,
            'zone': zone,
            'technician': technician,
            'overall_findings': overall_findings,
            'machine_condition': machine_condition,
            'issues_found': issues_found,
            'issues_description': issues_description,
            'spare_parts_needed': spare_parts_needed,
            'recommendations': recommendations,
            'technician_signature': technician_signature,
            'supervisor_approval': supervisor_approval,
            'report_date': report_date,
            'tasks': tasks_data,  # Includes user-entered descriptions and frequencies
            'saved_by': user.id,
            'saved_at': datetime.utcnow().isoformat()
        }
        
        # For now, just return success
        # In a production system, you might store this in a database
        return jsonify({'success': True, 'message': 'Report saved successfully', 'data': report_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
