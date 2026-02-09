"""Background tasks for reminders."""
import logging
from datetime import datetime, date, timedelta
from app import db
from app.models import Session
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


def send_daily_reminders(app):
    """Send daily reminders to users without orders."""
    with app.app_context():
        try:
            logger.info('Starting daily reminder task')
            
            # Get reminder days ahead from config
            days_ahead_list = app.config.get('REMINDER_DAYS_AHEAD', [1, 2, 3])
            
            # Send reminders for each configured day
            for days_ahead in days_ahead_list:
                target_date = date.today() + timedelta(days=days_ahead)
                logger.info(f'Sending reminders for {target_date} ({days_ahead} days ahead)')
                
                sent, failed = ReminderService.send_reminders_for_date(target_date)
                logger.info(f'Date {target_date}: {sent} reminders sent, {failed} failed')
            
            logger.info('Daily reminder task completed')
            
        except Exception as e:
            logger.error(f'Error in daily reminder task: {str(e)}', exc_info=True)


def cleanup_old_sessions(app):
    """Clean up expired sessions from database."""
    with app.app_context():
        try:
            logger.info('Starting session cleanup task')
            
            # Delete sessions older than expiry
            deleted_count = Session.query.filter(
                Session.expires_at < datetime.utcnow()
            ).delete()
            
            db.session.commit()
            
            logger.info(f'Session cleanup completed: {deleted_count} sessions removed')
            
        except Exception as e:
            logger.error(f'Error in session cleanup task: {str(e)}', exc_info=True)
            db.session.rollback()
