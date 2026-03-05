from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse, path
from django.utils.html import format_html
from django import forms
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
import json
from .views import send_fieldstaff_assignment_email
from .models import (
    Customer, Order, PainterBooking, tbl_category, 
    tbl_product, FieldStaff, ShowroomStaff, Painter, Cart
)

# Custom Admin Site
class ShadeStoreAdminSite(admin.AdminSite):
    site_header = "ShadeStore Administration"
    site_title = "ShadeStore Admin"
    index_title = "Welcome to ShadeStore Admin Panel"
    
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        try:
            chat_app = {
                'name': 'Chat',
                'app_label': 'chat',
                'models': [{
                    'name': 'Chat Dashboard',
                    'object_name': 'chat_dashboard',
                    'admin_url': reverse('chat:dashboard'),
                    'view_only': True,
                    'perms': {'view': True},
                }]
            }
            app_list.append(chat_app)
        except Exception:
            pass
        return app_list

custom_admin_site = ShadeStoreAdminSite(name='shadestore_admin')

# Mixins
class AdminSitePreviewMixin:
    def view_site(self, obj=None):
        url = reverse('index')
        return format_html('<a href="{}" target="_blank" style="color: blue;">View Site</a>', url)
    view_site.short_description = "Site Preview"

# Custom ColorShadeWidget

# Admin classes


class ShowroomAdmin(admin.ModelAdmin):
    pass

class PainterAdmin(admin.ModelAdmin):
    pass

class CartAdmin(admin.ModelAdmin):
    pass

class BookingAdmin(admin.ModelAdmin):
    pass

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('userid', 'city', 'state', 'customer_type', 'phone')
    list_filter = ('city', 'state', 'customer_type')
    search_fields = ('userid__username', 'city', 'phone')
    
    def get_email(self, obj):
        return obj.userid.email
    get_email.short_description = 'Email'

class FieldstaffAdmin(admin.ModelAdmin):
    list_display = ('userid', 'assigned_area', 'base_salary', 'join_date', 'phone')
    list_filter = ('assigned_area',)
    search_fields = ('userid__username', 'assigned_area', 'phone')

# Update these parts in your admin.py file
class ColorShadeWidget(forms.Widget):
    template_name = 'admin/widgets/color_shade_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = {}
        
        if attrs is None:
            attrs = {}
        
        # Ensure our widget has the class we're looking for in JavaScript
        attrs['class'] = f"color-shade-widget {attrs.get('class', '')}"
        
        context = self.get_context(name, value, attrs)

        # You should safely deserialize JSON if needed
        import json
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = {}
        elif not isinstance(value, dict):
            value = {}

        context.update({
            'colors': value,
        })

        return render_to_string(self.template_name, context)

# Custom Form for Product
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = tbl_product
        fields = '__all__'
    
    # Add a hidden field to store the JSON data for available_shades
    available_shades_json = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    # Add a visual color picker field (this won't be saved directly)
    color_picker = forms.CharField(
        widget=ColorShadeWidget(),
        required=False,
        label="Color Picker",
        help_text="Click to add colors and set quantities"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Determine if this is a shade-based product
        is_shade_based = False
        if self.instance and self.instance.pk and self.instance.category:
            is_shade_based = (
                self.instance.category.quantity_calculation_method == "shade_based" or
                self.instance.category.category_name.lower() == "paints"
            )
        
        # If it's not a shade-based product, hide the shade-related fields
        if not is_shade_based:
            self.fields['color_picker'].widget = forms.HiddenInput()
            self.fields['color_picker'].disabled = True
            self.fields['available_shades_json'].disabled = True
        else:
            # Pre-populate the color picker with existing shades
            if self.instance and self.instance.pk:
                available_shades = self.instance.available_shades or {}
                # Important: Properly serialize the initial data
                self.fields['color_picker'].initial = available_shades
                self.fields['available_shades_json'].initial = json.dumps(available_shades)
        
        # Make quantity field read-only for shade-based products
        if 'quantity' in self.fields and is_shade_based:
            self.fields['quantity'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Determine if this is a shade-based product
        category = cleaned_data.get('category')
        is_shade_based = False
        if category:
            is_shade_based = (
                category.quantity_calculation_method == "shade_based" or
                category.category_name.lower() == "paints"
            )
        
        # Only process shades for shade-based products
        if is_shade_based:
            # Get the JSON data from the hidden field and parse it
            json_data = cleaned_data.get('available_shades_json', '{}')
            try:
                shade_data = json.loads(json_data)
                # Convert to proper format with integer values
                shade_dict = {}
                for color, quantity in shade_data.items():
                    # Ensure quantity is an integer
                    shade_dict[color] = int(quantity)
                
                cleaned_data['available_shades'] = shade_dict
                
                # For shade-based products, calculate the quantity automatically
                if cleaned_data['available_shades']:
                    cleaned_data['quantity'] = sum(cleaned_data['available_shades'].values())
            except json.JSONDecodeError:
                cleaned_data['available_shades'] = {}
        else:
            # For non-shade-based products, don't use the shade data
            cleaned_data['available_shades'] = {}
            
        return cleaned_data

class ProductAdmin(admin.ModelAdmin, AdminSitePreviewMixin):
    form = ProductAdminForm
    list_display = ('product_name', 'category', 'price', 'quantity', 'view_site')
    list_filter = ('category',)
    search_fields = ('product_name', 'product_description')
    readonly_fields = []  # We'll dynamically set this based on the category

    def get_fieldsets(self, request, obj=None):
        # Standard fieldsets
        fieldsets = [
            ('Basic Information', {
                'fields': ('product_name', 'product_description', 'price', 'category')
            }),
            ('Inventory', {
                'fields': ('quantity',),
                'description': 'For manual entry products, specify quantity directly. For shade-based products, quantity is calculated automatically.'
            }),
            ('Images', {
                'fields': ('main_image', 'additional_image_1', 'additional_image_2', 'additional_image_3')
            }),
        ]
        
        # Check if this is a shade-based product
        is_shade_based = False
        category_id = request.POST.get('category') if request.method == 'POST' else None
        
        if obj and obj.category:
            is_shade_based = (
                obj.category.quantity_calculation_method == "shade_based" or
                obj.category.category_name.lower() == "paints"
            )
        elif category_id:
            try:
                category = tbl_category.objects.get(id=category_id)
                is_shade_based = (
                    category.quantity_calculation_method == "shade_based" or
                    category.category_name.lower() == "paints"
                )
            except (tbl_category.DoesNotExist, ValueError):
                pass
        
        # Only include the Available Shades section for shade-based products
        if is_shade_based:
            fieldsets.append(
                ('Available Shades', {
                    'fields': ('color_picker', 'available_shades_json'),
                    'description': 'Add color codes and quantities for this shade-based product.'
                })
            )
        
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # Make quantity field read-only for shade-based products
        if obj and obj.category:
            is_shade_based = (
                obj.category.quantity_calculation_method == "shade_based" or
                obj.category.category_name.lower() == "paints"
            )
            
            if is_shade_based and 'quantity' not in readonly_fields:
                readonly_fields.append('quantity')
        
        return readonly_fields

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
        js = ('admin/js/color_picker.js',)
    
    def save_model(self, request, obj, form, change):
        # First, get the shade data from the form's cleaned data
        if 'available_shades' in form.cleaned_data:
            # Explicitly set the available_shades on the model instance
            obj.available_shades = form.cleaned_data['available_shades']
        
        # Then call the original save_model
        super().save_model(request, obj, form, change)
        
        # Show a message to explain calculation method
        if obj.category.quantity_calculation_method == "shade_based":
            messages.info(request, f"Product quantity ({obj.quantity}) was automatically calculated from the sum of shade quantities.")

# Other admin classes...
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'quantity_calculation_method')
    list_filter = ('quantity_calculation_method',)
    search_fields = ('category_name', 'category_description')
class OrderAssignmentForm(forms.Form):
    field_staff = forms.ModelChoiceField(
        queryset=FieldStaff.objects.none(),
        label="Assign to field staff member",
        required=True
    )
    delivery_date = forms.DateField(
        label="Expected Delivery Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'customer', 'total_amount', 'payment_method', 'customer_location', 'status_delivery', 'assigned_to', 'delivery_date', 'assign_action')
    list_filter = ('status_delivery', 'payment_method', 'date', 'delivery_date')
    search_fields = ('id', 'customer__userid__username', 'customer__city')
    readonly_fields = ('date', 'total_amount')

    def customer_location(self, obj):
        if obj.customer:
            return f"{obj.customer.city}, {obj.customer.state}" if obj.customer.city and obj.customer.state else "Location not specified"
        return "No customer information"
    customer_location.short_description = "Customer Location"

    def assigned_to(self, obj):
        if hasattr(obj, 'field_staff') and obj.field_staff:
            return f"{obj.field_staff.userid.username} ({obj.field_staff.assigned_area})"
        return "Not assigned"
    assigned_to.short_description = "Assigned To"

    def assign_action(self, obj):
        if not hasattr(obj, 'field_staff') or not obj.field_staff:
            url = reverse('admin:ecom_order_assign_order', args=[obj.pk])
            return format_html('<a class="button" href="{}">Assign Delivery</a>', url)
        else:
            url = reverse('admin:ecom_order_reassign_order', args=[obj.pk])
            return format_html('<a class="button" href="{}">Reassign</a>', url)
    assign_action.short_description = "Assignment"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/assign/', self.admin_site.admin_view(self.assign_order_view), name='ecom_order_assign_order'),
            path('<int:order_id>/reassign/', self.admin_site.admin_view(self.reassign_order_view), name='ecom_order_reassign_order'),
        ]
        return custom_urls + urls

    def assign_order_view(self, request, order_id):
        order = Order.objects.get(id=order_id)
        customer = order.customer
        customer_city = order.customer.city if order.customer and order.customer.city else ""
        customer_state = order.customer.state if order.customer and order.customer.state else ""
        initial_data = {'delivery_date': order.delivery_date} if order.delivery_date else {}
        form = OrderAssignmentForm(initial=initial_data)

        matching_staff = []
        for staff in FieldStaff.objects.all():
            if (customer_city and customer_city.lower() in staff.assigned_area.lower()) or \
               (customer_state and customer_state.lower() in staff.assigned_area.lower()):
                matching_staff.append(staff.id)
        
        form.fields['field_staff'].queryset = FieldStaff.objects.filter(id__in=matching_staff) if matching_staff else FieldStaff.objects.all()
        form.fields['field_staff'].help_text = f"Matching area: {customer_city}, {customer_state}" if matching_staff else "No match found. Showing all."

        if request.method == 'POST':
            form = OrderAssignmentForm(request.POST)
            form.fields['field_staff'].queryset = FieldStaff.objects.all()
            if form.is_valid():
                field_staff = form.cleaned_data['field_staff']
                order.field_staff = field_staff
                order.delivery_date = form.cleaned_data['delivery_date']
                order.status_delivery = 'shipped'
                order.save()
                
                # Send email notification to field staff
                if customer:  # Make sure customer exists
                    send_fieldstaff_assignment_email(order, field_staff, customer)
                
                self.message_user(request, f"Order #{order_id} assigned to {order.field_staff.userid.username}")
                return redirect('admin:ecom_order_changelist')

        context = {
            'title': f'Assign Order #{order_id}',
            'form': form,
            'order': order,
            'opts': self.model._meta,
            'original': order,
        }
        return render(request, 'admin/assign_order.html', context)

    def reassign_order_view(self, request, order_id):
        order = Order.objects.get(id=order_id)
        customer = order.customer
        current_staff = order.field_staff
        initial_data = {'delivery_date': order.delivery_date} if order.delivery_date else {}
        form = OrderAssignmentForm(initial=initial_data)
        form.fields['field_staff'].queryset = FieldStaff.objects.all()

        if request.method == 'POST':
            form = OrderAssignmentForm(request.POST)
            form.fields['field_staff'].queryset = FieldStaff.objects.all()
            if form.is_valid():
                new_staff = form.cleaned_data['field_staff']
                order.field_staff = new_staff
                order.delivery_date = form.cleaned_data['delivery_date']
                order.status_delivery = 'shipped'
                order.save()
                
                # Send email notification to the new field staff
                if customer:  # Make sure customer exists
                    send_fieldstaff_assignment_email(order, new_staff, customer)
                
                self.message_user(request, f"Order #{order_id} reassigned from {current_staff.userid.username} to {new_staff.userid.username}")
                return redirect('admin:ecom_order_changelist')

        context = {
            'title': f'Reassign Order #{order_id}',
            'form': form,
            'order': order,
            'current_staff': current_staff,
            'opts': self.model._meta,
            'original': order,
        }
        return render(request, 'admin/reassign_order.html', context)
    
# Register models to Default Admin
admin.site.register(tbl_category, CategoryAdmin)
admin.site.register(FieldStaff, FieldstaffAdmin)
admin.site.register(ShowroomStaff, ShowroomAdmin)
admin.site.register(Painter, PainterAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(PainterBooking, BookingAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(tbl_product, ProductAdmin)

# Register models to Custom Admin
custom_admin_site.register(tbl_category, CategoryAdmin)
custom_admin_site.register(FieldStaff, FieldstaffAdmin)
custom_admin_site.register(ShowroomStaff, ShowroomAdmin)
custom_admin_site.register(Painter, PainterAdmin)
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(PainterBooking, BookingAdmin)
custom_admin_site.register(Customer, CustomerAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(tbl_product, ProductAdmin)


# Custom User Admin Implementation
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# Safely unregister and register User admin for both admin sites
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

try:
    custom_admin_site.unregister(User)
except admin.sites.NotRegistered:
    pass
custom_admin_site.register(User, CustomUserAdmin)
