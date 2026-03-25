from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Enums
class UserRole(Enum):
    ADMIN = 'admin'
    SUPERVISOR = 'supervisor'
    TECHNICIAN = 'technician'
    STOCK_AGENT = 'stock_agent'

class MaintenanceStatus(Enum):
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    OVERDUE = 'overdue'

class DemandStatus(Enum):
    PENDING = 'pending'
    SUPERVISOR_REVIEW = 'supervisor_review'
    APPROVED_SUPERVISOR = 'approved_supervisor'
    STOCK_AGENT_REVIEW = 'stock_agent_review'
    APPROVED_STOCK_AGENT = 'approved_stock_agent'
    REJECTED = 'rejected'
    PARTIAL_ALLOCATED = 'partial_allocated'
    FULFILLED = 'fulfilled'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'

class ApprovalStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PARTIAL = 'partial'

# Models

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default='technician', index=True)
    department = db.Column(db.String(100))
    zone = db.Column(db.String(100))  # Work zone for technicians
    is_active = db.Column(db.Boolean, default=True, index=True)
    status = db.Column(db.String(50), default='active')
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supervisor = db.relationship('User', remote_side=[id], backref='subordinates', foreign_keys=[supervisor_id])
    maintenance_schedules = db.relationship('MaintenanceSchedule', backref='supervisor', foreign_keys='MaintenanceSchedule.assigned_supervisor_id')
    maintenance_reports = db.relationship('MaintenanceReport', backref='technician', foreign_keys='MaintenanceReport.technician_id')
    demands_created = db.relationship('SparePartsDemand', backref='requestor', foreign_keys='SparePartsDemand.requestor_id')
    demands_supervised = db.relationship('SparePartsDemand', backref='supervisor_user', foreign_keys='SparePartsDemand.supervisor_id')
    demands_stock = db.relationship('SparePartsDemand', backref='stock_agent_user', foreign_keys='SparePartsDemand.stock_agent_id')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Zone(db.Model):
    __tablename__ = 'zones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', backref='zones_created', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<Zone {self.name}>'

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    budget_allocated = db.Column(db.Numeric(15, 2), default=0)
    budget_remaining = db.Column(db.Numeric(15, 2), default=0)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', backref='managed_departments', foreign_keys=[manager_id])
    
    def __repr__(self):
        return f'<Department {self.name}>'

class StockLocation(db.Model):
    __tablename__ = 'stock_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location_code = db.Column(db.String(50), unique=True, nullable=True)
    building = db.Column(db.String(50))
    floor = db.Column(db.Integer)
    warehouse_section = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockLocation {self.name}>'

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    unit = db.Column(db.String(50))
    min_stock = db.Column(db.Integer, default=10)
    max_stock = db.Column(db.Integer, default=100)
    current_stock = db.Column(db.Integer, default=0, index=True)
    reorder_point = db.Column(db.Integer)
    unit_cost = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    last_restocked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier_obj = db.relationship('Supplier', backref='materials')
    demands = db.relationship('SparePartsDemand', backref='material')
    movements = db.relationship('StockMovement', backref='material')
    alerts = db.relationship('StockAlert', backref='material', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Material {self.code}>'
    
    @property
    def stock_status(self):
        if self.current_stock <= self.min_stock:
            return 'critical'
        elif (self.reorder_point and self.current_stock <= self.reorder_point) or self.current_stock > self.max_stock:
            return 'warning'
        return 'normal'

class Machine(db.Model):
    __tablename__ = 'machines'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    machine_name = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    department = db.Column(db.String(100), index=True)
    zone = db.Column(db.String(100), nullable=True, index=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=True, index=True)
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    installation_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maintenance_schedules = db.relationship('MaintenanceSchedule', backref='machine', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Machine {self.machine_code}>'

class MaintenanceSchedule(db.Model):
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True)
    schedule_type = db.Column(db.String(50))
    frequency_days = db.Column(db.Integer)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)
    estimated_duration_hours = db.Column(db.Integer)
    assigned_supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='scheduled', index=True)
    priority = db.Column(db.String(50), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maintenance_reports = db.relationship('MaintenanceReport', backref='schedule', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MaintenanceSchedule {self.id}>'

class MaintenanceReport(db.Model):
    __tablename__ = 'maintenance_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('maintenance_schedules.id', ondelete='CASCADE'), nullable=True)  # nullable for ad-hoc reports
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    machine_name = db.Column(db.String(200))  # Cached machine name for easier access
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    actual_duration_hours = db.Column(db.Float)
    work_description = db.Column(db.Text)
    findings = db.Column(db.Text)
    actions_taken = db.Column(db.Text)
    issues_found = db.Column(db.Boolean, default=False)
    issue_description = db.Column(db.Text)
    components_replaced = db.Column(db.Text)
    next_maintenance_recommendation = db.Column(db.Text)
    report_type = db.Column(db.String(50), default='standard')  # 'standard' or 'detailed'
    report_status = db.Column(db.String(50), default='draft')  # draft, submitted, approved, rejected
    technician_zone = db.Column(db.String(100))  # Zone where technician worked
    machine_condition = db.Column(db.String(50))  # Before maintenance condition
    machine_condition_after = db.Column(db.String(50))  # After maintenance condition
    environmental_conditions = db.Column(db.Text)  # Environmental notes
    safety_observations = db.Column(db.Text)  # Safety observations
    tools_used = db.Column(db.Text)  # Tools used during maintenance
    
    # Supervisor approval fields
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    supervisor_approval_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    supervisor_approval_date = db.Column(db.DateTime)
    supervisor_notes = db.Column(db.Text)
    
    # Checklist data (JSON format for flexibility)
    checklist_data = db.Column(db.Text)  # JSON string with checklist items and results
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    demands = db.relationship('SparePartsDemand', backref='maintenance_report')
    
    def __repr__(self):
        return f'<MaintenanceReport {self.id}>'

class SparePartsDemand(db.Model):
    __tablename__ = 'spare_parts_demands'
    
    id = db.Column(db.Integer, primary_key=True)
    demand_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    maintenance_report_id = db.Column(db.Integer, db.ForeignKey('maintenance_reports.id', ondelete='SET NULL'))
    requestor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    quantity_requested = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(50), default='medium')
    reason = db.Column(db.Text)
    
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    supervisor_approval = db.Column(db.String(50), default='pending')
    supervisor_approval_date = db.Column(db.DateTime)
    supervisor_notes = db.Column(db.Text)
    
    stock_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    stock_agent_approval = db.Column(db.String(50), default='pending')
    stock_agent_approval_date = db.Column(db.DateTime)
    quantity_allocated = db.Column(db.Integer)
    stock_agent_notes = db.Column(db.Text)
    
    # Return tracking
    quantity_returned = db.Column(db.Integer, default=0)  # Material returned to stock
    return_date = db.Column(db.DateTime)
    return_notes = db.Column(db.Text)
    
    demand_status = db.Column(db.String(50), default='pending', index=True)
    fulfilled_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SparePartsDemand {self.demand_number}>'
    
    @property
    def progress_percentage(self):
        if self.demand_status == 'pending':
            return 10
        elif self.demand_status == 'supervisor_review':
            return 20
        elif self.demand_status == 'approved_supervisor':
            return 40
        elif self.demand_status == 'stock_agent_review':
            return 60
        elif self.demand_status == 'approved_stock_agent':
            return 100  # Finished - ready for archive
        elif self.demand_status == 'fulfilled':
            return 100  # Complete
        elif self.demand_status == 'archived':
            return 100  # Archived
        return 0

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movement_type = db.Column(db.String(50), nullable=False)  # 'in', 'out', 'allocated', 'returned', etc.
    quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.id}>'

class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False, index=True)
    alert_type = db.Column(db.String(50))  # 'low_stock', 'overstock', 'critical'
    alert_message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockAlert {self.id}>'

class MaintenanceTemplate(db.Model):
    __tablename__ = 'maintenance_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    frequency = db.Column(db.Integer)  # frequency in days
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='maintenance_templates', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<MaintenanceTemplate {self.name}>'

class DashboardKPI(db.Model):
    __tablename__ = 'dashboard_kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_name = db.Column(db.String(100))
    kpi_value = db.Column(db.Integer)
    kpi_date = db.Column(db.Date, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DashboardKPI {self.kpi_name}>'
class MaterialReturn(db.Model):
    __tablename__ = 'material_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    demand_id = db.Column(db.Integer, db.ForeignKey('spare_parts_demands.id', ondelete='CASCADE'), nullable=False, index=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity_returned = db.Column(db.Integer, nullable=False)
    return_condition = db.Column(db.String(100))
    reason_for_return = db.Column(db.Text)
    returned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    return_status = db.Column(db.String(50), default='pending', index=True)  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    returned_by = db.relationship('User', foreign_keys=[returned_by_id], backref='materials_returned')
    received_by = db.relationship('User', foreign_keys=[received_by_id], backref='materials_received')
    demand = db.relationship('SparePartsDemand')
    
    def __repr__(self):
        return f'<MaterialReturn {self.id}>'

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(15, 2))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft', index=True)  # 'draft', 'ordered', 'received', 'cancelled'
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='purchase_orders')
    material = db.relationship('Material', backref='purchase_orders')
    created_by = db.relationship('User', backref='created_purchase_orders', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'

class DemandApproval(db.Model):
    __tablename__ = 'demand_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    demand_id = db.Column(db.Integer, db.ForeignKey('spare_parts_demands.id', ondelete='CASCADE'), nullable=False, index=True)
    approval_level = db.Column(db.String(50), nullable=False)  # 'supervisor', 'stock_agent'
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_status = db.Column(db.String(50), default='pending')  # 'pending', 'approved', 'rejected'
    approval_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    demand = db.relationship('SparePartsDemand', backref='approvals')
    approver = db.relationship('User', backref='approvals_made', foreign_keys=[approver_id])
    
    def __repr__(self):
        return f'<DemandApproval {self.id}>'

# ============================================
# PREVENTIVE MAINTENANCE MODELS
# ============================================

class PreventiveMaintenancePlan(db.Model):
    """Defines the preventive maintenance plan template for machines"""
    __tablename__ = 'preventive_maintenance_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(150), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True)
    frequency_type = db.Column(db.String(50))  # 'monthly', 'semi-annual', 'annual'
    frequency_days = db.Column(db.Integer)  # Calculate from frequency_type
    description = db.Column(db.Text)
    last_execution = db.Column(db.DateTime)
    next_planned = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    machine = db.relationship('Machine', backref='preventive_plans')
    tasks = db.relationship('PreventiveMaintenanceTask', backref='maintenance_plan', cascade='all, delete-orphan')
    # Note: 'executions' relationship is created via backref from PreventiveMaintenanceExecution.plan
    created_by = db.relationship('User', backref='created_preventive_plans', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<PreventiveMaintenancePlan {self.plan_name}>'

class PreventiveMaintenanceTask(db.Model):
    """Individual tasks that make up a preventive maintenance plan"""
    __tablename__ = 'preventive_maintenance_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('preventive_maintenance_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    task_number = db.Column(db.Integer)  # Order in plan (1, 2, 3, etc)
    task_description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # e.g., 'Electrical', 'Mechanical', 'Hydraulic'
    estimated_duration_minutes = db.Column(db.Integer, default=15)
    required_materials = db.Column(db.Text)  # Comma-separated or JSON list
    safety_precautions = db.Column(db.Text)
    notes = db.Column(db.Text)
    method = db.Column(db.String(10), default='N')  # N (Visual), I (Manual), O (Sensor)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task_executions = db.relationship('PreventiveMaintenanceTaskExecution', backref='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PreventiveMaintenanceTask {self.task_number}: {self.task_description[:30]}>'

class PreventiveMaintenanceExecution(db.Model):
    """Tracks each preventive maintenance execution/report (instance of a plan)"""
    __tablename__ = 'preventive_maintenance_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('preventive_maintenance_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    assigned_supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    execution_date = db.Column(db.Date, index=True)
    
    # Report fields
    status = db.Column(db.String(50), default='scheduled', index=True)  # scheduled, started, completed, cancelled
    report_status = db.Column(db.String(50), default='draft')  # draft, submitted, approved, rejected
    
    overall_findings = db.Column(db.Text)  # General findings and observations
    machine_condition = db.Column(db.String(50))  # e.g., 'good', 'fair', 'needs_repair'
    issues_found = db.Column(db.Boolean, default=False)
    issues_description = db.Column(db.Text)
    recommendations = db.Column(db.Text)  # Next maintenance recommendations
    spare_parts_needed = db.Column(db.Boolean, default=False)
    
    # Supervisor approval
    supervisor_approval_date = db.Column(db.DateTime)
    supervisor_notes = db.Column(db.Text)
    supervision_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    
    # Timing
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    total_duration_minutes = db.Column(db.Integer)  # Calculated
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = db.relationship('PreventiveMaintenancePlan', backref='executions')
    machine = db.relationship('Machine', backref='preventive_executions')
    supervisor = db.relationship('User', foreign_keys=[assigned_supervisor_id], backref='supervised_preventive_executions')
    technician = db.relationship('User', foreign_keys=[assigned_technician_id], backref='executed_preventive_executions')
    task_executions = db.relationship('PreventiveMaintenanceTaskExecution', backref='execution', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PreventiveMaintenanceExecution {self.id} - {self.scheduled_date}>'
    
    @property
    def completion_percentage(self):
        """Calculate percentage of tasks completed"""
        if not self.task_executions:
            return 0
        completed = sum(1 for te in self.task_executions if te.status == 'completed')
        return int((completed / len(self.task_executions)) * 100)

class PreventiveMaintenanceTaskExecution(db.Model):
    """Tracks execution of individual tasks within a maintenance execution"""
    __tablename__ = 'preventive_maintenance_task_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('preventive_maintenance_executions.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('preventive_maintenance_tasks.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    order_number = db.Column(db.Integer)  # Task sequence number
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, skipped, unable_to_complete
    
    # Timing
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    actual_duration_minutes = db.Column(db.Integer)  # Calculated
    
    # Execution details
    findings = db.Column(db.Text)  # What was found/observed
    actions_taken = db.Column(db.Text)  # What was done
    issues_encountered = db.Column(db.Text)  # Any issues or problems
    materials_used = db.Column(db.Text)  # Materials/parts used (can link to inventory)
    completion_notes = db.Column(db.Text)  # General notes
    
    # Quality/verification
    quality_check = db.Column(db.String(50), default='passed')  # passed, failed, not_applicable
    quality_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    technician = db.relationship('User', backref='executed_preventive_tasks', foreign_keys=[technician_id])
    
    def __repr__(self):
        return f'<PreventiveMaintenanceTaskExecution {self.order_number}: {self.status}>'
    
    @property
    def duration_minutes(self):
        """Calculate duration if both start and end times exist"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return None


class MachineStatus(db.Model):
    """Tracks the current real-time status of each machine from Raspberry Pi"""
    __tablename__ = 'machine_status'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    machine_name = db.Column(db.String(200))  # Cache of machine name for quick access
    current_status = db.Column(db.String(50), default='working')  # working, downtime, maintenance, break, offline
    status_since = db.Column(db.DateTime, default=datetime.utcnow)  # When current status started
    last_event_type = db.Column(db.String(50))  # Type of last event
    last_user_start = db.Column(db.String(100))  # User ID who started current event
    last_user_end = db.Column(db.String(100))  # User ID who ended last event
    last_comment = db.Column(db.Text)  # Last comment or note
    power_status = db.Column(db.String(20), default='on')  # on or off
    
    # Timing
    cumulative_downtime_today = db.Column(db.Float, default=0)  # Total downtime hours today
    current_downtime_duration = db.Column(db.Float, default=0)  # Current downtime duration in seconds
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    machine = db.relationship('Machine', backref='status_tracker', foreign_keys=[machine_id])
    
    def __repr__(self):
        return f'<MachineStatus {self.machine_name}: {self.current_status}>'


class MachineEvent(db.Model):
    """Tracks all events from the Raspberry Pi (downtime, maintenance, break, etc.)"""
    __tablename__ = 'machine_events'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True)
    machine_name = db.Column(db.String(200))  # Cache for quick access
    event_type = db.Column(db.String(50), nullable=False)  # downtime, maintenance, break, breakdown, power_cut
    event_status = db.Column(db.String(50), default='started')  # started, ended, cancelled
    
    # User tracking
    start_user_id = db.Column(db.String(100))  # User ID who triggered event
    end_user_id = db.Column(db.String(100))  # User ID who ended event
    
    # Event details
    start_comment = db.Column(db.Text)  # Comment when event started
    end_comment = db.Column(db.Text)  # Comment when event ended
    cancel_reason = db.Column(db.Text)  # Reason if event was cancelled
    breakdown_type = db.Column(db.String(100))  # For maintenance: Curative/Corrective/Preventive
    
    # Timing
    event_start_time = db.Column(db.DateTime, nullable=False)
    event_end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Float)  # Total duration in seconds
    reaction_time_seconds = db.Column(db.Float)  # For breakdown: time until maintenance arrived
    maintenance_arrival_time = db.Column(db.DateTime)  # When maintenance team arrived
    maintenance_arrival_user_id = db.Column(db.String(100))  # Who arrived
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    machine = db.relationship('Machine', backref='events', foreign_keys=[machine_id])
    
    def __repr__(self):
        return f'<MachineEvent {self.machine_name}: {self.event_type} at {self.event_start_time}>'
    
    @property
    def duration_hours(self):
        """Get duration in hours"""
        if self.duration_seconds:
            return self.duration_seconds / 3600
        return 0
    
    @property
    def reaction_time_minutes(self):
        """Get reaction time in minutes"""
        if self.reaction_time_seconds:
            return self.reaction_time_seconds / 60
        return 0