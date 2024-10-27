from app import app, db
from sqlalchemy import text

def run_migrations():
    with app.app_context():
        try:
            # Rename email to email_encrypted in user table
            db.session.execute(text('ALTER TABLE "user" RENAME COLUMN email TO email_encrypted'))
            
            # Add title_encrypted to flipbook table
            db.session.execute(text('ALTER TABLE flipbook ADD COLUMN IF NOT EXISTS title_encrypted TEXT'))
            db.session.execute(text('UPDATE flipbook SET title_encrypted = title::TEXT'))
            db.session.execute(text('ALTER TABLE flipbook DROP COLUMN title'))
            
            # Update pageview table for encrypted IP addresses
            db.session.execute(text('ALTER TABLE page_view RENAME COLUMN ip_address TO ip_address_encrypted'))
            db.session.execute(text('ALTER TABLE page_view ALTER COLUMN ip_address_encrypted TYPE TEXT'))
            
            db.session.commit()
            print("Migration completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migrations()
