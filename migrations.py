from app import app, db
from sqlalchemy import text, exc

def run_migrations():
    with app.app_context():
        try:
            # Check if email column exists before trying to rename
            try:
                db.session.execute(text('ALTER TABLE "user" RENAME COLUMN email TO email_encrypted'))
                print("Renamed email column to email_encrypted")
            except exc.ProgrammingError:
                print("email_encrypted column already exists")
                db.session.rollback()
            
            # Add title_encrypted to flipbook table if it doesn't exist
            try:
                db.session.execute(text('ALTER TABLE flipbook ADD COLUMN title_encrypted TEXT'))
                db.session.execute(text('UPDATE flipbook SET title_encrypted = title::TEXT'))
                db.session.execute(text('ALTER TABLE flipbook DROP COLUMN IF EXISTS title'))
                print("Added title_encrypted column")
            except exc.ProgrammingError:
                print("title_encrypted column already exists")
                db.session.rollback()
            
            # Update pageview table for encrypted IP addresses
            try:
                db.session.execute(text('ALTER TABLE page_view RENAME COLUMN ip_address TO ip_address_encrypted'))
                db.session.execute(text('ALTER TABLE page_view ALTER COLUMN ip_address_encrypted TYPE TEXT'))
                print("Updated page_view table for encrypted IP addresses")
            except exc.ProgrammingError:
                print("ip_address_encrypted column already exists")
                db.session.rollback()
            
            db.session.commit()
            print("Migration completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migrations()
