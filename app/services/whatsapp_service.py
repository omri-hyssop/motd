"""WhatsApp Cloud API service."""
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Cloud API."""
    
    @staticmethod
    def send_template_message(to_phone, template_name, parameters):
        """Send a WhatsApp template message."""
        try:
            api_token = current_app.config['WHATSAPP_API_TOKEN']
            phone_number_id = current_app.config['WHATSAPP_PHONE_NUMBER_ID']
            api_version = current_app.config['WHATSAPP_API_VERSION']
            api_url = current_app.config['WHATSAPP_API_URL']
            
            if not all([api_token, phone_number_id]):
                logger.error('WhatsApp API credentials not configured')
                return False, 'WhatsApp not configured'
            
            url = f"{api_url}/{api_version}/{phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Build template message payload
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': 'en'
                    },
                    'components': [
                        {
                            'type': 'body',
                            'parameters': [
                                {'type': 'text', 'text': str(param)}
                                for param in parameters
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f'WhatsApp message sent successfully to {to_phone}')
                return True, response.json()
            else:
                logger.error(f'WhatsApp API error: {response.status_code} - {response.text}')
                return False, response.text
                
        except Exception as e:
            logger.error(f'Error sending WhatsApp message: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def send_order_reminder(user, order_date, order_url):
        """Send order reminder to user."""
        if not user.phone_number:
            logger.warning(f'User {user.id} has no phone number')
            return False, 'No phone number'
        
        # Format phone number (ensure it has country code)
        phone = user.phone_number
        if not phone.startswith('+'):
            # Assume default country code if not provided
            phone = f'+{phone}'
        
        # Template parameters: user first name, order date, order URL
        parameters = [
            user.first_name,
            order_date.strftime('%A, %B %d'),
            order_url
        ]
        
        # Use WhatsApp template (must be pre-approved in Meta Business)
        template_name = 'meal_reminder'  # This should match your approved template
        
        return WhatsAppService.send_template_message(phone, template_name, parameters)
    
    @staticmethod
    def send_text_message(to_phone, message):
        """Send a plain text WhatsApp message (for testing)."""
        try:
            api_token = current_app.config['WHATSAPP_API_TOKEN']
            phone_number_id = current_app.config['WHATSAPP_PHONE_NUMBER_ID']
            api_version = current_app.config['WHATSAPP_API_VERSION']
            api_url = current_app.config['WHATSAPP_API_URL']
            
            if not all([api_token, phone_number_id]):
                logger.error('WhatsApp API credentials not configured')
                return False, 'WhatsApp not configured'
            
            url = f"{api_url}/{api_version}/{phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
                
        except Exception as e:
            logger.error(f'Error sending WhatsApp text: {str(e)}')
            return False, str(e)
