"""Background tasks for order processing."""
import logging
from datetime import date
from app import db
from app.models import Order, RestaurantOrderSummary, Restaurant
from app.services.email_service import EmailService
from datetime import datetime

logger = logging.getLogger(__name__)


def send_restaurant_summaries(app):
    """Send order summaries to restaurants for today."""
    with app.app_context():
        try:
            logger.info('Starting restaurant order summary task')
            
            today = date.today()
            
            # Get all orders for today
            orders = Order.query.filter_by(
                order_date=today
            ).filter(
                Order.status.in_(['pending', 'confirmed'])
            ).all()
            
            if not orders:
                logger.info('No orders for today')
                return
            
            # Group orders by restaurant
            orders_by_restaurant = {}
            for order in orders:
                if order.restaurant_id not in orders_by_restaurant:
                    orders_by_restaurant[order.restaurant_id] = []
                orders_by_restaurant[order.restaurant_id].append(order)
            
            # Send summary to each restaurant
            summaries_sent = 0
            summaries_failed = 0
            
            for restaurant_id, restaurant_orders in orders_by_restaurant.items():
                restaurant = db.session.get(Restaurant, restaurant_id)
                if not restaurant or not restaurant.is_active:
                    continue
                
                # Send email
                success, message = EmailService.send_restaurant_order_summary(
                    restaurant=restaurant,
                    order_date=today,
                    orders=restaurant_orders
                )
                
                # Create summary record
                summary_data = {
                    'order_count': len(restaurant_orders),
                    'total_amount': float(sum(o.total_amount for o in restaurant_orders)),
                    'order_ids': [o.id for o in restaurant_orders]
                }
                
                summary = RestaurantOrderSummary(
                    restaurant_id=restaurant_id,
                    order_date=today,
                    sent_at=datetime.utcnow() if success else None,
                    email_status='sent' if success else 'failed',
                    summary_data=summary_data
                )
                
                db.session.add(summary)
                
                if success:
                    summaries_sent += 1
                    # Update order statuses
                    for order in restaurant_orders:
                        if order.status == 'confirmed':
                            order.status = 'sent_to_restaurant'
                else:
                    summaries_failed += 1
                    logger.error(f'Failed to send summary to restaurant {restaurant_id}: {message}')
            
            db.session.commit()
            
            logger.info(f'Restaurant summaries: {summaries_sent} sent, {summaries_failed} failed')
            
        except Exception as e:
            logger.error(f'Error in restaurant summary task: {str(e)}', exc_info=True)
            db.session.rollback()


def generate_restaurant_summary_for_date(restaurant_id, target_date):
    """Generate and send order summary for a specific restaurant and date (manual trigger)."""
    try:
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not restaurant:
            return False, 'Restaurant not found'
        
        # Get orders for the date
        orders = Order.query.filter_by(
            restaurant_id=restaurant_id,
            order_date=target_date
        ).filter(
            Order.status != 'cancelled'
        ).all()
        
        if not orders:
            return False, 'No orders found for this date'
        
        # Send email
        success, message = EmailService.send_restaurant_order_summary(
            restaurant=restaurant,
            order_date=target_date,
            orders=orders
        )
        
        if success:
            # Create summary record
            summary_data = {
                'order_count': len(orders),
                'total_amount': float(sum(o.total_amount for o in orders)),
                'order_ids': [o.id for o in orders]
            }
            
            summary = RestaurantOrderSummary(
                restaurant_id=restaurant_id,
                order_date=target_date,
                sent_at=datetime.utcnow(),
                email_status='sent',
                summary_data=summary_data
            )
            
            db.session.add(summary)
            db.session.commit()
            
            return True, 'Summary sent successfully'
        else:
            return False, message
            
    except Exception as e:
        logger.error(f'Error generating restaurant summary: {str(e)}')
        return False, str(e)
