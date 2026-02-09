"""Management script for database operations."""
import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate as create_migration, upgrade
from app import create_app, db
from app.models import User


def init_db():
    """Initialize database migrations."""
    print("Initializing database migrations...")
    try:
        init()
        print("✓ Migrations initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing migrations: {e}")


def migrate_db(message="Auto migration"):
    """Create a new migration."""
    print(f"Creating migration: {message}")
    try:
        create_migration(message=message)
        print("✓ Migration created successfully")
    except Exception as e:
        print(f"✗ Error creating migration: {e}")


def upgrade_db():
    """Apply migrations to database."""
    print("Applying migrations...")
    try:
        upgrade()
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"✗ Error applying migrations: {e}")


def create_admin(email, password, first_name, last_name):
    """Create an admin user."""
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=email).first()
        if existing_admin:
            print(f"✗ User with email {email} already exists")
            return
        
        try:
            admin = User(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created: {email}")
        except Exception as e:
            print(f"✗ Error creating admin: {e}")
            db.session.rollback()


def reset_db():
    """Drop all tables and recreate (WARNING: destroys all data)."""
    app = create_app()
    with app.app_context():
        response = input("⚠️  WARNING: This will delete ALL data. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled")
            return
        
        try:
            db.drop_all()
            db.create_all()
            print("✓ Database reset successfully")
        except Exception as e:
            print(f"✗ Error resetting database: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
Usage: python manage.py <command>

Commands:
  init              Initialize database migrations
  migrate [message] Create a new migration
  upgrade           Apply migrations to database
  create-admin      Create an admin user (interactive)
  reset             Reset database (WARNING: destroys all data)
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'migrate':
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        migrate_db(message)
    elif command == 'upgrade':
        upgrade_db()
    elif command == 'create-admin':
        email = input("Email: ")
        password = input("Password: ")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        create_admin(email, password, first_name, last_name)
    elif command == 'reset':
        reset_db()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
