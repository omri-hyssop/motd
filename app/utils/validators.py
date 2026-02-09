"""Input validation helpers."""
import re
from datetime import date, datetime, timedelta


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format (basic validation)."""
    if not phone:
        return True  # Phone is optional
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"


def validate_date_range(start_date, end_date):
    """Validate date range."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    return True, "Date range is valid"


def validate_future_date(target_date, allow_today=True):
    """Validate that date is in the future."""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    today = date.today()
    
    if allow_today:
        if target_date < today:
            return False, "Date must be today or in the future"
    else:
        if target_date <= today:
            return False, "Date must be in the future"
    
    return True, "Date is valid"


def validate_price(price):
    """Validate price is positive."""
    try:
        price_float = float(price)
        if price_float <= 0:
            return False, "Price must be positive"
        return True, "Price is valid"
    except (ValueError, TypeError):
        return False, "Invalid price format"
