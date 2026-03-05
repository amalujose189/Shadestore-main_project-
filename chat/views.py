from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.contrib.auth.models import User

from ShadeStore import settings
from .models import ChatRoom, Message
from ecom.models import Customer, FieldStaff, ShowroomStaff, Painter, Order, PainterBooking
from .forms import GroupChatForm, MessageForm
from django.utils import timezone

def get_user_type(user):
    """Determine user type based on related profiles"""
    # Check if user is a Customer
    if Customer.objects.filter(userid=user).exists():
        return 'customer'
    # Check if user is a FieldStaff 
    elif FieldStaff.objects.filter(userid=user).exists():
        return 'fieldstaff'
    # Check if user is a ShowroomStaff
    elif ShowroomStaff.objects.filter(userid=user).exists():
        return 'showroomstaff'
    # Check if user is a Painter
    elif Painter.objects.filter(userid=user).exists():
        return 'painter'
    # Check if user is admin (only superuser counts as admin)
    elif user.is_superuser:
        return 'admin'
    return 'unknown'

@login_required
def dashboard(request):
    """Main chat dashboard showing all chat rooms for the user"""
    user = request.user
    chat_rooms = ChatRoom.objects.filter(participants=user).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')
    
    rooms_with_details = []
    for room in chat_rooms:
        # Get the other participant(s)
        other_participants = room.participants.exclude(id=user.id)
        
        # Get the last message
        last_message = room.messages.order_by('-timestamp').first()
        
        # Count unread messages
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()
        
        rooms_with_details.append({
            'room': room,
            'participants': other_participants,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    context = {
        'rooms': rooms_with_details,
        'user_type': get_user_type(user),
    }
    return render(request, 'chat/dashboard.html', context)

def available_users(request):
    """Show users available for chatting based on user type"""
    user = request.user
    user_type = get_user_type(user)
    available_users = []
    
    if user_type == 'customer':
        # Customers can chat with admins and their assigned painters/field staff
        # Only superusers are considered admins
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get painters assigned to this customer through bookings
        customer_obj = Customer.objects.get(userid=user)
        painter_users = User.objects.filter(
            id__in=Painter.objects.filter(
                id__in=PainterBooking.objects.filter(customer=user).values_list('painter', flat=True)
            ).values_list('userid', flat=True)
        ).distinct()
        
        # Get field staff assigned to this customer through orders
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.filter(
                id__in=Order.objects.filter(user=user).values_list('field_staff', flat=True)
            ).values_list('userid', flat=True)
        ).distinct()
        
        available_users = [(u, 'admin') for u in admin_users] + \
                          [(u, 'painter') for u in painter_users] + \
                          [(u, 'fieldstaff') for u in field_staff_users]
    
    elif user_type == 'painter':
        # Painters can chat with their customers and admin
        painter = Painter.objects.get(userid=user)
        
        # Get customers from painter bookings
        customer_users = User.objects.filter(
            id__in=PainterBooking.objects.filter(painter=painter).values_list('customer', flat=True)
        ).distinct()
        
        # Only superusers are considered admins
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        available_users = [(u, 'customer') for u in customer_users] + \
                          [(u, 'admin') for u in admin_users]
    
    elif user_type == 'fieldstaff':
        # Field staff can chat with assigned customers and admin
        field_staff = FieldStaff.objects.get(userid=user)
        
        # Get customers associated with this field staff through orders
        # First, get all orders assigned to this field staff
        orders_assigned = Order.objects.filter(field_staff=field_staff)
        
        # Then, get all customer users from these orders - handle both direct user and customer relationship
        customer_users = User.objects.filter(
            Q(id__in=orders_assigned.values_list('user', flat=True)) |
            Q(id__in=Customer.objects.filter(id__in=orders_assigned.values_list('customer', flat=True)).values_list('userid', flat=True))
        ).distinct()
        
        # Get ONLY actual admin users (with is_superuser=True)
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get showroom staff for communication
        showroom_staff_users = User.objects.filter(
            id__in=ShowroomStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        available_users = [(u, 'customer') for u in customer_users] + \
                          [(u, 'admin') for u in admin_users] + \
                          [(u, 'showroomstaff') for u in showroom_staff_users]
    
    elif user_type == 'showroomstaff':
        # Showroom staff can chat with field staff, customers, and admin
        # Only superusers are considered admins
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get all field staff users for communication
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        # For showroom staff, they can see all customers
        customer_users = User.objects.filter(
            id__in=Customer.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        available_users = [(u, 'admin') for u in admin_users] + \
                          [(u, 'fieldstaff') for u in field_staff_users] + \
                          [(u, 'customer') for u in customer_users]
    
    elif user_type == 'admin':
        # Admin can chat with all customers, painters, field staff, and showroom staff
        customer_users = User.objects.filter(
            id__in=Customer.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        painter_users = User.objects.filter(
            id__in=Painter.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        showroom_staff_users = User.objects.filter(
            id__in=ShowroomStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        available_users = [(u, 'customer') for u in customer_users] + \
                          [(u, 'painter') for u in painter_users] + \
                          [(u, 'fieldstaff') for u in field_staff_users] + \
                          [(u, 'showroomstaff') for u in showroom_staff_users]
    
    # Remove duplicates and self (keeping the type information)
    filtered_available_users = []
    seen_ids = set()
    for u, u_type in available_users:
        if u.id not in seen_ids and u != user:
            seen_ids.add(u.id)
            filtered_available_users.append((u, u_type))
    
    # Provide the users list with type information
    users_list = []
    for u, u_type in filtered_available_users:
        users_list.append({
            'user': u,
            'name': u.get_full_name() or u.username,
            'user_type': u_type
        })
    
    context = {
        'available_users': users_list,
        'user_type': user_type  # Add user type to context for template usage
    }
    
    return render(request, 'chat/available_chat.html', context)
@login_required
def create_chat_room(request, user_id):
    """Create a new chat room or get existing one between current user and selected user"""
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    # Check if a chat room already exists between these users
    existing_rooms = ChatRoom.objects.filter(participants=current_user).filter(participants=other_user)
    
    if existing_rooms.exists():
        # Use the first room if multiple exist
        chat_room = existing_rooms.first()
    else:
        # Create a new room
        other_user_type = get_user_type(other_user)
        current_user_type = get_user_type(current_user)
        
        room_name = f"Chat: {current_user.username} ({current_user_type}) - {other_user.username} ({other_user_type})"
        chat_room = ChatRoom.objects.create(name=room_name)
        chat_room.participants.add(current_user, other_user)
        
        # Create a welcome message
        Message.objects.create(
            chat_room=chat_room,
            sender=current_user,
            content=f"Chat started with {other_user.get_full_name() or other_user.username}",
            is_read=False
        )
    
    return redirect('chat:chat_room', room_id=chat_room.id)
@login_required
def chat_room(request, room_id):
    """Display and process a specific chat room"""
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    messages = chat_room.messages.all().order_by('timestamp')
    other_participants = chat_room.participants.exclude(id=request.user.id)
    
    # Mark messages as read
    chat_room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_room = chat_room
            message.sender = request.user
            
            # Determine attachment type
            if 'attachment_file' in request.FILES and request.FILES['attachment_file']:
                message.attachment_type = 'file'
                message.attachment_file = request.FILES['attachment_file']
            elif 'attachment_image' in request.FILES and request.FILES['attachment_image']:
                message.attachment_type = 'image'
                message.attachment_image = request.FILES['attachment_image']
            else:
                message.attachment_type = 'none'
            
            message.save()
            return redirect('chat:chat_room', room_id=room_id)
        else:
            print("Form errors:", form.errors)
    else:
        form = MessageForm()
    
    context = {
        'chat_room': chat_room,
        'messages': messages,
        'other_participants': other_participants,
        'form': form,
        'user_type': get_user_type(request.user),
        'is_group': chat_room.is_group,
        'is_group_admin': chat_room.is_group and chat_room.group_admin == request.user
    }
    
    return render(request, 'chat/chat_room.html', context)
@login_required
def get_unread_count(request):
    """API endpoint to get unread message count for current user"""
    unread_count = Message.objects.filter(
        chat_room__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_as_read(request, room_id):
    """Mark all messages in a room as read"""
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        chat_room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'POST request required'})
@login_required
def delete_chat_room(request, room_id):
    """Delete a chat room and all its messages"""
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # Check if the user is a participant in this room
        if request.user in chat_room.participants.all():
            # Delete all messages in the chat room
            chat_room.messages.all().delete()
            # Remove the user from participants
            chat_room.participants.remove(request.user)
            
            # If no participants left, delete the room
            if chat_room.participants.count() == 0:
                chat_room.delete()
            
            return redirect('chat:dashboard')
        else:
            # User is not a participant in this chat room
            return HttpResponseForbidden("You don't have permission to delete this chat room.")
    except ChatRoom.DoesNotExist:
        # Chat room not found
        return HttpResponseNotFound("Chat room not found.")
    
@login_required
def forward_message(request, message_id):
    """Forward a message to a different chat room"""
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        target_room_id = request.POST.get('target_room_id')
        target_room = get_object_or_404(ChatRoom, id=target_room_id, participants=request.user)
        
        # Create new message as a forward
        new_message = Message.objects.create(
            chat_room=target_room,
            sender=request.user,
            content=original_message.content,
            is_read=False,
            is_forwarded=True,
            original_message=original_message,
            attachment_type=original_message.attachment_type,
            attachment_file=original_message.attachment_file,
            attachment_image=original_message.attachment_image,
            location_lat=original_message.location_lat,
            location_lng=original_message.location_lng,
            location_name=original_message.location_name
        )
        
        return redirect('chat:chat_room', room_id=target_room.id)
    
    # Get available rooms for forwarding
    available_rooms = ChatRoom.objects.filter(participants=request.user).exclude(id=original_message.chat_room.id)
    
    context = {
        'message': original_message,
        'available_rooms': available_rooms
    }
    
    return render(request, 'chat/forward_message.html', context)

@login_required
def create_group(request):
    """Create a new group chat"""
    user = request.user
    user_type = get_user_type(user)
    
    # Initialize eligible_users list
    eligible_users = []
    
    # Determine eligible users based on user type
    if user_type == 'customer':
        # Get admin users
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get painters assigned to this customer
        customer_obj = Customer.objects.get(userid=user)
        painter_users = User.objects.filter(
            id__in=Painter.objects.filter(
                id__in=PainterBooking.objects.filter(customer=customer_obj).values_list('painter', flat=True)
            ).values_list('userid', flat=True)
        ).distinct()
        
        # Get field staff assigned to this customer
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.filter(
                id__in=Order.objects.filter(user=user).values_list('field_staff', flat=True)
            ).values_list('userid', flat=True)
        ).distinct()
        
        eligible_users = list(admin_users) + list(painter_users) + list(field_staff_users)
    
    elif user_type == 'painter':
        # Get admin users
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get customers from painter bookings
        painter = Painter.objects.get(userid=user)
        customer_users = User.objects.filter(
            id__in=Customer.objects.filter(
                id__in=PainterBooking.objects.filter(painter=painter).values_list('customer', flat=True)
            ).values_list('userid', flat=True)
        ).distinct()
        
        eligible_users = list(admin_users) + list(customer_users)
    
    elif user_type == 'fieldstaff':
        # Get admin users
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get customers associated with this field staff
        field_staff = FieldStaff.objects.get(userid=user)
        orders_assigned = Order.objects.filter(field_staff=field_staff)
        customer_users = User.objects.filter(
            Q(id__in=orders_assigned.values_list('user', flat=True)) |
            Q(id__in=Customer.objects.filter(id__in=orders_assigned.values_list('customer', flat=True)).values_list('userid', flat=True))
        ).distinct()
        
        # Get showroom staff
        showroom_staff_users = User.objects.filter(
            id__in=ShowroomStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        eligible_users = list(admin_users) + list(customer_users) + list(showroom_staff_users)
    
    elif user_type == 'showroomstaff':
        # Get admin users
        admin_users = User.objects.filter(is_superuser=True).distinct()
        
        # Get field staff
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        # Get all customers
        customer_users = User.objects.filter(
            id__in=Customer.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        eligible_users = list(admin_users) + list(field_staff_users) + list(customer_users)
    
    elif user_type == 'admin':
        # Admin can chat with everyone
        customer_users = User.objects.filter(
            id__in=Customer.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        painter_users = User.objects.filter(
            id__in=Painter.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        field_staff_users = User.objects.filter(
            id__in=FieldStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        showroom_staff_users = User.objects.filter(
            id__in=ShowroomStaff.objects.all().values_list('userid', flat=True)
        ).distinct()
        
        eligible_users = list(customer_users) + list(painter_users) + list(field_staff_users) + list(showroom_staff_users)
    
    if request.method == 'POST':
        form = GroupChatForm(request.POST)
        if form.is_valid():
            group_chat = form.save(commit=False)
            group_chat.is_group = True
            group_chat.group_admin = request.user
            group_chat.save()
            
            # Add participants including the current user
            participants = form.cleaned_data['participants']
            group_chat.participants.add(*participants)
            group_chat.participants.add(request.user)
            
            # Create welcome message
            Message.objects.create(
                chat_room=group_chat,
                sender=request.user,
                content=f"Group {group_chat.name} created",
                is_read=False
            )
            
            return redirect('chat:chat_room', room_id=group_chat.id)
    else:
        form = GroupChatForm()
        # Filter out the current user and use only eligible users
        # Make sure to exclude the current user
        eligible_user_ids = [u.id for u in eligible_users]
        form.fields['participants'].queryset = User.objects.filter(id__in=eligible_user_ids).exclude(id=user.id)
    
    context = {
        'form': form,
        'user_type': user_type
    }
    
    return render(request, 'chat/create_group.html', context)
@login_required
def manage_group(request, room_id):
    """Manage a group chat (add/remove members)"""
    chat_room = get_object_or_404(ChatRoom, id=room_id, is_group=True, group_admin=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            chat_room.participants.add(user)
            Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=f"{user.get_full_name() or user.username} added to the group",
                is_read=False
            )
        
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            chat_room.participants.remove(user)
            Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=f"{user.get_full_name() or user.username} removed from the group",
                is_read=False
            )
        
        return redirect('chat:manage_group', room_id=room_id)
    
    # Get current participants
    participants = chat_room.participants.exclude(id=request.user.id)
    
    # Get eligible users to add
    user_type = get_user_type(request.user)
    # Logic to determine eligible users based on user type (similar to available_users)
    # ...
    eligible_users = User.objects.filter(id__in=[u.id for u, _ in available_users]).exclude(
        id__in=chat_room.participants.all().values_list('id', flat=True)
    )
    
    context = {
        'chat_room': chat_room,
        'participants': participants,
        'eligible_users': eligible_users
    }
    
    return render(request, 'chat/manage_group.html', context)