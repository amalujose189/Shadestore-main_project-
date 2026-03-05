from django.urls import path
from . import views
app_name = 'painter'

urlpatterns = [
    
    path('',views.painterdash,name='painter_dashboard'),
    path('profile/update/', views.update_profile, name='painter_profile_update'),
    path('assigned-jobs/', views.assigned_jobs, name='assigned_jobs'),
    path('completed-jobs/', views.completed_jobs, name='completed_jobs'),
    path('painter-booking/<int:booking_id>/', views.painter_booking_detail, name='painter_booking_detail'),
    path("painter/completed-confirmed/", views.confirmed_and_completed, name="confirmed_and_completed"),
    
]