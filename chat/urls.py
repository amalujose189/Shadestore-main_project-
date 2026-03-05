from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.available_users, name='available_users'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('room/<int:room_id>/delete/', views.delete_chat_room, name='delete_chat_room'),
    path('create/<int:user_id>/', views.create_chat_room, name='create_chat_room'),
    path('get_unread_count/', views.get_unread_count, name='get_unread_count'),
    path('mark_as_read/<int:room_id>/', views.mark_as_read, name='mark_as_read'),
    path('forward-message/<int:message_id>/', views.forward_message, name='forward_message'),
    path('create-group/', views.create_group, name='create_group'),
    path('manage-group/<int:room_id>/', views.manage_group, name='manage_group'),
   
]