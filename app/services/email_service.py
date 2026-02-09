"""Email service using SendGrid."""
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid."""
    
    @staticmethod
    def send_email(to_email, subject, html_content, plain_content=None):
        """Send an email using SendGrid."""
        try:
            api_key = current_app.config['SENDGRID_API_KEY']
            from_email = current_app.config['FROM_EMAIL']
            from_name = current_app.config['FROM_NAME']
            
            if not api_key:
                logger.error('SendGrid API key not configured')
                return False, 'Email not configured'
            
            message = Mail(
                from_email=Email(from_email, from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.add_content(Content("text/plain", plain_content))
            
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f'Email sent successfully to {to_email}')
                return True, 'Email sent'
            else:
                logger.error(f'SendGrid error: {response.status_code}')
                return False, f'SendGrid error: {response.status_code}'
                
        except Exception as e:
            logger.error(f'Error sending email: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def send_restaurant_order_summary(restaurant, order_date, orders):
        """Send order summary email to restaurant."""
        if not restaurant.email:
            logger.warning(f'Restaurant {restaurant.id} has no email')
            return False, 'No email address'
        
        # Build email content
        subject = f'Order Summary for {order_date.strftime("%A, %B %d, %Y")}'
        
        # Group orders by user and items
        order_lines = []
        total_orders = len(orders)
        total_amount = sum(order.total_amount for order in orders)
        
        for order in orders:
            order_lines.append(f'<h3>{order.user.full_name}</h3>')
            order_lines.append('<ul>')
            
            for item in order.items:
                order_lines.append(
                    f'<li>{item.quantity}x {item.menu_item.name} - ${item.price} '
                    f'(${item.quantity * item.price})'
                )
                if item.notes:
                    order_lines.append(f'<br><em>Note: {item.notes}</em>')
                order_lines.append('</li>')
            
            order_lines.append('</ul>')
            if order.notes:
                order_lines.append(f'<p><strong>Order notes:</strong> {order.notes}</p>')
            order_lines.append(f'<p><strong>Total:</strong> ${order.total_amount}</p>')
            order_lines.append('<hr>')
        
        html_content = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #333; }}
                h3 {{ color: #666; margin-bottom: 10px; }}
                ul {{ margin-top: 5px; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Order Summary - {restaurant.name}</h1>
            <div class="summary">
                <p><strong>Date:</strong> {order_date.strftime("%A, %B %d, %Y")}</p>
                <p><strong>Total Orders:</strong> {total_orders}</p>
                <p><strong>Total Amount:</strong> ${total_amount}</p>
            </div>
            
            <h2>Orders:</h2>
            {''.join(order_lines)}
            
            <p>Thank you for your service!</p>
            <p><em>This email was sent automatically by Meal of the Day.</em></p>
        </body>
        </html>
        '''
        
        # Plain text version
        plain_content = f'''
        Order Summary - {restaurant.name}
        Date: {order_date.strftime("%A, %B %d, %Y")}
        Total Orders: {total_orders}
        Total Amount: ${total_amount}
        
        Orders:
        ''' + '\n\n'.join([
            f"{order.user.full_name}:\n" + '\n'.join([
                f"  {item.quantity}x {item.menu_item.name} - ${item.price * item.quantity}"
                for item in order.items
            ]) + f"\n  Total: ${order.total_amount}"
            for order in orders
        ])
        
        return EmailService.send_email(
            to_email=restaurant.email,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )
