from app import app, db
from sqlalchemy import text

def run_migrations():
    with app.app_context():
        try:
            # Add refresh_token column
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS refresh_token VARCHAR(256) UNIQUE'))
            # Add refresh_token_expiry column
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS refresh_token_expiry TIMESTAMP'))
            db.session.commit()
            print("Migration completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migrations()
