from datetime import date
from django.db import models
from django.utils.timezone import now
from django.db import models

from django.contrib.auth.models import User
class tbl_category(models.Model):
    QUANTITY_METHODS = [
        ("manual", "Manual Entry"),  
        ("shade_based", "Shade-Based"),  
        ("custom", "Custom Calculation")  
    ]

    category_name = models.CharField(max_length=100, unique=True)
    category_description = models.TextField(blank=True, null=True)
    quantity_calculation_method = models.CharField(
        max_length=20, choices=QUANTITY_METHODS, default="manual"
    )  # Defines how quantity is calculated

    def __str__(self):
        return self.category_name
class tbl_product(models.Model):
    product_name = models.CharField(max_length=150)
    product_description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        tbl_category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    additional_image_1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    additional_image_2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    additional_image_3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    available_shades = models.JSONField(default=dict, blank=True, null=True)  # Example: {"#ff0000": 5, "#00ff00": 3}

    def save(self, *args, **kwargs):
        """
        Calculate total quantity based on category's calculation method or category name for paints
        """
        # Check if it's shade-based explicitly or if it's a paint category
        is_shade_based = (self.category.quantity_calculation_method == "shade_based" or 
                          self.category.category_name.lower() == "paints")
        
        if is_shade_based:
            # For shade-based products, sum up all shade quantities
            self.quantity = sum(self.available_shades.values()) if self.available_shades else 0
            
            # If it's a paint category but not marked as shade-based, ensure consistency
            if self.category.quantity_calculation_method != "shade_based" and self.category.category_name.lower() == "paints":
                self.category.quantity_calculation_method = "shade_based"
                self.category.save()
        
        # For manual and other methods, quantity is directly managed
        super().save(*args, **kwargs)
    
    @property
    def total_stock(self):
        """
        Return the total stock available
        """
        return self.quantity
    
    def is_available(self):
        return self.total_stock > 0
    
    def __str__(self):
        return self.product_name


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE_CHOICES, null=False)
    phone = models.CharField(max_length=15, null=False)
    approched_by_staff = models.BooleanField(default=False)
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='approached_customers', null=True, blank=True)
    
    def __str__(self):
        return f"{self.userid.username} - {self.customer_type}"



class FieldStaff(models.Model):
    
    userid = models.ForeignKey(User, on_delete=models.CASCADE,related_name='fieldstaff')
    assigned_area = models.CharField(max_length=255)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    incentive_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    join_date = models.DateField(null=False)
    phone = models.CharField(max_length=15, null=False)
    address = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.userid.username} - {self.assigned_area}"

class ShowroomStaff(models.Model):
    
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=255, null=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    join_date = models.DateField(null=False)
    phone = models.CharField(max_length=15, null=False)
    address = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.userid.username} - {self.department}"

class Order(models.Model):
    PAYMENT_METHODS = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed','completed'),
        ('delivered', 'delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    invoice_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    date = models.DateField(default=now)
    field_staff = models.ForeignKey(FieldStaff, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cod')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_date = models.DateField(null=True, blank=True)  # Stores shipped date
    delivery_date = models.DateField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True) 
    
    STATUS_CHOICES_delivery = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    status_delivery = models.CharField(max_length=10, choices=STATUS_CHOICES_delivery, default='pending')
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Check if this is a new order or an existing one
        is_new = self.pk is None
        
        if not is_new:
            old_order = Order.objects.get(pk=self.pk)
            old_status = old_order.status
            
            # If status changed to 'completed', update inventory (decrease stock)
            if old_status != 'completed' and self.status == 'completed':
                self.update_inventory(decrease=True)
            
            # If status changed from 'completed' to 'cancelled', restore inventory
            elif old_status == 'completed' and self.status == 'cancelled':
                self.update_inventory(decrease=False)
        
        super().save(*args, **kwargs)
        
        # If it's a new completed order, update inventory immediately
        if is_new and self.status == 'completed':
            self.update_inventory(decrease=True)
    
    def cancel_order(self):
        """
        Utility method to cancel an order and restore inventory if needed
        """
        old_status = self.status
        self.status = 'cancelled'
        self.status_delivery = 'cancelled'
        
        # If the order was completed, restore inventory
        if old_status == 'completed':
            self.update_inventory(decrease=False)
            
        self.save(update_fields=['status', 'status_delivery'])
    
    def update_inventory(self, decrease=True):
  
            for item in self.items.all():
                if not item.product:
                    continue
                    
                product = item.product
                
                # Check for both shade-based method and 'paints' category name
                is_shade_based = (product.category.quantity_calculation_method == "shade_based" or 
                                product.category.category_name.lower() == "paints")

                # Handle shade-based products (like paints)
                if is_shade_based and item.color:
                    if not product.available_shades:
                        product.available_shades = {}
                        
                    if decrease:
                        # Decrease stock for the specific shade
                        if item.color in product.available_shades:
                            current_qty = product.available_shades.get(item.color, 0)
                            product.available_shades[item.color] = max(0, current_qty - item.quantity)
                    else:
                        # Increase stock for the specific shade (when cancelling)
                        if item.color in product.available_shades:
                            current_qty = product.available_shades.get(item.color, 0)
                            product.available_shades[item.color] = current_qty + item.quantity
                        else:
                            # Add the shade if it doesn't exist
                            product.available_shades[item.color] = item.quantity
                
                # Handle regular products
                else:
                    if decrease:
                        # Decrease the quantity
                        product.quantity = max(0, product.quantity - item.quantity)
                    else:
                        # Increase the quantity when restoring
                        product.quantity += item.quantity
                
                # Save the product to update stock
                # This will recalculate total quantity for shade-based products automatically
                product.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(tbl_product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    color = models.CharField(max_length=50, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"{self.quantity} x {self.product.product_name if self.product else 'Deleted Product'} ({self.color})"




class Painter(models.Model):
    CURRENT_STATUS_CHOICES = [
        ('available', 'Available'),
        ('onproject', 'On Project'),
        ('unavailable', 'Unavailable'),
    ]

   
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True) 
    experience_years = models.IntegerField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    join_date = models.DateField(default=date.today)
    current_status = models.CharField(max_length=12, choices=CURRENT_STATUS_CHOICES, default='available')
    
    def __str__(self):
        return f"{self.userid.username} - {self.current_status}"

class SiteVisit(models.Model):
    STAGE_OF_CONSTRUCTION_CHOICES = [
        ('foundation', 'Foundation'),
        ('middle', 'Middle'),
        ('final', 'Final'),
    ]

    field_staff = models.ForeignKey('FieldStaff', on_delete=models.CASCADE, related_name='site_visits')
    owner_name = models.CharField(max_length=255, null=True)  # Add this field
    visit_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    large_project = models.BooleanField(default=False)
    site_address = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=100, null=False)
    phone = models.BigIntegerField(null=False)
    square_feet = models.IntegerField(null=False)
    stage_of_construction = models.CharField(
        max_length=10, 
        choices=STAGE_OF_CONSTRUCTION_CHOICES, 
        null=False
    )
    proposed_date_visit = models.DateField()

    def __str__(self):
        return f"Visit ID: {self.id} - {self.site_address}, {self.city}"
# Add these models to your models.py file
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(tbl_product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50)  # Store the selected color code
    color_name = models.CharField(max_length=50, blank=True, null=True)  # Optional friendly name
    added_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} ({self.color})"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class PainterBooking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="painter_bookings")
    painter = models.ForeignKey('Painter', on_delete=models.CASCADE)
    project_completion_date = models.DateField()
    order = models.ForeignKey('Order', on_delete=models.CASCADE,related_name='painter_bookings', null=True, blank=True) 
    square_feet = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.username} - {self.painter.userid.username}"
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import os

class tbl_review(models.Model):
   
    product = models.ForeignKey('tbl_product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified_purchase = models.BooleanField(default=False)
    
    # Fields for review images
    def review_image_path(instance, filename):
        # File will be uploaded to MEDIA_ROOT/review_images/product_<id>/<filename>
        return os.path.join('review_images', f'product_{instance.product.id}', filename)
    
    image1 = models.ImageField(upload_to=review_image_path, blank=True, null=True)
    image2 = models.ImageField(upload_to=review_image_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=review_image_path, blank=True, null=True)
    
    
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('product', 'user')  # Ensure one review per user per product
        ordering = ['-verified_purchase', '-helpful_count', '-created_at']  # Prioritize verified and helpful reviews
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.product.product_name}"
    
    def has_images(self):
        """Check if review has any images"""
        return bool(self.image1 or self.image2 or self.image3)
    
    def get_images(self):
        """Return all non-empty images"""
        images = []
        if self.image1:
            images.append(self.image1)
        if self.image2:
            images.append(self.image2)
        if self.image3:
            images.append(self.image3)
        return images


class ReviewHelpful(models.Model):
    """Tracks which users found which reviews helpful"""
    review = models.ForeignKey(tbl_review, on_delete=models.CASCADE, related_name='helpful_marks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('review', 'user')  

