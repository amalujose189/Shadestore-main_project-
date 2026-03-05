'''from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request,'index.html')
def register(request):
    return render(request,'register.html')
def collections(request):
    return render(request,"collections.html")'''
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import csv
import datetime
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
import razorpay
from .models import *
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ShadeStore import settings
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import FieldStaff, ShowroomStaff, Customer, Painter,SiteVisit,tbl_review,ReviewHelpful
from django.contrib.auth.decorators import login_required
from .forms import CustomerUpdateForm, ReviewForm, UserUpdateForm, FieldStaffUpdateForm,SiteVisitForm
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import tbl_product, Customer
from decimal import Decimal
from .models import Cart,CartItem
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from ecom.forms import CustomerRegistrationForm
from django.db.models import Sum
from collections import Counter
from django.db.models import Avg, Count
from django.core.paginator import Paginator

def index(request):
    categories = tbl_category.objects.prefetch_related('products').all()
    context = {
        'categories': categories
    }
    return render(request, 'index.html', context)
# views.py

from django.shortcuts import render
from django.db.models import Q  # Make sure this import is included
from .models import tbl_product, tbl_category
def search_products(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', 'all')
    
    # Start with all products - but only if we have some filters
    # Otherwise, show empty results until user applies a filter
    if query or category_id != 'all':
        products = tbl_product.objects.all()
        
        # Filter by category if specified
        if category_id != 'all' and category_id.isdigit():
            products = products.filter(category_id=category_id)
        
        # Filter by search query if provided
        if query:
            products = products.filter(
                Q(product_name__icontains=query) | 
                Q(product_description__icontains=query) |
                Q(category__category_name__icontains=query)
            ).distinct()
    else:
        # No filters applied, show empty products list
        products = tbl_product.objects.none()
    
    # Get all categories for the dropdown
    categories = tbl_category.objects.all()
    
    # Get the selected category for display
    selected_category = None
    if category_id != 'all' and category_id.isdigit():
        selected_category = tbl_category.objects.filter(id=category_id).first()
    
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'category_id': category_id,
        'filters_applied': (query != '' or category_id != 'all')
    }
    
    return render(request, 'search_result.html', context)
def filter_by_category(request, category_id):
    # Redirect to search page with the category pre-selected
    return redirect(f'/search/?category={category_id}')
''''def product_detail(request, product_id):
    product = tbl_product.objects.get(id=product_id)
    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context)'''

def category_detail(request, category_id):
    category = tbl_category.objects.get(id=category_id)
    products = category.products.all()
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'category_detail.html', context)


class SignupView(CreateView):
    model = User
    form_class = CustomerRegistrationForm
    template_name = 'login.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # Get form data
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        phone = form.cleaned_data['phone']
        
        # Create user object manually
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(password)  # Important: set_password hashes the password
        user.save()
        
        # Create customer object
        customer = Customer(
            userid=user,
            phone=phone,
            customer_type='online'  # Default value
        )
        customer.save()
        
        messages.success(self.request, 'Account created successfully!')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your form. Please check the information and try again.')
        return super(SignupView, self).form_invalid(form)

'''def signup(request):
    if request.method == "POST":
        # Collect form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validate data
        if not (first_name and last_name and username and email and phone and password1 and password2):
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords don't match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        try:
            with transaction.atomic():  # Ensure both User and Customer are created together
                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )

                # Create Customer profile
                customer = Customer.objects.create(
                    userid=user,  # ForeignKey linking to User
                    phone=phone,
                    customer_type='online'  # Default value
                )

                # Log the user in
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('home')

        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('signup')

    return render(request, 'login.html')


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Check if the input is an email or username
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or username.')
                return redirect('login_view')
        else:
            username = username_or_email

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # First check if user is admin/superuser
                if user.is_superuser:
                    return redirect('admin:index')  # Redirect to admin dashboard
                
                # Then check other roles
                if FieldStaff.objects.filter(userid=user).exists():
                    return redirect('fieldstaff_dashboard')
                elif ShowroomStaff.objects.filter(userid=user).exists():
                    return redirect('showroomstaff_dashboard')
                elif Customer.objects.filter(userid=user).exists():
                    return redirect('index')  # Redirect customers to the home page
                elif Painter.objects.filter(userid=user).exists():
                    return redirect('painter_dashboard')
                else:
                    messages.error(request, 'You do not have a valid role.')
                    logout(request)  # Logout user if no valid role
                    return redirect('login_view')
            else:
                messages.error(request, 'Your account is disabled.')
                return redirect('login_view')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('login_view')

    return render(request, 'login.html')'''
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()  # Ensure it's a string
        password = request.POST.get('password', '')

        if not username_or_email:
            messages.error(request, 'Username or email is required.')
            return redirect('login_view')

        if '@' in username_or_email:
            user = User.objects.filter(email=username_or_email).first()  # Use filter().first() to avoid exceptions
            if user:
                username = user.username
            else:
                messages.error(request, 'Invalid email or username.')
                return redirect('login_view')
        else:
            username = username_or_email

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Check user roles
                if user.is_superuser:
                    return redirect('admin:index')
                elif FieldStaff.objects.filter(userid=user).exists():
                    return redirect('fieldstaff_dashboard')
                elif ShowroomStaff.objects.filter(userid=user).exists():
                    return redirect('showroomstaff_dashboard')
                elif Customer.objects.filter(userid=user).exists():
                    return redirect('index')  # Redirect customers to home
                elif Painter.objects.filter(userid=user).exists():
                    return redirect('painter:painter_dashboard')
                else:
                    messages.error(request, 'You do not have a valid role.')
                    logout(request)
                    return redirect('login_view')
            else:
                messages.error(request, 'Your account is disabled.')
                return redirect('login_view')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('login_view')

    return render(request, 'registration/login.html')

def fieldstaff_dashboard(request):
    return render(request,'fieldstaff_dash.html')
def showroomstaff_dashboard(request):
    return render(request,'showroomstaff_dash.html')
def painter_dashboard(request):
    return render(request,'painter_dash.html')
def fieldstaff(request):
    return render(request,'fieldstaff.html')



@login_required(login_url='login_view')
def profile_update(request):
    # Get FieldStaff instance
    try:
        fieldstaff = FieldStaff.objects.get(userid=request.user)
    except FieldStaff.DoesNotExist:
        messages.error(request, 'Field Staff profile not found.')
        return redirect('index')  # or wherever you want to redirect
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        fieldstaff_form = FieldStaffUpdateForm(request.POST, instance=fieldstaff)
        
        if user_form.is_valid() and fieldstaff_form.is_valid():
            user_form.save()
            fieldstaff_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        fieldstaff_form = FieldStaffUpdateForm(instance=fieldstaff)

    context = {
        'user_form': user_form,
        'fieldstaff_form': fieldstaff_form,
        'fieldstaff': fieldstaff
    }
    return render(request, 'fieldstaff_updateProfile.html', context)

@login_required(login_url='/login_view/')
def customer_profile_update(request):
    customer = Customer.objects.filter(userid=request.user).first()  # Avoids crash

    if not customer:
        messages.error(request, "Customer profile not found.")
        return redirect('index')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        customer_form = CustomerUpdateForm(request.POST, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('customer_profile_update')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        customer_form = CustomerUpdateForm(instance=customer)

    return render(request, 'customerupdateprof.html', {
        'user_form': user_form,
        'customer_form': customer_form,
        'customer': customer
    })
@login_required(login_url='login_view')
def site_visit_list(request):
    site_visits = SiteVisit.objects.all().order_by('-visit_date')
    return render(request, 'site_visit_list.html', {'site_visits': site_visits})

@login_required(login_url='login_view')
def site_visit_detail(request, pk):
    site_visit = get_object_or_404(SiteVisit, pk=pk)  # pk refers to the primary key (id)
    return render(request, 'fieldstaff_viewVisit.html', {'site_visit': site_visit})

@login_required(login_url='login_view')
def create_site_visit(request):
    try:
        field_staff = FieldStaff.objects.get(userid=request.user)
    except FieldStaff.DoesNotExist:
        messages.error(request, 'Field Staff profile not found.')
        return redirect('index')

    if request.method == 'POST':
        form = SiteVisitForm(request.POST)
        if form.is_valid():
            site_visit = form.save(commit=False)
            site_visit.field_staff = field_staff  # Set the field_staff to the logged-in user
            site_visit.save()
            messages.success(request, 'Site visit created successfully!')
            return redirect('site_visit_detail', pk=site_visit.id)  # Use site_visit.id instead of site_visit.visit_id
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SiteVisitForm()
    
    return render(request, 'fieldstaff_sitevisit.html', {
        'form': form,
        'title': 'Create Site Visit',
        'button_label': 'Create'
    })
@login_required(login_url='login_view')
def edit_site_visit(request, pk):
    site_visit = get_object_or_404(SiteVisit, pk=pk)  # Use pk (id) instead of visit_id
    
    # Check if the logged-in user is the owner of this site visit
    if site_visit.field_staff.userid != request.user:
        messages.error(request, 'You do not have permission to edit this site visit.')
        return redirect('site_visit_list')
        
    if request.method == 'POST':
        form = SiteVisitForm(request.POST, instance=site_visit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site visit updated successfully!')
            return redirect('site_visit_detail', pk=site_visit.id)  # Use site_visit.id instead of site_visit.visit_id
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SiteVisitForm(instance=site_visit)
    
    return render(request, 'fieldstaff_sitevisit.html', {
        'form': form,
        'title': 'Edit Site Visit',
        'button_label': 'Update'
    })

@login_required(login_url='login_view')
def delete_site_visit(request, pk):
    site_visit = get_object_or_404(SiteVisit, pk=pk)  # Use pk (id) instead of visit_id
    if request.method == 'POST':
        site_visit.delete()
        messages.success(request, 'Site visit deleted successfully!')
        return redirect('site_visit_list')
    return render(request, 'site_visit_delete.html', {
        'site_visit': site_visit
    })
@login_required(login_url='login_view')
def download_site_visits_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="site_visits.csv"'
    writer = csv.writer(response)
    writer.writerow(['Visit Date', 'Site Address', 'City', 'Owner Name', 'Phone', 'Square Feet', 'Stage of Construction', 'Proposed Visit Date', 'Large Project', 'Comments'])
    site_visits = SiteVisit.objects.all()
    for site_visit in site_visits:
        writer.writerow([
            site_visit.visit_date,
            site_visit.site_address,
            site_visit.city,
            site_visit.owner_name,
            site_visit.phone,
            site_visit.square_feet,
            site_visit.get_stage_of_construction_display(),
            site_visit.proposed_date_visit,
            'Yes' if site_visit.large_project else 'No',
            site_visit.comments,
        ])
    return response


def fetch_print_data(request):
    print_option = request.GET.get("print_option", "all")
    selected_dates = request.GET.get("selected_dates", "").split(",")

    if print_option == "all":
        site_visits = SiteVisit.objects.all()
    elif print_option == "date" and selected_dates:
        site_visits = SiteVisit.objects.filter(visit_date__in=selected_dates)
    else:
        site_visits = []

    data = {
        "site_visits": [
            {
                "owner_name": visit.owner_name,
                "visit_date": visit.visit_date.strftime("%Y-%m-%d"),
                "city": visit.city,
                "phone": visit.phone,
                "square_feet": visit.square_feet,
                "stage_of_construction": visit.get_stage_of_construction_display(),
                "proposed_date_visit": visit.proposed_date_visit.strftime("%Y-%m-%d") if visit.proposed_date_visit else "N/A"
            }
            for visit in site_visits
        ]
    }
    return JsonResponse(data)


from django.views.generic import DetailView

class SiteVisitDetailView(DetailView):
    model = SiteVisit
    template_name = 'site_visit_detailView.html'
    context_object_name = 'site_visit'



# View for product details
'''def product_detail(request, product_id):
    product = get_object_or_404(tbl_product, id=product_id)
    
    # Get related products from the same category
    related_products = tbl_product.objects.filter(
        category=product.category
    ).exclude(id=product_id)[:4]  # Limit to 4 related products
    colors = ["white", "beige", "blue", "green", "yellow", "red"] 
    context = {
        'product': product,
        'related_products': related_products,
        'colors': colors,
    }
    return render(request, 'productdetails.html', context)'''
from django.db.models import Avg, Count

def product_detail(request, product_id):
    product = get_object_or_404(tbl_product, id=product_id)

    # Related products
    related_products = tbl_product.objects.filter(
        category=product.category
    ).exclude(id=product_id)[:4]

    # Only provide colors for paint products
    colors = []
    is_paint = product.category.category_name.lower() == 'paints'
    if is_paint:
        colors = ["white", "beige", "blue", "green", "yellow", "red"]

    # Field staff check
    is_fieldstaff = False
    if request.user.is_authenticated:
        is_fieldstaff = hasattr(request.user, 'profile') and request.user.profile.role == 'fieldstaff'

    # Reviews and rating stats
    reviews = tbl_review.objects.filter(product=product)
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # Star-wise counts (1 to 5)
    rating_counts_raw = reviews.values('rating').annotate(count=Count('rating'))
    rating_counts = {str(i): 0 for i in range(1, 6)}  # Initialize all with 0
    for entry in rating_counts_raw:
        rating_counts[str(entry['rating'])] = entry['count']

    # Percentage calculation
    rating_percentages = {
        star: (count / total_reviews) * 100 if total_reviews > 0 else 0
        for star, count in rating_counts.items()
    }
    
    # Check if user has already reviewed this product
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = reviews.filter(user=request.user).exists()
    
    # Initialize review form
    review_form = None
    if request.user.is_authenticated and not has_reviewed:
        review_form = ReviewForm()
    
    # Reviews with images
    reviews_with_images = reviews.filter(
        Q(image1__isnull=False) | 
        Q(image2__isnull=False) | 
        Q(image3__isnull=False)
    ).distinct()

    # Product JSON for JavaScript
    product_json = json.dumps({
        'id': product.id,
        'name': product.product_name,
        'price': float(product.price),
        'total_stock': product.total_stock
    })

    context = {
        'product': product,
        'related_products': related_products,
        'colors': colors,
        'is_fieldstaff': is_fieldstaff,
        'is_paint': is_paint,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
        'review_form': review_form,  # Add review form to context
        'has_reviewed': has_reviewed,  # Add has_reviewed flag
        'reviews_with_images': reviews_with_images,  # Add reviews with images
        'product_json': product_json,  # Add product JSON for JavaScript
    }

    return render(request, 'productdetailss.html', context)

# Add to cart functionality

from django.contrib import messages
from .models import tbl_product, Cart, CartItem

@login_required(login_url='login_view')
def add_to_cart(request, product_id):
    product = get_object_or_404(tbl_product, id=product_id)
    
    if request.method == 'POST':
        # Determine if the product is a paint (requires color) or wallpaper (quantity only)
        is_paint = product.category.category_name.lower() == 'paints'
        
        # Get color only for paints
        color = request.POST.get('selected_color') if is_paint else None
        
        # Validate color for paints
        if is_paint:
            if not color:
                messages.error(request, 'Please select a shade color')
                return redirect('product_detail', product_id)
            
            # Validate stock for specific color
            if color not in product.available_shades or product.available_shades.get(color, 0) <= 0:
                messages.error(request, 'Selected color is not available')
                return redirect('product_detail', product_id)
        
        # Get and validate quantity
        quantity = int(request.POST.get('quantity', 1))
        
        # Check product availability
        if not product.is_available() or quantity <= 0:
            messages.error(request, 'Product is not available in the selected quantity')
            return redirect('product_detail', product_id)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        try:
            # Different logic for paints and wallpapers
            if is_paint:
                # For paints, use color in lookup
                cart_item = CartItem.objects.get(cart=cart, product=product, color=color)
                cart_item.quantity += quantity
                cart_item.save()
            else:
                # For wallpapers, create or update without color
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=product, 
                    color='',  # Empty string for non-color products
                    defaults={
                        'quantity': quantity,
                        'price': product.price
                    }
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
        except CartItem.DoesNotExist:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                color=color if is_paint else '',
                quantity=quantity,
                price=product.price
            )
        
        messages.success(request, f'{product.product_name} added to your cart')
        return redirect('cart')
    
    return redirect('product_detail', product_id)
  
@login_required(login_url='login_view') # Redirect to login page if not authenticated
def cart(request):
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get all cart items for the logged-in user
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate the total price
    cart_total = sum(item.subtotal for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    
    return render(request, 'cart.html', context)

@login_required(login_url='login_view')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    
    # Get available stock for the item
    available_stock = cart_item.product.available_shades.get(cart_item.color, 0)
    
    if action == 'increase':
        # Check if there's enough stock
        if cart_item.quantity < available_stock:
            cart_item.quantity += 1
            messages.success(request, 'Item quantity increased.')
        else:
            messages.error(request, f'Cannot add more items. Only {available_stock} available in stock.')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            messages.success(request, 'Item quantity decreased.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
            return redirect('cart')
    
    cart_item.save()
    return redirect('cart')

@login_required(login_url='login_view')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')



def send_painter_booking_email(booking, customer):
    painter = booking.painter
    subject = f"New Painting Job Assigned - {booking.project_completion_date}"
    
    # Build location string from customer's address
    location_parts = []
    if customer.address:
        location_parts.append(customer.address)
    if customer.city:
        location_parts.append(customer.city)
    if customer.state:
        location_parts.append(customer.state)
    
    location = ", ".join(location_parts) if location_parts else "Location not specified"
    
    context = {
        'painter': painter,
        'booking': booking,
        'customer': customer,
        'project_date': booking.project_completion_date,
        'location': location,
        'square_feet': booking.square_feet,
        'order': booking.order,
        'customer_phone': customer.phone,
    }
    
    html_message = render_to_string('emails/painter_booking_notification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email='amalmanoj396@gmail.com',
        recipient_list=[painter.userid.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_fieldstaff_assignment_email(order, field_staff, customer):
    subject = f"New Order Assignment - Order #{order.id}"
    
    # Build location string from customer's address
    location_parts = []
    if customer.address:
        location_parts.append(customer.address)
    if customer.city:
        location_parts.append(customer.city)
    if customer.state:
        location_parts.append(customer.state)
    
    location = ", ".join(location_parts) if location_parts else "Location not specified"
    
    context = {
        'order': order,
        'field_staff': field_staff,
        'customer': customer,
        'delivery_address': location,
        'order_items': order.items.all(),
        'total_amount': order.total_amount,
        'customer_phone': customer.phone,
    }
    
    html_message = render_to_string('emails/fieldstaff_assignment_notification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email='amalmanoj396@gmail.com',
        recipient_list=[field_staff.userid.email],
        html_message=html_message,
        fail_silently=False,
    )


@login_required(login_url='/login/')



@login_required(login_url='login_view')
def checkout(request):
    # Get the user's cart
    cart = get_object_or_404(Cart, user=request.user)
    customer = Customer.objects.filter(userid=request.user).first()
    
    # Check if this is a "Buy Now" request
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity')
    selected_color = request.GET.get('selected_color')
    
    if product_id and quantity:
        # This is a "Buy Now" request
        CartItem.objects.filter(cart=cart).delete()
        
        # Add the specific product to the cart
        product = get_object_or_404(tbl_product, id=product_id)
        is_paint = product.category.category_name.lower() == 'paints'
        
        CartItem.objects.create(
            cart=cart,
            product=product,
            color=selected_color if is_paint and selected_color else '',
            quantity=int(quantity),
            price=product.price
        )
    
    # Get updated cart items
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        messages.error(request, "Your cart is empty. Add items before checkout.")
        return redirect('cart')

    total_amount = sum(item.subtotal for item in cart_items)
    field_staff_list = FieldStaff.objects.all()
    available_painters = Painter.objects.filter(current_status='available')
    is_customer = Customer.objects.filter(userid=request.user).exists()
    
    if request.method == "POST":
        # Get all form data
        payment_method = request.POST.get('payment_method')
        approached_by_staff = request.POST.get('approached_by_staff') == 'yes'
        field_staff_id = request.POST.get('field_staff') if approached_by_staff else None
        need_painter = request.POST.get('need_painter') == 'yes'
        painter_id = request.POST.get('painter_id') if need_painter else None
        project_completion_date = request.POST.get('project_completion_date') if need_painter else None
        square_feet = request.POST.get('square_feet') if need_painter else None

        field_staff = None
        if field_staff_id:
            field_staff = FieldStaff.objects.get(id=field_staff_id)
        
        # Create the order
        order = Order.objects.create(
            user=request.user,
            customer=customer,
            total_amount=total_amount,
            payment_method=payment_method,
            status='pending',
            field_staff=field_staff
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                color=item.color,
                subtotal=item.subtotal
            )
        
        # If customer was approached by field staff, update customer record
        if is_customer and approached_by_staff and field_staff_id:
            customer = Customer.objects.get(userid=request.user)
            customer.approched_by_staff = True
            staff_member = get_object_or_404(User, id=field_staff_id)
            customer.staff_member = staff_member
            customer.save()
        
        # If customer needs painter, create painter booking
        if is_customer and need_painter and painter_id and project_completion_date and square_feet:
            painter_booking = PainterBooking.objects.create(
                customer=request.user,
                painter_id=painter_id,
                project_completion_date=project_completion_date,
                square_feet=square_feet,
                status='pending',
                order=order
            )
            
            # Send email to painter with customer's address
            send_painter_booking_email(painter_booking, customer)
        
        # If field staff is assigned, send them email with customer's address
        if field_staff:
            send_fieldstaff_assignment_email(order, field_staff, customer)
        
        # Clear cart after successful order creation
        cart_items.delete()
        #messages.success(request, "Order placed successfully!")
        return redirect('order_confirmation', order_id=order.id)
    
    
    # GET request handling
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'field_staff_list': field_staff_list,
        'available_painters': available_painters,
        'is_customer': is_customer,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    } 
    return render(request, 'cartCheckout.html', context)


@login_required(login_url='login_view')
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    painter_booking = request.user.painter_bookings.first()

    return render(request, 'order_confirmation.html', {
        'order': order,
        'painter_booking': painter_booking
    })
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
@login_required
@require_POST
@csrf_protect
def confirm_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Update order status to completed
        order.status = 'completed'
        order.save()

        return JsonResponse({'success': True})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
@login_required(login_url='login_view')
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        # Initialize Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Verify payment signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            
            # Update order status
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.status = 'processing'
            order.razorpay_payment_id = payment_id
            order.save()
            
            messages.success(request, "Payment successful, your order is being processed!")
            return redirect('order_confirmation', order_id=order.id)
            
        except:
            messages.error(request, "Payment verification failed.")
            return redirect('payment_failed')
    
    return redirect('index')

@login_required(login_url='login_view')
def payment_failed(request):
    return render(request, 'payment_failed.html')

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import tbl_product

@require_GET
def get_product_details(request, product_id):
    try:
        product = tbl_product.objects.get(id=product_id)
        
        data = {
            'id': product.id,
            'product_name': product.product_name,
            'price': str(product.price),
            'available_shades': product.available_shades or {},
        }
        
        return JsonResponse(data)
    except tbl_product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

from django.shortcuts import render

from django.shortcuts import render, get_object_or_404

@login_required(login_url='login_view')
def my_orders(request):
    user = request.user
    
    # Get the active tab from request parameters (default to 'orders')
    active_tab = request.GET.get('tab', 'orders')
    
    # Get orders
    orders_list = Order.objects.filter(user=user).order_by('-id')
    orders_paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    orders_page = request.GET.get('page')
    orders = orders_paginator.get_page(orders_page)
    
    # Get painter bookings
    painter_bookings_list = PainterBooking.objects.filter(customer=user).order_by('-id')
    painter_bookings_paginator = Paginator(painter_bookings_list, 10)
    painter_bookings_page = request.GET.get('page')
    painter_bookings = painter_bookings_paginator.get_page(painter_bookings_page)
    
    context = {
        'orders': orders,
        'painter_bookings': painter_bookings,
        'active_tab': active_tab
    }
    
    return render(request, 'my_order.html', context)

@login_required(login_url='login_view')
def order_detail(request, order_id):
    """
    View to display details of a specific order
    """
    # Get the specific order for the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    return render(request, 'order_detail_ecom.html', {
        'order': order,
    })

@login_required(login_url='login_view')
def update_booking_status(request, booking_id):
    """
    View for customers to update the status of their painter booking
    Primarily used for marking bookings as completed
    """
    # Get the specific booking for the logged-in user
    booking = get_object_or_404(PainterBooking, id=booking_id, customer=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        booking_notes = request.POST.get('booking_notes')
        
        # Validate status - only allow the customer to mark as completed
        if status == 'completed' and booking.status == 'confirmed':
            booking.status = status
            
            # Add notes if provided
            if booking_notes:
                if booking.notes:
                    booking.notes += f"\n\nCompletion notes (added {datetime.now().strftime('%Y-%m-%d')}): {booking_notes}"
                else:
                    booking.notes = f"Completion notes (added {datetime.now().strftime('%Y-%m-%d')}): {booking_notes}"
                    
            booking.save()
            
            # Update painter status to available now that project is complete
            if booking.painter:
                painter = booking.painter
                painter.current_status = 'available'
                painter.save()
            
            messages.success(request, 'Booking has been marked as completed successfully.')
        else:
            messages.error(request, 'Invalid update request. Only confirmed bookings can be marked as completed.')
        
        # Redirect to the booking detail page
        return redirect('Customer_painter_bookingDetail', booking_id=booking.id)
    
    # If not a POST request, redirect to the booking detail page
    return redirect('Customer_painter_bookingDetail', booking_id=booking.id)

@login_required(login_url='login_view')
def cancel_booking(request, booking_id):
    """
    View for customers to cancel their pending painter booking
    """
    # Get the specific booking for the logged-in user
    booking = get_object_or_404(PainterBooking, id=booking_id, customer=request.user)
    
    if request.method == 'POST':
        # Only allow cancellation of pending bookings
        if booking.status == 'pending':
            # You might want to set a special status or just delete it
            booking.delete()  # Or set a cancelled status if you want to keep records
            
            messages.success(request, 'Booking has been cancelled successfully.')
            return redirect('my_orders')  # Redirect to the orders page
        else:
            messages.error(request, 'Only pending bookings can be cancelled.')
            return redirect('Customer_painter_bookingDetail', booking_id=booking.id)
    
    # If not a POST request, redirect to the booking detail page
    return redirect('Customer_painter_bookingDetail', booking_id=booking.id)


@login_required(login_url='login_view')
def Customer_painter_bookingDetail(request, booking_id):
    """
    View to display details of a specific painter booking
    """
    # Get the specific booking for the logged-in user
    booking = get_object_or_404(PainterBooking, id=booking_id, customer=request.user)
    
    return render(request, 'update_painting_status.html', {
        'booking': booking,
    })

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            # Get the total amount
           # total_amount = 749.00  # Hardcode for testing based on your screenshot
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            # Calculate total amount from cart items
            total_amount = sum(item.subtotal for item in cart_items)
            # Convert to paise (smallest currency unit)
            amount_in_paise = int(total_amount * 100)
            
            print(f"Creating Razorpay order with amount: {amount_in_paise} paise")
            print(f"Using key: {settings.RAZORPAY_KEY_ID}")
            
            # Create Razorpay Order
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1  # Auto-capture payment
            })
            
            print(f"Order created successfully with ID: {razorpay_order['id']}")
            
            # Return order details
            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'currency': 'INR'
            })
            
        except Exception as e:
            import traceback
            print(f"Error creating Razorpay order: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
def verify_payment(request):
    if request.method == 'POST':
        try:
            # Get payment verification data
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify the payment signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            # Verify signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Process the order (save to database)
            process_order(request, payment_method='razorpay', payment_id=payment_id)
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Helper function to process the order (you'll need to implement this based on your model)
def process_order(request, payment_method, payment_id=None):
    # Get cart items
    cart_items = get_cart_items(request.user)
    customer = Customer.objects.filter(userid=request.user).first()
    # Create order
    order = Order.objects.create(
        user=request.user,
        customer=customer,
        payment_method=payment_method,
        payment_id=payment_id,
        total_amount=calculate_total_amount(request),
        # other fields...
    )
    
    # Process painter booking if selected
    if request.POST.get('need_painter') == 'yes':
        painter_id = request.POST.get('painter_id')
        completion_date = request.POST.get('project_completion_date')
        square_feet = request.POST.get('square_feet')
        
        # Create painter booking
        PainterBooking.objects.create(
            order=order,
            painter_id=painter_id,
            expected_completion_date=completion_date,
            area_square_feet=square_feet
        )
    
    # Process field staff commission if applicable
    if request.POST.get('approached_by_staff') == 'yes':
        field_staff_id = request.POST.get('field_staff')
        if field_staff_id:
            # Associate field staff with order
            order.field_staff_id = field_staff_id
            order.save()
    
    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            color=item.color,
            price=item.product.price,
            subtotal=item.subtotal
        )
    
    # Clear the cart
    cart_items.delete()
    
    return order

# Helper functions for calculating totals and getting cart items
def calculate_total_amount(request):
    cart_items = get_cart_items(request.user)
    total = sum(item.subtotal for item in cart_items)
    return total

def get_cart_items(user):
    # Implement based on your model
    return CartItem.objects.filter(user=user)
@login_required
def delivery_details(request, order_id):
    """
    Detailed view of a specific delivery
    """
    order = get_object_or_404(
        Order, 
        id=order_id, 
        field_staff__userid=request.user
    )
    
    if request.method == 'POST':
        # Update delivery status
        new_status = request.POST.get('delivery_status')
        valid_statuses = ['processing', 'shipped', 'delivered', 'cancelled']
        
        if new_status in valid_statuses:
            order.status_delivery = new_status
            
            if new_status == 'delivered':
                order.status = 'completed'
            
            order.save()
            
            messages.success(request, "Delivery status updated successfully!")
            return redirect('delivery_details', order_id=order.id)
    
    context = {
        'order': order,
        'delivery_statuses': Order.STATUS_CHOICES_delivery
    }
    return render(request, 'delivery_manage.html', context)
@login_required
def assigned_order_detail(request, order_id):
    try:
        field_staff = FieldStaff.objects.get(userid=request.user)
        order = get_object_or_404(Order, id=order_id)
        
        # Verify that this order is assigned to the current field staff
        if order.field_staff != field_staff:
            messages.error(request, "You don't have permission to view this order.")
            return redirect('assigned_deliveries')
        
        # Process form submission for status update
        if request.method == 'POST':
            new_status = request.POST.get('status_delivery')
            delivery_notes = request.POST.get('delivery_notes', '')
            
            # Update the order status
            if new_status in dict(Order.STATUS_CHOICES_delivery):
                # Save old status for comparison
                old_status = order.status_delivery
                
                # Update status and delivery notes
                order.status_delivery = new_status
                if delivery_notes:
                    order.delivery_notes = delivery_notes
                
                # Update dates based on status changes
                current_date = now().date()
                
                # If status is changed to shipped
                if old_status != 'shipped' and new_status == 'shipped':
                    order.shipped_date = current_date
                    order.status = 'shipped'  # Update main status to reflect shipping
                
                # If status is changed to delivered
                if old_status != 'delivered' and new_status == 'delivered':
                    order.delivery_date = current_date
                    order.status = 'delivered'  # Update main status to reflect delivery
                
                order.save()
                
                messages.success(request, f"Order status updated to {order.get_status_delivery_display()}")
            else:
                messages.error(request, "Invalid status selected")
            
            return redirect('assigned_order_detail', order_id=order.id)
        
        context = {
            'order': order,
            'field_staff': field_staff
        }
        return render(request, 'assign_delivery.html', context)
    
    except FieldStaff.DoesNotExist:
        messages.error(request, "You are not registered as a field staff.")
        return redirect('index')

import datetime

def update_delivery_prediction(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_date = request.POST.get("delivery_date")

        if new_date:
            order.delivery_date = datetime.datetime.strptime(new_date, "%Y-%m-%d").date()

        # Auto-update delivery_date when status is changed to 'delivered'
        if request.POST.get("status_delivery") == "delivered":
            order.delivery_date = datetime.date.today()

        order.save()
        messages.success(request, "Delivery date updated successfully.")

    return redirect("assigned_order_detail", order_id=order.id)


@login_required
def assigned_deliveries(request):
    try:
        field_staff = FieldStaff.objects.get(userid=request.user)
        
        processing_orders = Order.objects.filter(
            field_staff=field_staff, 
            status_delivery__in=['pending', 'processing', 'shipped']  # Include all non-delivered statuses
        ).order_by('-date')
        
        return render(request, 'assigned_deliveries.html', {'processing_orders': processing_orders})
    
    except FieldStaff.DoesNotExist:
       
        return render(request, 'error.html', {'message': 'You are not authorized to view this page.'})
@login_required
def staff_delivery_dashboard(request):
    try:
        field_staff = FieldStaff.objects.get(userid=request.user)
        orders = Order.objects.filter(field_staff=field_staff).order_by('-created_at')
        pending_orders = orders.filter(status_delivery='pending')
        processing_orders = orders.filter(status_delivery='processing')
        completed_orders = orders.filter(status_delivery='delivered')    
        context = {
            'field_staff': field_staff,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'completed_orders': completed_orders,
            'total_orders': orders.count()
        }
        
        return render(request, 'delivery_manage.html', context)
    
    except FieldStaff.DoesNotExist:
        messages.error(request, "You are not registered as a field staff.")
        return redirect('index')

@login_required
def fieldstaff_delivered_orders(request):
    try:    
        field_staff = FieldStaff.objects.get(userid=request.user)
    except FieldStaff.DoesNotExist:
        
        return render(request, 'error.html', {
            'message': 'You are not registered as a field staff member.'
        })
    delivered_orders = Order.objects.filter(
        field_staff=field_staff,
        status_delivery='delivered'
    ).order_by('-delivery_date')

    total_orders = delivered_orders.count()
    total_amount = delivered_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'delivered_orders': delivered_orders,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'field_staff': field_staff
    }
    
    return render(request, 'delivered_orders.html', context)

@login_required
def add_review(request, product_id):
    """
    Handle the submission of product reviews with image uploads.
    
    This view validates the review form, checks for verified purchases,
    saves the review to the database, and redirects back to the product detail page.
    """
    product = get_object_or_404(tbl_product, id=product_id)
    
    if request.method == 'POST':
        # Use request.FILES to handle uploaded images
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            # Check if user has already reviewed this product
            existing_review = tbl_review.objects.filter(
                user=request.user,
                product=product
            ).exists()
            
            if not existing_review:
                # Save review but don't commit yet
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                
                # Check if user has purchased this product
                # Assuming you have Order and OrderItem models
                verified_purchase = OrderItem.objects.filter(
                    order__user=request.user,
                    order__status='completed',  # or whatever status indicates successful purchase
                    product=product
                ).exists()
                
                review.verified_purchase = verified_purchase
                review.save()
                
                # Update product rating
                update_product_rating(product)
                
                messages.success(request, 'Your review has been submitted successfully.')
            else:
                messages.error(request, 'You have already reviewed this product.')
        else:
            messages.error(request, 'There was an error with your review submission.')
    
    # Redirect back to product detail page
    return redirect('product_detail', product_id=product_id)


def update_product_rating(product):
    """
    Update the product's average rating based on all its reviews
    """
    reviews = tbl_review.objects.filter(product=product)
    
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product.average_rating = round(avg_rating, 1)
        product.total_reviews = reviews.count()
        product.save()
    else:
        product.average_rating = 0
        product.total_reviews = 0
        product.save()


@login_required
@require_POST
def mark_review_helpful(request, review_id):
    """
    Allow users to mark a review as helpful
    """
    review = get_object_or_404(tbl_review, id=review_id)
    
    # Check if user has already marked this review as helpful
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if not created:
        # User is unmarking the review as helpful
        helpful.delete()
        review.helpful_count = max(0, review.helpful_count - 1)
        message = "You've removed your helpful mark from this review."
    else:
        # User is marking the review as helpful
        review.helpful_count += 1
        message = "You've marked this review as helpful."
    
    review.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'helpfulCount': review.helpful_count,
            'message': message
        })
    else:
        messages.success(request, message)
        return HttpResponseRedirect(reverse('product_detail', args=[review.product.id]))


@login_required
def report_review(request, review_id):
    """
    Allow users to report inappropriate reviews
    """
    review = get_object_or_404(tbl_review, id=review_id)
    
    # In a real app, you might want to create a ReportedReview model
    # to track reports, report reasons, etc.
    
    # For now, just show a confirmation message
    messages.success(request, "Thank you for your report. We'll review this content soon.")
    
    return redirect('product_detail', product_id=review.product.id)
def about(request):
    """View for the about page"""
    context = {
        'title': 'About ShadeStore'
        # Add any other context variables you need
    }
    return render(request, 'about.html', context)