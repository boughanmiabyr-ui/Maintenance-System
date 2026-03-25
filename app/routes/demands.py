from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.models import db, SparePartsDemand, Material, User, MaintenanceReport
from app.routes.auth import login_required, role_required
from app.email_service import EmailService
from datetime import datetime, timedelta
import uuid
import logging
import threading
import time

logger = logging.getLogger(__name__)

demands_bp = Blueprint('demands', __name__, url_prefix='/demands')

def generate_demand_number():
    """Generate unique demand number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:6].upper()
    return f'DEM-{timestamp}-{unique_id}'


def _get_group_base(demand_number):
    """Return the base group for a demand_number (strip -A suffix if present)"""
    if not demand_number:
        return demand_number
    if '-' in demand_number:
        parts = demand_number.rsplit('-', 1)
        if len(parts[1]) == 1 and parts[1].isalpha():
            return parts[0]
    return demand_number


def _schedule_stock_agent_email_reminder(base_demand_number, stock_agent_id, interval=60):
    """Send reminder emails to a stock agent every `interval` seconds.

    This helper functions similarly to the supervisor reminder but targets a
    specific stock agent and only runs while the demand status indicates it is
    waiting for stock allocation (either 'approved_supervisor' or
    'stock_agent_review').
    """
    app = current_app._get_current_object()

    def _run_cycle():
        for remaining in range(interval, 0, -1):
            print(f"[StockReminder] sending in {remaining} second{'s' if remaining != 1 else ''}...")
            time.sleep(1)
        with app.app_context():
            items = SparePartsDemand.query.filter(
                (SparePartsDemand.demand_number == base_demand_number) |
                (SparePartsDemand.demand_number.like(f"{base_demand_number}-%"))
            ).all()
            if not items:
                return
            rep = sorted(items, key=lambda x: x.created_at, reverse=True)[0]
            agent = User.query.get(stock_agent_id)
            if agent and rep.demand_status in ['approved_supervisor', 'stock_agent_review']:
                EmailService.send_stock_agent_notification(rep, agent)
                print(f"[StockReminder] resent agent notification for {rep.demand_number} to {agent.email}")
                threading.Thread(target=_run_cycle, daemon=True).start()
    threading.Thread(target=_run_cycle, daemon=True).start()


def _schedule_supervisor_email_reminder(base_demand_number, supervisor_id, interval=60):
    """Send reminder emails at a fixed `interval` (seconds) as long as the demand
    group status stays pending/supervisor_review.

    A dedicated thread runs a simple countdown showing remaining seconds before
    each send.  Once countdown hits zero the same approval-request email is
    dispatched; if the demand is still awaiting supervisor, the cycle starts
    over with another countdown.
    """
    app = current_app._get_current_object()

    def _run_cycle():
        # countdown loop
        for remaining in range(interval, 0, -1):
            print(f"[Reminder] sending in {remaining} second{'s' if remaining != 1 else ''}...")
            time.sleep(1)
        with app.app_context():
            items = SparePartsDemand.query.filter(
                (SparePartsDemand.demand_number == base_demand_number) |
                (SparePartsDemand.demand_number.like(f"{base_demand_number}-%"))
            ).all()
            if not items:
                return
            rep = sorted(items, key=lambda x: x.created_at, reverse=True)[0]
            supervisor = User.query.get(supervisor_id)
            if supervisor and rep.demand_status in ['pending', 'supervisor_review']:
                EmailService.send_supervisor_approval_request(rep, supervisor)
                print(f"[Reminder] resent approval request for {rep.demand_number} to {supervisor.email}")
                # start next countdown cycle
                threading.Thread(target=_run_cycle, daemon=True).start()
    # kick off first cycle in background
    threading.Thread(target=_run_cycle, daemon=True).start()


def archive_old_finished_demands(hours=1):
    """
    Automatically archive demands that have been in finished state for more than N hours.
    
    Finished states: approved_stock_agent, fulfilled, rejected, cancelled
    
    Args:
        hours: Number of hours a demand must be finished before auto-archiving (default: 1)
    
    Returns:
        int: Number of demands archived
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Find all finished demands that haven't been archived and are older than cutoff
    old_finished = SparePartsDemand.query.filter(
        SparePartsDemand.demand_status.in_(['approved_stock_agent', 'fulfilled', 'rejected', 'cancelled']),
        SparePartsDemand.updated_at <= cutoff_time,
        SparePartsDemand.archive_date.is_(None)
    ).all()
    
    archived_count = 0
    for demand in old_finished:
        # Archive all items in the same demand group
        base = _get_group_base(demand.demand_number)
        items = SparePartsDemand.query.filter(
            (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
        ).all()
        
        for it in items:
            it.demand_status = 'archived'
            it.archive_date = datetime.utcnow()
        
        archived_count += 1
    
    if archived_count > 0:
        db.session.commit()
        logger.info(f"Auto-archived {archived_count} finished demand groups")
    
    return archived_count

@demands_bp.route('/')
@login_required
def list_demands():
    # Auto-archive finished demands older than 1 hour
    archive_old_finished_demands(hours=1)
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    show_archived = request.args.get('show_archived', 'false').lower() == 'true'
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    query = SparePartsDemand.query
    
    # Exclude archived demands by default
    if not show_archived:
        query = query.filter(SparePartsDemand.demand_status != 'archived')
    
    # Filter based on user role
    if user.role == 'technician':
        # Technicians see their own demands
        query = query.filter_by(requestor_id=user_id)
    elif user.role == 'supervisor':
        # Supervisors see their own demands + demands assigned to them
        query = query.filter(
            (SparePartsDemand.requestor_id == user_id) |
            (SparePartsDemand.supervisor_id == user_id)
        )
    elif user.role == 'stock_agent':
        # Stock agents see demands assigned to them + pending (no supervisor) + approved by supervisor
        query = query.filter(
            (SparePartsDemand.stock_agent_id == user_id) |
            (SparePartsDemand.demand_status == 'pending') |
            (SparePartsDemand.demand_status == 'approved_supervisor') |
            (SparePartsDemand.demand_status == 'stock_agent_review')
        )
    
    if status_filter:
        query = query.filter_by(demand_status=status_filter)
    
    # Retrieve matching demands and group by base demand number (strip per-item suffix)
    all_demands = query.order_by(SparePartsDemand.created_at.desc()).all()
    groups = {}
    for d in all_demands:
        dn = d.demand_number or ''
        # If demand_number ends with -<single letter> treat that as per-item suffix
        if '-' in dn:
            parts = dn.rsplit('-', 1)
            if len(parts[1]) == 1 and parts[1].isalpha():
                base = parts[0]
            else:
                base = dn
        else:
            base = dn

        groups.setdefault(base, []).append(d)

    grouped = []
    for base, items in groups.items():
        # Representative demand (most recent) for header
        rep = sorted(items, key=lambda x: x.created_at, reverse=True)[0]
        rep.items = items
        rep.total_quantity = sum(i.quantity_requested for i in items)
        rep.group_base = base
        grouped.append(rep)

    # Simple in-memory pagination for grouped list
    per_page = 20
    total = len(grouped)
    start = (page - 1) * per_page
    end = start + per_page
    paged_items = grouped[start:end]

    class SimplePager:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
        def iter_pages(self):
            return range(1, self.pages + 1)

    demands = SimplePager(paged_items, page, per_page, total)
    
    # Status counts
    all_demands_query = SparePartsDemand.query
    if not show_archived:
        all_demands_query = all_demands_query.filter(SparePartsDemand.demand_status != 'archived')
    
    if user.role == 'technician':
        all_demands_query = all_demands_query.filter_by(requestor_id=user_id)
    elif user.role == 'supervisor':
        all_demands_query = all_demands_query.filter(
            (SparePartsDemand.requestor_id == user_id) |
            (SparePartsDemand.supervisor_id == user_id)
        )
    
    status_counts = {}
    for status in ['pending', 'supervisor_review', 'approved_supervisor', 'stock_agent_review', 'approved_stock_agent', 'fulfilled']:
        status_counts[status] = all_demands_query.filter_by(demand_status=status).count()
    
    # Count archived demands
    archived_count = SparePartsDemand.query.filter_by(demand_status='archived').count()
    
    return render_template(
        'demands/list.html',
        demands=demands,
        status_filter=status_filter,
        status_counts=status_counts,
        show_archived=show_archived,
        archived_count=archived_count
    )

@demands_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('technician', 'supervisor', 'stock_agent')
def create_demand():
    if request.method == 'POST':
        materials_data = request.form.getlist('material_id')
        quantities_data = request.form.getlist('quantity')
        
        user = User.query.get(session['user_id'])
        
        # Get supervisor from user's supervisor_id field (set during registration)
        supervisor_id = None
        demand_status = 'pending'
        
        if user.role == 'technician' and user.supervisor_id:
            # If technician has assigned supervisor, route to supervisor
            supervisor_id = user.supervisor_id
            demand_status = 'supervisor_review'
        elif user.role == 'technician':
            # If technician has no supervisor, route directly to stock agent
            demand_status = 'pending'

        # Validate requested quantities against current stock to prevent over-requesting
        for material_id, quantity in zip(materials_data, quantities_data):
            if not material_id or not quantity:
                continue

            material = Material.query.get(material_id)
            if not material:
                flash(f'Material {material_id} not found.', 'danger')
                return redirect(url_for('demands.create_demand'))

            try:
                qty = int(quantity)
            except ValueError:
                flash(f'Invalid quantity for {material.name}.', 'danger')
                return redirect(url_for('demands.create_demand'))

            if qty > material.current_stock:
                flash(
                    f'Requested quantity for "{material.name}" ({qty}) exceeds available stock ({material.current_stock}).',
                    'danger'
                )
                return redirect(url_for('demands.create_demand'))

        # Create a base demand number and append suffixes (A, B, C...) per item
        base_demand_number = generate_demand_number()
        for idx, (material_id, quantity) in enumerate(zip(materials_data, quantities_data)):
            if not material_id or not quantity:
                continue
            
            material = Material.query.get(material_id)
            if not material:
                flash(f'Material {material_id} not found.', 'danger')
                continue
            # ensure unique demand_number per row by adding a letter suffix
            suffix = chr(65 + (idx % 26))
            demand_number = f"{base_demand_number}-{suffix}"

            demand = SparePartsDemand(
                demand_number=demand_number,
                maintenance_report_id=request.form.get('maintenance_report_id'),
                requestor_id=session['user_id'],
                material_id=material_id,
                quantity_requested=int(quantity),
                priority=request.form.get('priority', 'medium'),
                reason=request.form.get('reason'),
                supervisor_id=supervisor_id,
                demand_status=demand_status
            )
            
            db.session.add(demand)
        
        db.session.commit()
        
        # Send email notifications (grouped) to avoid one email per material
        email_errors = []
        created_demands = SparePartsDemand.query.filter_by(requestor_id=session['user_id']).order_by(SparePartsDemand.created_at.desc()).limit(len(materials_data)).all()
        try:
            # If supervisor route is used, group and send one email to supervisor
            if supervisor_id:
                supervisor = User.query.get(supervisor_id) if supervisor_id else None
                if supervisor:
                    EmailService.send_bulk_supervisor_approval_request(created_demands, supervisor)
                    # schedule reminder emails every minute until status changes
                    base = _get_group_base(created_demands[0].demand_number) if created_demands else None
                    if base:
                        _schedule_supervisor_email_reminder(base, supervisor_id, interval=60)
            else:
                # Send grouped notification to each stock agent
                stock_agents = User.query.filter_by(role='stock_agent').all()
                for stock_agent in stock_agents:
                    EmailService.send_bulk_stock_agent_notification(created_demands, stock_agent)
        except Exception as e:
            email_errors.append(f"Failed to send grouped notification emails: {str(e)}")
            current_app.logger.error(f"Grouped email error for demands: {str(e)}")
        
        success_msg = 'Demand(s) created successfully!'
        if email_errors:
            success_msg += ' (Note: Some notification emails could not be sent)'
            logger.warning(f"Email sending errors: {email_errors}")
        
        flash(success_msg, 'success')
        return redirect(url_for('demands.list_demands'))
    
    materials = Material.query.all()
    maintenance_reports = MaintenanceReport.query.filter_by(report_status='approved').all()
    
    return render_template(
        'demands/create.html',
        materials=materials,
        maintenance_reports=maintenance_reports
    )

@demands_bp.route('/<int:demand_id>')
@login_required
def detail(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])

    # If this demand is part of a grouped request, fetch all items in the group
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).order_by(SparePartsDemand.created_at.desc()).all()

    if items and len(items) > 1:
        rep = items[0]
        rep.items = items
        rep.total_quantity = sum(i.quantity_requested for i in items)
        demand = rep

    # Check if user has permission to view
    has_permission = (
        user.role == 'admin' or
        demand.requestor_id == user.id or
        (demand.supervisor_id and demand.supervisor_id == user.id) or
        (demand.stock_agent_id and demand.stock_agent_id == user.id)
    )

    # Stock agents can view demands ready for their approval (no stock agent assigned yet)
    if user.role == 'stock_agent' and not demand.stock_agent_id and demand.demand_status in ['pending', 'approved_supervisor']:
        has_permission = True

    if not has_permission:
        flash('You do not have permission to view this demand.', 'danger')
        return redirect(url_for('demands.list_demands'))

    return render_template('demands/detail.html', demand=demand, user=user)


@demands_bp.route('/<int:demand_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('technician', 'admin')
def edit_demand(demand_id):
    """Allow the original requestor to modify a demand before supervisor approval."""
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])

    # Determine the group base
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).order_by(SparePartsDemand.created_at.desc()).all()

    if not items:
        flash('Demand not found.', 'danger')
        return redirect(url_for('demands.list_demands'))

    # Representative demand for group fields
    rep = items[0]
    rep.items = items

    # Only the original requestor (or admin) can edit while awaiting supervisor approval
    if user.role != 'admin' and rep.requestor_id != user.id:
        flash('You do not have permission to edit this demand.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))

    if rep.demand_status not in ['pending', 'supervisor_review']:
        flash('This demand cannot be edited at this stage.', 'warning')
        return redirect(url_for('demands.detail', demand_id=demand_id))

    materials = Material.query.all()

    if request.method == 'POST':
        material_ids = request.form.getlist('material_id')
        quantities = request.form.getlist('quantity')
        priority = request.form.get('priority', rep.priority)
        reason = request.form.get('reason', rep.reason)

        # Validate the requester's ability to update quantities
        for material_id, quantity in zip(material_ids, quantities):
            if not material_id or not quantity:
                continue

            material = Material.query.get(material_id)
            if not material:
                flash(f'Material {material_id} not found.', 'danger')
                return redirect(url_for('demands.edit_demand', demand_id=demand_id))

            try:
                qty_int = int(quantity)
            except ValueError:
                flash('Invalid quantity provided.', 'danger')
                return redirect(url_for('demands.edit_demand', demand_id=demand_id))

            if qty_int < 1:
                flash('Quantity must be at least 1.', 'danger')
                return redirect(url_for('demands.edit_demand', demand_id=demand_id))

            if qty_int > material.current_stock:
                flash(
                    f'Requested quantity for "{material.name}" ({qty_int}) exceeds available stock ({material.current_stock}).',
                    'danger'
                )
                return redirect(url_for('demands.edit_demand', demand_id=demand_id))

        # Rebuild the demand group from submitted values (easy way to allow changing materials/quantities)
        SparePartsDemand.query.filter(
            (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
        ).delete(synchronize_session=False)

        # Recreate demand items using the same base demand number
        for idx, (material_id, quantity) in enumerate(zip(material_ids, quantities)):
            if not material_id or not quantity:
                continue

            suffix = chr(65 + (idx % 26))
            demand_number = f"{base}-{suffix}"

            demand_item = SparePartsDemand(
                demand_number=demand_number,
                maintenance_report_id=rep.maintenance_report_id,
                requestor_id=rep.requestor_id,
                material_id=material_id,
                quantity_requested=int(quantity),
                priority=priority,
                reason=reason,
                supervisor_id=rep.supervisor_id,
                demand_status=rep.demand_status
            )
            db.session.add(demand_item)

        db.session.commit()

        flash('Demand updated successfully.', 'success')
        # Redirect to the group detail page (use the first item for URL)
        first_item = SparePartsDemand.query.filter(
            SparePartsDemand.demand_number.like(f"{base}-%")
        ).order_by(SparePartsDemand.created_at).first()
        return redirect(url_for('demands.detail', demand_id=first_item.id if first_item else demand_id))

    return render_template(
        'demands/edit.html',
        demand=rep,
        items=items,
        materials=materials
    )

@demands_bp.route('/<int:demand_id>/supervisor-approve', methods=['POST'])
@login_required
@role_required('supervisor', 'admin')
def supervisor_approve(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Check if supervisor is assigned to this demand
    if user.role == 'supervisor' and demand.supervisor_id != user.id:
        flash('This demand is not assigned to you.', 'danger')
        return redirect(url_for('demands.list_demands'))
    
    if demand.demand_status not in ['pending', 'supervisor_review']:
        flash('This demand cannot be approved at this stage.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Approve all items in the same demand group
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.supervisor_id = session['user_id']
        it.supervisor_approval = 'approved'
        it.supervisor_approval_date = datetime.utcnow()
        it.supervisor_notes = request.form.get('notes', '')
        it.demand_status = 'approved_supervisor'

    db.session.commit()

    # Send notifications (non-blocking) once for the group (use representative)
    rep = items[0] if items else demand
    try:
        EmailService.send_supervisor_decision_notification(rep, 'approved', rep.supervisor_notes)
        stock_agents = User.query.filter_by(role='stock_agent').all()
        for stock_agent in stock_agents:
            EmailService.send_stock_agent_notification(rep, stock_agent)
            # start reminder countdown for this agent until they take action
            _schedule_stock_agent_email_reminder(base, stock_agent.id, interval=60)
    except Exception as e:
        logger.warning(f"Failed to send approval emails for demand group {base}: {str(e)}")
    
    flash('Demand approved by supervisor!', 'success')
    return redirect(url_for('demands.detail', demand_id=demand_id))

@demands_bp.route('/<int:demand_id>/supervisor-reject', methods=['POST'])
@login_required
@role_required('supervisor', 'admin')
def supervisor_reject(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Check if supervisor is assigned to this demand
    if user.role == 'supervisor' and demand.supervisor_id != user.id:
        flash('This demand is not assigned to you.', 'danger')
        return redirect(url_for('demands.list_demands'))
    
    if demand.demand_status not in ['pending', 'supervisor_review']:
        flash('This demand cannot be rejected at this stage.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Reject all items in the same demand group
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.supervisor_id = session['user_id']
        it.supervisor_approval = 'rejected'
        it.supervisor_approval_date = datetime.utcnow()
        it.supervisor_notes = request.form.get('notes', '')
        it.demand_status = 'rejected'

    db.session.commit()

    # Send rejection notification once for the group
    rep = items[0] if items else demand
    try:
        EmailService.send_supervisor_decision_notification(rep, 'rejected', rep.supervisor_notes)
    except Exception as e:
        logger.warning(f"Failed to send rejection email for demand group {base}: {str(e)}")
    
    flash('Demand rejected by supervisor.', 'warning')
    return redirect(url_for('demands.detail', demand_id=demand_id))

@demands_bp.route('/<int:demand_id>/stock-review', methods=['POST'])
@login_required
@role_required('stock_agent', 'admin')
def stock_agent_review(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Only allow if:
    # 1. This is an admin, OR
    # 2. No stock agent is assigned yet
    if user.role == 'stock_agent' and demand.stock_agent_id:
        flash('This demand is already assigned to another stock agent. You cannot modify it.', 'danger')
        return redirect(url_for('demands.list_demands'))
    
    # Accept either pending (no supervisor) or approved_supervisor (supervisor already approved)
    if demand.demand_status not in ['pending', 'approved_supervisor']:
        flash('This demand is not ready for stock agent review.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Move entire group to stock agent review
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.stock_agent_id = session['user_id']
        it.demand_status = 'stock_agent_review'

    db.session.commit()
    # schedule reminders for the assigned stock agent until they process the group
    base = _get_group_base(demand.demand_number)
    if base:
        _schedule_stock_agent_email_reminder(base, session['user_id'], interval=60)
    flash('Demand group moved to stock agent review.', 'info')
    return redirect(url_for('demands.detail', demand_id=demand_id))

@demands_bp.route('/<int:demand_id>/stock-approve', methods=['POST'])
@login_required
@role_required('stock_agent', 'admin')
def stock_agent_approve(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Only allow approval if:
    # 1. This is an admin, OR
    # 2. No stock agent is assigned yet (new demand), OR
    # 3. This stock agent is already assigned
    if user.role == 'stock_agent' and demand.stock_agent_id and demand.stock_agent_id != user.id:
        flash('This demand is already assigned to another stock agent. You cannot modify it.', 'danger')
        return redirect(url_for('demands.list_demands'))
    
    if demand.demand_status not in ['pending', 'approved_supervisor', 'stock_agent_review']:
        flash('Invalid demand status for approval.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Approve and allocate for entire demand group; process each material row
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    from app.models import StockMovement
    total_allocated = 0
    processed = []
    for it in items:
        material = Material.query.get(it.material_id)
        if not material:
            continue
        qty_req = it.quantity_requested
        qty_alloc = min(qty_req, material.current_stock)
        if qty_alloc > 0:
            material.current_stock -= qty_alloc
            movement = StockMovement(
                material_id=material.id,
                movement_type='fulfilled',
                quantity=qty_alloc,
                reference_id=f"demand-{it.id}",
                user_id=session['user_id'],
                notes=f'Allocated for demand {it.demand_number}'
            )
            db.session.add(movement)

            # If stock has reached or fallen below minimum, send alert email to stock agents
            if material.current_stock <= (material.min_stock or 0):
                from app.email_service import EmailService
                try:
                    EmailService.send_low_stock_alert(material, material.current_stock)
                except Exception as e:
                    logger.warning(f"Failed to send low stock alert for material {material.id}: {str(e)}")

        it.stock_agent_id = session['user_id']
        it.stock_agent_approval = 'approved' if qty_alloc == qty_req else ('partial' if qty_alloc > 0 else 'rejected')
        it.quantity_allocated = qty_alloc
        it.stock_agent_approval_date = datetime.utcnow()
        it.stock_agent_notes = request.form.get('notes', '')
        it.demand_status = 'approved_stock_agent' if qty_alloc == qty_req else ('partial_allocated' if qty_alloc > 0 else 'rejected')
        it.fulfilled_date = datetime.utcnow() if qty_alloc > 0 else it.fulfilled_date

        total_allocated += qty_alloc
        processed.append(it)

    db.session.commit()

    # Notify once for the group (use representative)
    rep = processed[0] if processed else demand
    try:
        EmailService.send_allocation_notification(rep, rep.requestor)
    except Exception as e:
        logger.warning(f"Failed to send allocation email for demand group {base}: {str(e)}")

    flash(f'Demand group processed. Total allocated: {total_allocated} units. Stock updated.', 'success')
    # Redirect to inventory so the stock list reflects the updated quantities immediately
    return redirect(url_for('stock.inventory'))

@demands_bp.route('/<int:demand_id>/stock-reject', methods=['POST'])
@login_required
@role_required('stock_agent', 'admin')
def stock_agent_reject(demand_id):
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Only allow rejection if:
    # 1. This is an admin, OR
    # 2. No stock agent is assigned yet (new demand), OR
    # 3. This stock agent is already assigned
    if user.role == 'stock_agent' and demand.stock_agent_id and demand.stock_agent_id != user.id:
        flash('This demand is already assigned to another stock agent. You cannot modify it.', 'danger')
        return redirect(url_for('demands.list_demands'))
    
    if demand.demand_status not in ['pending', 'approved_supervisor', 'stock_agent_review']:
        flash('Invalid demand status for rejection.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Reject entire demand group
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.stock_agent_id = session['user_id']
        it.stock_agent_approval = 'rejected'
        it.stock_agent_approval_date = datetime.utcnow()
        it.stock_agent_notes = request.form.get('notes', '')
        it.demand_status = 'rejected'

    db.session.commit()

    # Send rejection notification once for the group (notify technician)
    rep = items[0] if items else demand
    try:
        EmailService.send_stock_agent_decision_notification(rep, 'rejected', rep.stock_agent_notes)
    except Exception as e:
        logger.warning(f"Failed to send stock agent rejection email for demand group {base}: {str(e)}")

    flash('Demand group rejected by stock agent. Technician has been notified.', 'warning')
    return redirect(url_for('demands.detail', demand_id=demand_id))

@demands_bp.route('/<int:demand_id>/archive', methods=['POST'])
@login_required
@role_required('stock_agent', 'supervisor', 'admin')
def archive_demand(demand_id):
    """Archive a finished (fulfilled) demand."""
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Check permission - user should be able to archive their own associated demands
    has_permission = (
        user.role == 'admin' or
        demand.requested_by_id == user.id or
        (hasattr(demand, 'supervisor_id') and demand.supervisor_id == user.id) or
        (hasattr(demand, 'stock_agent_id') and demand.stock_agent_id == user.id)
    )
    
    if not has_permission:
        flash('You do not have permission to archive this demand.', 'danger')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Only allow archiving fulfilled or rejected demands
    if demand.demand_status not in ['fulfilled', 'approved_stock_agent', 'rejected', 'cancelled']:
        flash('Only finished demands (fulfilled, rejected, or cancelled) can be archived.', 'warning')
        return redirect(url_for('demands.detail', demand_id=demand_id))
    
    # Archive all items in the same demand group
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.demand_status = 'archived'
        it.archive_date = datetime.utcnow()

    db.session.commit()

    flash(f'Demand group {base} has been archived and removed from active list.', 'success')
    return redirect(url_for('demands.list_demands'))

@demands_bp.route('/archived')
@login_required
def archived_demands():
    """View archived demands with filtering options."""
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date_filter', '')  # Filter by archive date range
    original_status = request.args.get('original_status', '')  # Filter by status before archiving
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Start query - only archived demands
    query = SparePartsDemand.query.filter_by(demand_status='archived')
    
    # Filter based on user role (same logic as list_demands)
    if user.role == 'technician':
        query = query.filter_by(requested_by_id=user_id)
    elif user.role == 'supervisor':
        query = query.filter(
            (SparePartsDemand.requested_by_id == user_id) |
            (SparePartsDemand.supervisor_id == user_id)
        )
    elif user.role == 'stock_agent':
        query = query.filter(
            (SparePartsDemand.stock_agent_id == user_id) |
            (SparePartsDemand.requested_by_id == user_id)
        )
    
    # Filter by archive date if provided
    if date_filter:
        if date_filter == 'today':
            from datetime import date
            today = date.today()
            query = query.filter(SparePartsDemand.archive_date >= f'{today} 00:00:00')
        elif date_filter == 'week':
            from datetime import datetime, timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            query = query.filter(SparePartsDemand.archive_date >= week_ago)
        elif date_filter == 'month':
            from datetime import datetime, timedelta
            month_ago = datetime.utcnow() - timedelta(days=30)
            query = query.filter(SparePartsDemand.archive_date >= month_ago)
    
    # Retrieve matching archived demands and group by base demand number
    all_archived = query.order_by(SparePartsDemand.archive_date.desc()).all()
    groups = {}
    for d in all_archived:
        dn = d.demand_number or ''
        if '-' in dn:
            parts = dn.rsplit('-', 1)
            if len(parts[1]) == 1 and parts[1].isalpha():
                base = parts[0]
            else:
                base = dn
        else:
            base = dn

        groups.setdefault(base, []).append(d)

    grouped = []
    for base, items in groups.items():
        rep = sorted(items, key=lambda x: x.archive_date, reverse=True)[0]
        rep.items = items
        rep.total_quantity = sum(i.quantity_requested for i in items)
        rep.group_base = base
        grouped.append(rep)

    # Pagination
    per_page = 20
    total = len(grouped)
    start = (page - 1) * per_page
    end = start + per_page
    paged_items = grouped[start:end]

    class SimplePager:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
        def iter_pages(self):
            return range(1, self.pages + 1)

    demands = SimplePager(paged_items, page, per_page, total)
    
    return render_template(
        'demands/archived.html',
        demands=demands,
        date_filter=date_filter,
        total_archived=total
    )

@demands_bp.route('/archived/<int:demand_id>/restore', methods=['POST'])
@login_required
@role_required('stock_agent', 'supervisor', 'admin')
def restore_archived_demand(demand_id):
    """Restore an archived demand back to its previous status."""
    demand = SparePartsDemand.query.get_or_404(demand_id)
    user = User.query.get(session['user_id'])
    
    # Check permission
    has_permission = (
        user.role == 'admin' or
        demand.requested_by_id == user.id or
        (hasattr(demand, 'supervisor_id') and demand.supervisor_id == user.id) or
        (hasattr(demand, 'stock_agent_id') and demand.stock_agent_id == user.id)
    )
    
    if not has_permission:
        flash('You do not have permission to restore this demand.', 'danger')
        return redirect(url_for('demands.archived_demands'))
    
    if demand.demand_status != 'archived':
        flash('This demand is not archived.', 'warning')
        return redirect(url_for('demands.archived_demands'))
    
    # Restore to fulfilled status (the most common state for archived demands)
    base = _get_group_base(demand.demand_number)
    items = SparePartsDemand.query.filter(
        (SparePartsDemand.demand_number == base) | (SparePartsDemand.demand_number.like(f"{base}-%"))
    ).all()

    for it in items:
        it.demand_status = 'fulfilled'
        it.archive_date = None

    db.session.commit()

    flash(f'Demand group {base} has been restored to active list.', 'success')
    return redirect(url_for('demands.detail', demand_id=demand_id))

@demands_bp.route('/admin/auto-archive', methods=['POST'])
@login_required
@role_required('admin')
def trigger_auto_archive():
    """
    Admin endpoint to manually trigger automatic archival of old finished demands.
    This is useful for testing or explicit control over the archival process.
    """
    hours = request.args.get('hours', 1, type=int)
    archived_count = archive_old_finished_demands(hours=hours)
    
    flash(f'Auto-archive completed: {archived_count} demand groups archived.', 'info')
    return redirect(url_for('demands.list_demands'))
