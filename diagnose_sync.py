#!/usr/bin/env python
"""Diagnose database synchronization issues"""
import os
from dotenv import load_dotenv
import time

load_dotenv()

print("=" * 80)
print("DATABASE SYNCHRONIZATION DIAGNOSTIC".center(80))
print("=" * 80)

try:
    from app import create_app, db
    from app.models import Material
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("\n[1] Testing Read-Write Synchronization...")
        
        # Get initial count
        initial_count = Material.query.count()
        print(f"  Initial material count: {initial_count}")
        
        # Create a test material
        test_material = Material(
            code=f'TEST_{int(time.time())}',
            name='Test Material Sync',
            description='Testing database synchronization',
            unit='piece',
            current_stock=100
        )
        
        print(f"\n[2] Adding new material: {test_material.code}")
        db.session.add(test_material)
        db.session.flush()  # Flush to generate ID
        test_id = test_material.id
        print(f"  Added with ID: {test_id}")
        
        # Check before commit
        before_commit = Material.query.filter_by(code=test_material.code).first()
        print(f"  Before commit - Can query new material: {before_commit is not None}")
        
        # Commit
        print(f"\n[3] Committing changes...")
        db.session.commit()
        print(f"  Commit successful")
        
        # Check after commit
        after_commit = Material.query.filter_by(code=test_material.code).first()
        print(f"  After commit - Can query new material: {after_commit is not None}")
        
        # Check count
        new_count = Material.query.count()
        print(f"  Material count after insert: {new_count}")
        print(f"  Count increased: {new_count > initial_count}")
        
        # Test update
        print(f"\n[4] Testing UPDATE synchronization...")
        if after_commit:
            after_commit.current_stock = 200
            db.session.commit()
            print(f"  Updated stock to 200")
            
            # Verify update
            updated = Material.query.get(after_commit.id)
            print(f"  Current stock in DB: {updated.current_stock}")
            print(f"  Update synchronized: {updated.current_stock == 200}")
        
        # Test delete
        print(f"\n[5] Testing DELETE synchronization...")
        if after_commit:
            delete_id = after_commit.id
            db.session.delete(after_commit)
            db.session.commit()
            print(f"  Deleted test material")
            
            # Verify delete
            deleted = Material.query.get(delete_id)
            print(f"  Material still in DB: {deleted is not None}")
            print(f"  Delete synchronized: {deleted is None}")
        
        # Check connection pooling
        print(f"\n[6] Database Connection Pool Info:")
        pool = db.engine.pool
        print(f"  Pool size: {pool.size if hasattr(pool, 'size') else 'N/A'}")
        print(f"  Pool checked out: {pool.checkedout() if hasattr(pool, 'checkedout') else 'N/A'}")
        print(f"  Pool type: {type(pool).__name__}")
        
        # Check SQLAlchemy configuration
        print(f"\n[7] SQLAlchemy Configuration:")
        echo = app.config.get('SQLALCHEMY_ECHO', False)
        track_mods = app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        print(f"  Query echo: {echo}")
        print(f"  Track modifications: {track_mods}")
        
        print(f"\n" + "=" * 80)
        print("DATABASE SYNCHRONIZATION: OK".center(80))
        print("=" * 80)
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
