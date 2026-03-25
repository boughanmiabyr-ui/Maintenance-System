#!/usr/bin/env python
"""
Migration Runner for Archive System
Adds archive_date column and updates demand_status enum
"""

import pymysql
import os
from config import Config

def run_migration():
    """Execute the archive system migration"""
    
    # Get database config from Config class
    db_config = {
        'host': Config.MYSQL_HOST,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
        'database': Config.MYSQL_DB,
        'charset': 'utf8mb4'
    }
    
    # SQL migration statements
    migration_sql = [
        """
        ALTER TABLE spare_parts_demands 
        MODIFY COLUMN demand_status ENUM(
            'pending',
            'supervisor_review',
            'approved_supervisor',
            'stock_agent_review',
            'approved_stock_agent',
            'rejected',
            'partial_allocated',
            'fulfilled',
            'cancelled',
            'archived'
        ) DEFAULT 'pending'
        """,
        """
        ALTER TABLE spare_parts_demands 
        ADD COLUMN archive_date DATETIME NULL
        """,
        """
        ALTER TABLE spare_parts_demands 
        ADD INDEX idx_archive_date (archive_date)
        """,
        """
        ALTER TABLE spare_parts_demands 
        ADD INDEX idx_status_archived (demand_status, archive_date)
        """
    ]
    
    try:
        # Connect to database
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("Connected to database successfully!")
        print(f"Database: {db_config['database']}")
        print("-" * 50)
        
        # Execute migration statements
        for i, sql in enumerate(migration_sql, 1):
            try:
                cursor.execute(sql)
                print(f"✓ Migration {i} executed successfully")
            except pymysql.Error as e:
                # Check if error is about column already existing
                if "Duplicate column name" in str(e):
                    print(f"✓ Migration {i} skipped (column already exists)")
                elif "Duplicate key name" in str(e):
                    print(f"✓ Migration {i} skipped (index already exists)")
                else:
                    print(f"✗ Migration {i} failed: {e}")
                    raise
        
        connection.commit()
        print("-" * 50)
        print("✓ Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("DESCRIBE spare_parts_demands")
        columns = cursor.fetchall()
        
        print("\nUpdated table structure (partial):")
        for col in columns[-3:]:  # Show last 3 columns
            print(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
