# In your_app/templatetags/user_role_tags.py
from django import template
from ecom.models import FieldStaff, ShowroomStaff, Customer, Painter

register = template.Library()

@register.filter
def is_fieldstaff(user):
    if not user.is_authenticated:
        return False
    return FieldStaff.objects.filter(userid=user).exists()

@register.filter
def is_showroomstaff(user):
    if not user.is_authenticated:
        return False
    return ShowroomStaff.objects.filter(userid=user).exists()

@register.filter
def is_customer(user):
    if not user.is_authenticated:
        return False
    return Customer.objects.filter(userid=user).exists()

@register.filter
def is_painter(user):
    if not user.is_authenticated:
        return False
    return Painter.objects.filter(userid=user).exists()