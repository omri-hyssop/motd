"""Flask application factory."""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
ma = Marshmallow()
scheduler = BackgroundScheduler()


def create_app(config_name=None):
    """Create and configure Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )

    # Register blueprints
    with app.app_context():
        from app.routes import auth, users, restaurants, menus, orders, admin, reminders, health, uploads
        from app.routes import tasks
        
        app.register_blueprint(auth.bp)
        app.register_blueprint(users.bp)
        app.register_blueprint(restaurants.bp)
        app.register_blueprint(menus.bp)
        app.register_blueprint(orders.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(reminders.bp)
        app.register_blueprint(tasks.bp)
        app.register_blueprint(health.bp)
        app.register_blueprint(uploads.bp)

        # Register error handlers
        from app.middleware.error_handler import register_error_handlers
        register_error_handlers(app)

        # Configure scheduler (only in non-testing environments)
        if not app.config['TESTING'] and app.config.get('SCHEDULER_ENABLED', True):
            configure_scheduler(app)

    return app


def configure_scheduler(app):
    """Configure APScheduler for background jobs."""
    from app.tasks.reminder_tasks import send_daily_reminders, cleanup_old_sessions
    from app.tasks.order_tasks import send_restaurant_summaries

    # Parse time strings
    reminder_hour, reminder_minute = map(int, app.config['REMINDER_TIME'].split(':'))
    summary_hour, summary_minute = map(int, app.config['RESTAURANT_SUMMARY_TIME'].split(':'))

    # Add jobs
    scheduler.add_job(
        func=lambda: send_daily_reminders(app),
        trigger='cron',
        hour=reminder_hour,
        minute=reminder_minute,
        id='daily_reminders',
        name='Send daily meal reminders',
        replace_existing=True
    )

    scheduler.add_job(
        func=lambda: send_restaurant_summaries(app),
        trigger='cron',
        hour=summary_hour,
        minute=summary_minute,
        id='restaurant_summaries',
        name='Send restaurant order summaries',
        replace_existing=True
    )

    scheduler.add_job(
        func=lambda: cleanup_old_sessions(app),
        trigger='cron',
        hour=0,
        minute=0,
        id='session_cleanup',
        name='Clean up expired sessions',
        replace_existing=True
    )

    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        app.logger.info('APScheduler started')

    # Register shutdown hook
    import atexit
    atexit.register(lambda: scheduler.shutdown())
