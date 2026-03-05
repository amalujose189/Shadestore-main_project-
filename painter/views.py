from django.shortcuts import render
from django.shortcuts import render, redirect
# Create your views here.
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PainterUpdateForm, UserUpdateForm
from ecom.models import Customer, Painter,Order,PainterBooking
from django.shortcuts import render

from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404
from ecom.models import Painter, PainterBooking
from django.contrib.auth.decorators import login_required


@login_required
def painterdash(request):
    return render(request,'painter_dashboard.html')
def update_profile(request):
    painter = Painter.objects.get(userid=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        painter_form = PainterUpdateForm(request.POST, instance=painter)
        if user_form.is_valid() and painter_form.is_valid():
            user_form.save()
            painter_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(request.path) 
    else:
        user_form = UserUpdateForm(instance=request.user)
        painter_form = PainterUpdateForm(instance=painter)

    context = {
        'user_form': user_form,
        'painter_form': painter_form,
        'painter': painter,
    }
    return render(request, 'profile_update_painter.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ecom.models import Painter, PainterBooking, Customer

@login_required
def assigned_jobs(request):
    try:
        # Get the painter object
        painter = get_object_or_404(Painter, userid=request.user)
        
        # Get all assigned jobs
        assigned_jobs = PainterBooking.objects.filter(
            painter=painter, 
            status__in=['pending', 'confirmed']
        ).select_related('customer')
        
        # Create a list of job dictionaries with all needed information
        jobs_with_details = []
        
        for job in assigned_jobs:
            # Get customer phone
            phone = "Not available"
            
            # Try to get phone from Customer model
            customer = Customer.objects.filter(userid=job.customer).first()
            if customer and customer.phone:
                phone = customer.phone
            # If not found and job has order with customer, try that
            elif job.order and job.order.customer and job.order.customer.phone:
                phone = job.order.customer.phone
            
            # Add all details to a dictionary
            job_details = {
                'id': job.id,
                'customer_name': job.customer.get_full_name() or job.customer.username,
                'phone': phone,
                'square_feet': job.square_feet,
                'project_completion_date': job.project_completion_date,
                'status': job.get_status_display(),
            }
            
            jobs_with_details.append(job_details)
        
        return render(request, 'job_assigned.html', {
            'jobs': jobs_with_details,
        })

    except Painter.DoesNotExist:
        return render(request, 'error.html', {'message': 'You are not registered as a painter.'})

@login_required
def completed_jobs(request):
    try:
        # Ensure user has a related painter profile
        painter = get_object_or_404(Painter, userid=request.user)
        
        # Fetch completed jobs
        completed_jobs = PainterBooking.objects.filter(painter=painter, status='completed')

        return render(request, 'completedjob.html', {'completed_jobs': completed_jobs})
    
    except Painter.DoesNotExist:
        return render(request, 'error.html', {'message': 'You are not registered as a painter.'})
def painter_booking_detail(request, booking_id):
    booking = get_object_or_404(PainterBooking, id=booking_id)
    
    if request.method == 'POST':
        # Check if the status is being updated
        if 'status' in request.POST:
            booking.status = request.POST.get('status')
            booking.save()
            messages.success(request, f'Booking #{booking.id} status updated successfully.')
            
        # Check if notes are being updated (we'll add a notes field to the model)
        if 'booking_notes' in request.POST:
            booking.notes = request.POST.get('booking_notes')
            booking.save()
            messages.success(request, 'Booking notes updated successfully.')
        
        # Redirect to the same page to avoid form resubmission
        return redirect('painter_booking_detail', booking_id=booking.id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'painter_booking_detail.html', context)
'''def confirmed_and_completed(request):
    """View to display the painter's dashboard with confirmed and completed works."""
    painter = get_object_or_404(Painter, userid=request.user)

    completed_works = PainterBooking.objects.filter(painter=painter, status="completed").select_related("customer")
    confirmed_works = PainterBooking.objects.filter(painter=painter, status="confirmed").select_related("customer")
    total_completed_works = completed_works.count()
    total_square_footage = sum(job.square_feet for job in completed_works)

    total_confirmed_works = confirmed_works.count()
    pending_square_footage = sum(job.square_feet for job in confirmed_works)

    context = {
        "painter": painter,
        "completed_works": completed_works,
        "confirmed_works": confirmed_works,
        "total_completed_works": total_completed_works,
        "total_square_footage": total_square_footage,
        "total_confirmed_works": total_confirmed_works,
        "pending_square_footage": pending_square_footage,
    }

    return render(request, "completed_and_confirmed.html", context)'''
@login_required
def confirmed_and_completed(request):
    """View to display the painter's dashboard with confirmed and completed works."""
    painter = get_object_or_404(Painter, userid=request.user)

    # Get completed and confirmed works without select_related (we'll handle phone numbers differently)
    completed_works = PainterBooking.objects.filter(painter=painter, status="completed")
    confirmed_works = PainterBooking.objects.filter(painter=painter, status="confirmed")
    
    # Prefetch related customer data more efficiently
    customer_ids = list(completed_works.values_list('customer', flat=True)) + \
                 list(confirmed_works.values_list('customer', flat=True))
    customers = Customer.objects.filter(userid__in=customer_ids)
    customer_dict = {c.userid_id: c for c in customers}

    # Annotate the jobs with phone numbers
    for job in completed_works:
        job.customer_phone = customer_dict.get(job.customer_id, Customer()).phone or "Not Available"
    
    for job in confirmed_works:
        job.customer_phone = customer_dict.get(job.customer_id, Customer()).phone or "Not Available"

    # Calculate statistics
    total_completed_works = completed_works.count()
    total_square_footage = sum(job.square_feet for job in completed_works if job.square_feet)
    
    total_confirmed_works = confirmed_works.count()
    pending_square_footage = sum(job.square_feet for job in confirmed_works if job.square_feet)

    context = {
        "painter": painter,
        "completed_works": completed_works,
        "confirmed_works": confirmed_works,
        "total_completed_works": total_completed_works,
        "total_square_footage": total_square_footage or 0,
        "total_confirmed_works": total_confirmed_works,
        "pending_square_footage": pending_square_footage or 0,
    }

    return render(request, "completed_and_confirmed.html", context)