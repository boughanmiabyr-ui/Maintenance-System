"""
Add conditional maintenance columns to machines table
Run this script to update your database schema
"""

from app import create_app
from app.models import db
from sqlalchemy import text

def add_conditional_maintenance_columns():
    """Add missing columns to machines table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.connect()
            
            print("Checking if columns exist and adding them if needed...\n")
            
            # Column definitions to add
            columns_to_add = [
                ("operation_count", "ALTER TABLE machines ADD COLUMN operation_count INT DEFAULT 0 NOT NULL, ADD INDEX idx_operation_count (operation_count)"),
                ("conditional_maintenance_threshold", "ALTER TABLE machines ADD COLUMN conditional_maintenance_threshold INT DEFAULT 300000 NOT NULL"),
                ("last_conditional_reset_date", "ALTER TABLE machines ADD COLUMN last_conditional_reset_date DATETIME NULL"),
                ("last_conditional_replacement_date", "ALTER TABLE machines ADD COLUMN last_conditional_replacement_date DATETIME NULL")
            ]
            
            for col_name, sql_statement in columns_to_add:
                try:
                    # Check if column exists
                    check_sql = f"SHOW COLUMNS FROM machines LIKE '{col_name}'"
                    result = connection.execute(text(check_sql))
                    
                    if result.rowcount == 0:
                        print(f"✓ Adding column: {col_name}")
                        connection.execute(text(sql_statement))
                        connection.commit()
                        print(f"  ✓ Column '{col_name}' added successfully!\n")
                    else:
                        print(f"✓ Column '{col_name}' already exists\n")
                
                except Exception as e:
                    print(f"✗ Error processing column '{col_name}': {str(e)}\n")
            
            # Create ConditionalMaintenanceRecord table if it doesn't exist
            print("Creating conditional_maintenance_records table if needed...\n")
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS conditional_maintenance_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                machine_id INT NOT NULL,
                technician_id INT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                operation_count_before INT NOT NULL,
                operation_count_after INT NOT NULL,
                description LONGTEXT,
                components_replaced LONGTEXT,
                maintenance_report_id INT NULL,
                email_sent BOOLEAN DEFAULT FALSE,
                email_sent_to VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_machine_id (machine_id),
                INDEX idx_created_at (created_at),
                CONSTRAINT fk_cmr_machine FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
                CONSTRAINT fk_cmr_technician FOREIGN KEY (technician_id) REFERENCES users(id),
                CONSTRAINT fk_cmr_report FOREIGN KEY (maintenance_report_id) REFERENCES maintenance_reports(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            try:
                connection.execute(text(create_table_sql))
                connection.commit()
                print("✓ conditional_maintenance_records table created/verified successfully!\n")
            except Exception as e:
                print(f"✗ Error creating conditional_maintenance_records table: {str(e)}\n")
            
            connection.close()
            print("✓ Database migration completed successfully!")
            print("\nYou can now use the conditional maintenance feature.")
            
        except Exception as e:
            print(f"✗ Database connection error: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Conditional Maintenance Database Migration")
    print("=" * 60)
    print()
    
    success = add_conditional_maintenance_columns()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration Status: SUCCESS ✓")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration Status: FAILED ✗")
        print("=" * 60)
