"""Reminder service for scheduling and sending reminders."""
import logging
from datetime import datetime
from flask import current_app
from app import db
from app.models import User, Reminder
from app.services.whatsapp_service import WhatsAppService
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for handling reminders."""
    
    @staticmethod
    def send_reminders_for_date(target_date):
        """Send reminders to users who haven't ordered for target_date."""
        logger.info(f'Sending reminders for {target_date}')
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        reminders_sent = 0
        reminders_failed = 0
        
        for user in users:
            # Check if user has order for target date
            missing_dates = OrderService.get_missing_order_days(
                user_id=user.id,
                days_ahead=1,
                start_date=target_date
            )
            
            if target_date in missing_dates:
                # User needs reminder
                success = ReminderService.send_reminder_to_user(user, target_date)
                if success:
                    reminders_sent += 1
                else:
                    reminders_failed += 1
        
        logger.info(f'Reminders sent: {reminders_sent}, failed: {reminders_failed}')
        return reminders_sent, reminders_failed
    
    @staticmethod
    def send_reminder_to_user(user, order_date):
        """Send a reminder to a specific user."""
        try:
            # Build order URL
            frontend_url = current_app.config['FRONTEND_URL']
            order_url = f"{frontend_url}/order?date={order_date.isoformat()}"
            
            # Create reminder record
            reminder = Reminder(
                user_id=user.id,
                order_date=order_date,
                reminder_type='whatsapp',
                status='pending'
            )
            db.session.add(reminder)
            db.session.commit()
            
            # Send WhatsApp message
            success, response = WhatsAppService.send_order_reminder(
                user=user,
                order_date=order_date,
                order_url=order_url
            )
            
            # Update reminder status
            if success:
                reminder.status = 'sent'
                reminder.sent_at = datetime.utcnow()
                logger.info(f'Reminder sent to user {user.id} for {order_date}')
            else:
                reminder.status = 'failed'
                reminder.failure_reason = str(response)
                logger.error(f'Failed to send reminder to user {user.id}: {response}')
            
            db.session.commit()
            return success
            
        except Exception as e:
            logger.error(f'Error sending reminder to user {user.id}: {str(e)}')
            if reminder:
                reminder.status = 'failed'
                reminder.failure_reason = str(e)
                db.session.commit()
            return False
    
    @staticmethod
    def get_users_without_orders(order_date):
        """Get list of users who haven't ordered for a specific date."""
        users = User.query.filter_by(is_active=True).all()
        users_without_orders = []
        
        for user in users:
            missing_dates = OrderService.get_missing_order_days(
                user_id=user.id,
                days_ahead=1,
                start_date=order_date
            )
            
            if order_date in missing_dates:
                users_without_orders.append(user)
        
        return users_without_orders
