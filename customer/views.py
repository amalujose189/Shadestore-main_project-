from django.shortcuts import render
import csv
import datetime
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from ecom.models import FieldStaff, ShowroomStaff, Customer, Painter,SiteVisit,tbl_product
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, FieldStaffUpdateForm,SiteVisitForm
from django.urls import reverse
from django.http import JsonResponse

# Create your views here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    field_staff = models.ForeignKey(FieldStaff, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(tbl_product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"
    
    def get_total(self):
        return self.price * self.quantity
    