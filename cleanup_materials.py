"""
Script to keep only 10 materials and delete all others
"""

import os
from app import create_app, db
from app.models import Material
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    # Get all materials ordered by ID
    all_materials = Material.query.order_by(Material.id).all()
    
    print(f"Total materials in database: {len(all_materials)}")
    
    if len(all_materials) > 10:
        # Get materials to delete (keep first 10)
        materials_to_delete = all_materials[10:]
        materials_to_delete_ids = [str(mat.id) for mat in materials_to_delete]
        ids_str = ','.join(materials_to_delete_ids)
        
        print(f"Keeping first 10 materials:")
        for i, mat in enumerate(all_materials[:10], 1):
            print(f"  {i}. {mat.code} - {mat.name}")
        
        print(f"\nPreparing to delete {len(materials_to_delete)} materials...")
        
        try:
            # Delete using raw SQL with CASCADE for ALL related tables
            # First, get material IDs to delete
            print("  - Disabling foreign key constraints temporarily...")
            db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            
            # Delete all records referencing these materials
            print(f"  - Deleting {len(materials_to_delete)} materials and all related records...")
            delete_query = f"DELETE FROM materials WHERE id IN ({ids_str})"
            db.session.execute(text(delete_query))
            
            # Re-enable foreign key constraints
            print("  - Re-enabling foreign key constraints...")
            db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            
            # Commit the deletion
            db.session.commit()
            print("\n✓ Successfully deleted all materials except the first 10!")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error: {str(e)}")
            raise
    else:
        print("✓ Database already has 10 or fewer materials. No action needed.")
