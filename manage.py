"""Management script for database operations."""
import os
import sys
import getpass
import argparse
from datetime import datetime, timezone
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
    parser = argparse.ArgumentParser(prog="python manage.py", add_help=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize database migrations")

    migrate_parser = subparsers.add_parser("migrate", help="Create a new migration")
    migrate_parser.add_argument("message", nargs="?", default="Auto migration")

    subparsers.add_parser("upgrade", help="Apply migrations to database")

    create_admin_parser = subparsers.add_parser("create-admin", help="Create an admin user")
    create_admin_parser.add_argument("--email", default=os.environ.get("ADMIN_EMAIL"))
    create_admin_parser.add_argument("--password", default=os.environ.get("ADMIN_PASSWORD"))
    create_admin_parser.add_argument("--first-name", default=os.environ.get("ADMIN_FIRST_NAME"))
    create_admin_parser.add_argument("--last-name", default=os.environ.get("ADMIN_LAST_NAME"))

    subparsers.add_parser("reset", help="Reset database (WARNING: destroys all data)")

    args = parser.parse_args()

    if args.command == "init":
        init_db()
    elif args.command == "migrate":
        migrate_db(args.message)
    elif args.command == "upgrade":
        upgrade_db()
    elif args.command == "create-admin":
        non_interactive = not sys.stdin.isatty()
        if non_interactive and not args.email:
            print("✗ ADMIN_EMAIL (or --email) is required in non-interactive mode")
            sys.exit(2)
        if non_interactive and not args.first_name:
            print("✗ ADMIN_FIRST_NAME (or --first-name) is required in non-interactive mode")
            sys.exit(2)
        if non_interactive and not args.last_name:
            print("✗ ADMIN_LAST_NAME (or --last-name) is required in non-interactive mode")
            sys.exit(2)
        if non_interactive and not args.password:
            print("✗ ADMIN_PASSWORD (or --password) is required in non-interactive mode")
            sys.exit(2)

        email = args.email or input("Email: ")
        password = args.password
        if not password:
            password = getpass.getpass("Password (hidden): ")
            password_confirm = getpass.getpass("Confirm Password: ")
            if password != password_confirm:
                print("✗ Passwords do not match")
                sys.exit(1)
        first_name = args.first_name or input("First Name: ")
        last_name = args.last_name or input("Last Name: ")
        create_admin(email, password, first_name, last_name)
    elif args.command == "reset":
        reset_db()
