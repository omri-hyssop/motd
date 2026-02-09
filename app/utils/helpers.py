"""Utility helper functions."""
from datetime import date, timedelta


def get_week_dates(start_date=None, days=7):
    """Get list of dates for the week starting from start_date."""
    if start_date is None:
        start_date = date.today()
    elif isinstance(start_date, str):
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    return [start_date + timedelta(days=i) for i in range(days)]


def get_upcoming_weekdays(start_date=None, count=5):
    """Get upcoming weekdays (Monday-Friday), excluding weekends."""
    if start_date is None:
        start_date = date.today()
    elif isinstance(start_date, str):
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    weekdays = []
    current_date = start_date
    
    while len(weekdays) < count:
        # 0-4 are Monday-Friday, 5-6 are Saturday-Sunday
        if current_date.weekday() < 5:
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    
    return weekdays


def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"


def calculate_order_total(order_items):
    """Calculate total from order items."""
    return sum(item['price'] * item['quantity'] for item in order_items)


def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """Paginate a SQLAlchemy query."""
    per_page = min(per_page, max_per_page)
    page = max(1, page)
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


def parse_time_string(time_str):
    """Parse time string in HH:MM format."""
    from datetime import datetime
    return datetime.strptime(time_str, '%H:%M').time()
