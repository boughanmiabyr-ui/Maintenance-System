"""
Email Service Module for notifications
Handles sending emails for demands, approvals, rejections, etc.
"""
import logging
from flask import current_app
from flask_mail import Mail, Message

# Configure logging for email service
logger = logging.getLogger('EmailService')
if not logger.handlers:
    # Create file handler
    fh = logging.FileHandler('email_logs.log')
    fh.setLevel(logging.DEBUG)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

# Initialize Mail object (will be initialized in app context)
mail = Mail()

# Import User model - done here to avoid circular imports
def get_user_model():
    """Lazy import to avoid circular dependencies"""
    from app.models import User
    return User


class EmailService:
    """Service to handle email notifications - simplified version matching gmailtest.py approach"""
    
    @staticmethod
    def send_email(recipients, subject, html_body, text_body=None):
        """
        Send email to one or more recipients using Flask-Mail
        Simple, direct approach matching gmailtest.py
        
        Args:
            recipients: str or list of email addresses
            subject: Email subject
            html_body: HTML version of email body
            text_body: Plain text version (optional)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not current_app.config.get('EMAILS_ENABLED', True):
            logger.info(f"Email sending disabled. Skipping email: {subject}")
            return False
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        sender = current_app.config['MAIL_USERNAME']
        recipients_str = ', '.join(recipients)
        
        try:
            logger.info(f"========== EMAIL SEND REQUEST STARTED ==========")
            logger.info(f"Mail server: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
            logger.info(f"Using TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Username: {current_app.config['MAIL_USERNAME']}")
            
            logger.info("Preparing email message...")
            logger.info(f"  - To: {recipients_str}")
            logger.info(f"  - Subject: {subject}")
            
            # Create message using Flask-Mail (simple approach like gmailtest.py)
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                sender=sender
            )
            logger.info("Message object created successfully")
            
            logger.info("Attempting to send email via SMTP...")
            mail.send(msg)
            logger.info("Email sent successfully to SMTP server")
            
            logger.info(f"========== EMAIL SEND COMPLETED ==========")
            return True
            
        except Exception as e:
            logger.error(f"========== EMAIL SEND FAILED ==========")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error("Full traceback:", exc_info=True)
            return False
    
    @staticmethod
    def _get_logo_html():
        """Generate HTML img tag with logo URL from config"""
        logo_url = current_app.config.get('LOGO_URL')
        if logo_url and 'YOUR_USERNAME' not in logo_url:
            return f'<img src="{logo_url}" alt="Sumitomo Wiring Systems" style="max-width: 150px; height: auto; margin-bottom: 15px;">'
        return ""
    
    @staticmethod
    def _create_email_template(
        title,
        message,
        details=None,
        action_button=False,
        action_url="",
        action_text="",
        highlight_color="#4c6ef5",
        secondary_action_button=False,
        secondary_action_url="",
        secondary_action_text="",
    ):
        """
        Create a professional HTML email template with logo, colors, and proper formatting
        
        Args:
            title: Email title/heading
            message: Main message body
            details: List of tuples (label, value) for detail rows
            action_button: Whether to include primary action button
            action_url: URL for primary action button
            action_text: Text for primary action button
            highlight_color: Primary color for highlights
            secondary_action_button: Whether to include a secondary action button
            secondary_action_url: URL for secondary action button
            secondary_action_text: Text for secondary action button
        
        Returns:
            str: HTML email content
        """
        # Build details section
        details_html = ""
        if details:
            details_html = '<table style="width: 100%; margin: 20px 0; border-collapse: collapse;">'
            for label, value in details:
                if value:  # Only include non-empty details
                    details_html += f'''
                    <tr>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e9ecef; font-weight: 600; color: #495057; width: 35%;">
                            {label}:
                        </td>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e9ecef; color: #212529;">
                            {value}
                        </td>
                    </tr>
                    '''
            details_html += '</table>'
        
        # Build action buttons
        action_button_html = ""
        if (action_button and action_url) or (secondary_action_button and secondary_action_url):
            action_button_html = '<div style="margin: 30px 0; text-align: center;">'
            if action_button and action_url:
                action_button_html += f'''
                    <a href="{action_url}" style="display: inline-block; padding: 12px 32px; background-color: {highlight_color}; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; font-size: 16px;">
                        {action_text}
                    </a>
                '''
            if secondary_action_button and secondary_action_url:
                action_button_html += f'''
                    <a href="{secondary_action_url}" style="display: inline-block; padding: 12px 32px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; font-size: 16px; margin-left: 10px;">
                        {secondary_action_text}
                    </a>
                '''
            action_button_html += "</div>"
        
        # Build footer
        footer_html = '''
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #868e96;">
            <p>
                <strong>Sumitomo Wiring Systems</strong><br>
                Maintenance Management System<br><br>
                This is an automated email. Please do not reply to this message.
            </p>
        </div>
        '''
        
        # Get logo HTML from config
        logo_html = EmailService._get_logo_html()
        
        # Main HTML template
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Maintenance System Notification</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; line-height: 1.6; color: #212529; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 0;">
                
                <!-- Header with Logo -->
                <div style="background: linear-gradient(135deg, {highlight_color} 0%, {highlight_color}e6 100%); padding: 30px; text-align: center;">
                    {logo_html}
                    <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">
                        {title}
                    </h1>
                </div>
                
                <!-- Main Content -->
                <div style="padding: 30px;">
                    
                    <!-- Message -->
                    <p style="font-size: 16px; color: #495057; margin: 0 0 20px 0;">
                        {message}
                    </p>
                    
                    <!-- Details Section -->
                    {details_html}
                    
                    <!-- Action Button -->
                    {action_button_html}
                    
                    <!-- Footer -->
                    {footer_html}
                    
                </div>
                
            </div>
        </body>
        </html>
        '''
        return html
    
    @staticmethod
    def send_demand_created_notification(demand, requestor):
        """Send notification when demand is created"""
        subject = f"New Spare Parts Demand: {demand.demand_number}"
        html_body = EmailService._create_email_template(
            title="Spare Parts Demand Created",
            message="Your spare parts demand has been successfully created and is pending supervisor approval.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Quantity Requested", str(demand.quantity_requested)),
                ("Priority", f'<span style="color: #e8590c; font-weight: 600;">{demand.priority.upper()}</span>'),
                ("Date Created", str(demand.created_at.strftime('%Y-%m-%d %H:%M')) if demand.created_at else "")
            ],
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="View Details"
        )
        return EmailService.send_email(requestor.email, subject, html_body)
    
    @staticmethod
    def send_supervisor_approval_request(demand, supervisor):
        """Send notification to supervisor to approve demand"""
        subject = f"Approval Required: Spare Parts Demand {demand.demand_number}"
        User = get_user_model()
        requestor = User.query.get(demand.requestor_id) if demand.requestor_id else None
        html_body = EmailService._create_email_template(
            title="Approval Required",
            message="A spare parts demand requires your review and approval.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Quantity Requested", str(demand.quantity_requested)),
                ("Priority", f'<span style="color: #e8590c; font-weight: 600;">{demand.priority.upper()}</span>'),
                ("Requested By", requestor.full_name if requestor else "Unknown"),
                ("Date Submitted", str(demand.created_at.strftime('%Y-%m-%d %H:%M')) if demand.created_at else "")
            ],
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="Review & Approve/Reject",
            highlight_color="#ff6b6b"
        )
        return EmailService.send_email(supervisor.email, subject, html_body)

    @staticmethod
    def send_bulk_supervisor_approval_request(demands, supervisor):
        """Send a single email to supervisor summarizing multiple demands"""
        if not demands:
            return False
        User = get_user_model()
        requestor = User.query.get(demands[0].requestor_id) if demands[0].requestor_id else None
        subject = f"Approval Required: {len(demands)} Spare Parts Demands"

        details = []
        for d in demands:
            details.append((f"{d.demand_number} - {d.material.code}", f"{d.material.name} — Qty: {d.quantity_requested}"))

        html_body = EmailService._create_email_template(
            title="Approval Required for Multiple Demands",
            message=f"{requestor.full_name if requestor else 'A technician'} has submitted {len(demands)} spare parts requests requiring your approval.",
            details=details,
            action_button=True,
            action_url=f"http://localhost:5000/demands",
            action_text="Review Demands",
            highlight_color="#ff6b6b"
        )
        return EmailService.send_email(supervisor.email, subject, html_body)

    @staticmethod
    def send_bulk_stock_agent_notification(demands, stock_agent):
        """Send a single email to a stock agent summarizing multiple approved demands"""
        if not demands:
            return False

        User = get_user_model()
        requestor = User.query.get(demands[0].requestor_id) if demands[0].requestor_id else None
        subject = f"Stock Allocation Needed: {len(demands)} Demands"

        details = []
        for d in demands:
            details.append((f"{d.demand_number} - {d.material.code}", f"{d.material.name} — Qty: {d.quantity_requested}"))

        html_body = EmailService._create_email_template(
            title="Stock Allocation Required",
            message=f"{len(demands)} demands have been approved and require stock allocation.",
            details=details,
            action_button=True,
            action_url=f"http://localhost:5000/demands",
            action_text="Allocate Stock",
            highlight_color="#4c6ef5"
        )
        return EmailService.send_email(stock_agent.email, subject, html_body)
    
    @staticmethod
    def send_supervisor_decision_notification(demand, decision, notes=''):
        """Send notification about supervisor's decision"""
        status_color = "#51cf66" if decision.lower() == "approved" else "#ff6b6b"
        status_style = f'<span style="color: {status_color}; font-weight: 700;">{decision.upper()}</span>'
        
        User = get_user_model()
        requestor = User.query.get(demand.requestor_id) if demand.requestor_id else None
        subject = f"Demand {decision.upper()}: {demand.demand_number}"
        html_body = EmailService._create_email_template(
            title=f"Demand {status_style}",
            message=f"Your spare parts demand has been <strong>{decision}</strong> by the supervisor.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Quantity", str(demand.quantity_requested)),
                ("Decision", status_style),
                ("Decision Date", str(demand.updated_at.strftime('%Y-%m-%d %H:%M')) if demand.updated_at else "")
            ] + ([("Notes", f'<span style="font-style: italic; color: #666;">{notes}</span>')] if notes else []),
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="View Full Details"
        )
        return EmailService.send_email(requestor.email if requestor else "", subject, html_body)
    
    @staticmethod
    def send_stock_agent_notification(demand, stock_agents):
        """Send notification to stock agents about approved demands"""
        if isinstance(stock_agents, list) and len(stock_agents) > 0:
            stock_agent = stock_agents[0]
            recipient = stock_agent.email
        else:
            recipient = stock_agents.email if hasattr(stock_agents, 'email') else None
        
        if not recipient:
            return False
        
        User = get_user_model()
        requestor = User.query.get(demand.requestor_id) if demand.requestor_id else None
        subject = f"Stock Allocation Needed: Demand {demand.demand_number}"
        html_body = EmailService._create_email_template(
            title="Stock Allocation Required",
            message="A demand has been approved and requires stock allocation.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Quantity Needed", str(demand.quantity_requested)),
                ("Requested By", requestor.full_name if requestor else "Unknown"),
                ("Priority", f'<span style="color: #e8590c; font-weight: 600;">{demand.priority.upper()}</span>'),
                ("Due Date", "As Soon As Possible")
            ],
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="Allocate Stock",
            highlight_color="#4c6ef5"
        )
        return EmailService.send_email(recipient, subject, html_body)

    @staticmethod
    def send_low_stock_alert(material, current_stock):
        """Send an email to stock agents when a material hits minimum stock."""
        from app.models import StockAlert, User

        if not current_app.config.get('EMAIL_LOW_STOCK_ALERTS_ENABLED', True):
            logger.info("Low stock alert emails are disabled by configuration; skipping email.")
            return False

        stock_agents = User.query.filter_by(role='stock_agent').all()
        if not stock_agents:
            return False

        # Create a StockAlert record so the user can mark it as skipped/read
        try:
            alert = StockAlert(
                material_id=material.id,
                alert_type='low_stock',
                alert_message=(
                    f"Material {material.name} (code: {material.code}) is at {current_stock} {material.unit} "
                    f"(min: {material.min_stock})."
                )
            )
            from app.models import db
            db.session.add(alert)
            db.session.commit()
        except Exception:
            alert = None
            db.session.rollback()

        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000').rstrip('/')
        # Direct stock alert emails to the main stock dashboard (no /inventory route used)
        view_url = f"{base_url}/stock"
        skip_url = f"{base_url}/stock/alert/{alert.id}/skip" if alert else f"{base_url}/stock/alerts"

        subject = f"Low Stock Alert: {material.name}"
        message = (
            f"The material <strong>{material.name}</strong> (code: {material.code}) has reached or fallen below its minimum stock level. "
            f"Current stock is <strong>{current_stock}</strong> {material.unit}.<br/><br/>"
            f"<strong>Next steps:</strong><br/>"
            f"• Recharge the quantity of this PDR (spare part) in the system.<br/>"
            f"• If this alert is not relevant, skip it using the button below.<br/>"
            f"• Update the stock quantity once replenished.<br/>"
            f"If you need assistance, contact your supervisor."
        )

        html_body = EmailService._create_email_template(
            title="Low Stock Alert",
            message=message,
            details=[
                ("Material", f"{material.name} ({material.code})"),
                ("Current Stock", str(current_stock)),
                ("Minimum Stock", str(material.min_stock)),
            ],
            action_button=True,
            action_url=view_url,
            action_text="Recharge PDR",
            secondary_action_button=True,
            secondary_action_url=skip_url,
            secondary_action_text="Skip Alert",
            highlight_color="#ff6b6b"
        )

        recipients = [agent.email for agent in stock_agents if agent.email]
        return EmailService.send_email(recipients, subject, html_body)

    @staticmethod
    def send_critical_stock_alert(materials, recipients):
        """Send a critical stock summary email to a list of recipients."""
        if not current_app.config.get('EMAIL_CRITICAL_STOCK_ALERTS_ENABLED', False):
            logger.info("Critical stock alert emails are disabled by configuration; skipping email.")
            return False

        if not materials or not recipients:
            return False

        # Create a single StockAlert entry so users can skip it cleanly
        try:
            alert_message = "; ".join([
                f"{m.name} ({m.code}) - {m.current_stock} {m.unit} (Min: {m.min_stock})"
                for m in materials
            ])
            from app.models import StockAlert, db
            alert = StockAlert(
                material_id=materials[0].id if materials else None,
                alert_type='critical',
                alert_message=alert_message
            )
            db.session.add(alert)
            db.session.commit()
        except Exception:
            alert = None
            db.session.rollback()

        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000').rstrip('/')
        recharge_url = f"{base_url}/stock"
        skip_url = f"{base_url}/stock/alert/{alert.id}/skip" if alert else f"{base_url}/stock/alerts"

        # Ensure recipients are unique and non-empty so users do not receive duplicate copies.
        if isinstance(recipients, list):
            recipients = [r for r in dict.fromkeys(recipients) if r]

        subject = "CRITICAL STOCK ALERT: Items at or below minimum"
        details = []
        for m in materials:
            details.append((
                f"{m.name} ({m.code})",
                f"Stock: {m.current_stock} {m.unit} (Min: {m.min_stock})"
            ))

        html_body = EmailService._create_email_template(
            title="Critical Stock Alert",
            message=(
                "The following inventory items have reached or fallen below minimum stock levels.<br/>"
                "Please recharge the stock quantities for these items (PDR) or mark the alert as skipped if it is not relevant."
            ),
            details=details,
            action_button=True,
            action_url=recharge_url,
            action_text="Recharge Stock",
            secondary_action_button=True,
            secondary_action_url=skip_url,
            secondary_action_text="Skip Alert",
            highlight_color="#ff3b30"
        )

        return EmailService.send_email(recipients, subject, html_body)
    
    @staticmethod
    def send_allocation_notification(demand, technician):
        """Send notification to technician that parts are ready"""
        subject = f"Parts Ready for Pickup: Demand {demand.demand_number}"
        html_body = EmailService._create_email_template(
            title="Parts Allocated & Ready",
            message="Your requested spare parts have been allocated and are ready for pickup.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Allocated Quantity", str(demand.quantity_allocated) if demand.quantity_allocated else str(demand.quantity_requested)),
                ("Status", '<span style="color: #51cf66; font-weight: 700;">READY FOR PICKUP</span>'),
                ("Pickup Location", "Stock Room"),
                ("Allocated Date", str(demand.updated_at.strftime('%Y-%m-%d %H:%M')) if demand.updated_at else "")
            ],
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="View & Confirm Pickup",
            highlight_color="#51cf66"
        )
        return EmailService.send_email(technician.email, subject, html_body)

    @staticmethod
    def send_stock_agent_decision_notification(demand, decision, notes=''):
        """Notify technician of stock agent's decision (approved/rejected)."""
        status_color = "#51cf66" if decision.lower() == "approved" else "#ff6b6b"
        status_style = f'<span style="color: {status_color}; font-weight: 700;">{decision.upper()}</span>'
        User = get_user_model()
        technician = User.query.get(demand.requestor_id) if demand.requestor_id else None
        subject = f"Demand {decision.upper()} by Stock Agent: {demand.demand_number}"
        html_body = EmailService._create_email_template(
            title=f"Demand {status_style}",
            message=f"Your spare parts demand has been <strong>{decision}</strong> by the stock agent.",
            details=[
                ("Demand Number", demand.demand_number),
                ("Material", demand.material.name if demand.material else "Unknown"),
                ("Quantity", str(demand.quantity_requested)),
                ("Decision", status_style),
                ("Decision Date", str(demand.updated_at.strftime('%Y-%m-%d %H:%M')) if demand.updated_at else "")
            ] + ([("Notes", f'<span style="font-style: italic; color: #666;">{notes}</span>')] if notes else []),
            action_button=True,
            action_url=f"http://localhost:5000/demands/{demand.id}",
            action_text="View Full Details"
        )
        return EmailService.send_email(technician.email if technician else "", subject, html_body)
