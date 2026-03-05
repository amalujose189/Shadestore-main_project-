from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_days(value, days):
    """Add a number of days to a date string"""
    try:
        # If the value is already a date, use it directly
        if isinstance(value, datetime.date):
            date_obj = value
        else:
            # Otherwise, parse it from string format
            date_obj = datetime.strptime(value, '%Y-%m-%d').date()
        
        # Add the days
        new_date = date_obj + timedelta(days=int(days))
        return new_date
    except (ValueError, TypeError):
        return value
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Return 0 as default if key doesn't exist