from django.shortcuts import redirect
from django.urls import resolve
from ecom.models import FieldStaff, ShowroomStaff, Painter

class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view is called
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            
            # Don't redirect if we're on these pages
            excluded_urls = ['login_view', 'logout', 'admin:index', 
                           'fieldstaff_dashboard', 'showroomstaff_dashboard', 
                           'painter_dashboard', 'painter:painter_dashboard']
            
            if current_url in excluded_urls:
                # Let these URLs process normally
                return self.get_response(request)
            
            # Handle redirects for index page or after login
            if current_url == 'index':
                # Check user's role and redirect accordingly
                if ShowroomStaff.objects.filter(userid=request.user).exists():
                    return redirect('showroomstaff_dashboard')
                elif Painter.objects.filter(userid=request.user).exists():
                    return redirect('painter:painter_dashboard')
                elif FieldStaff.objects.filter(userid=request.user).exists():
                    return redirect('fieldstaff_dashboard')
                # Customers can access the index page
        
        # If no redirection happens, continue with the regular flow
        response = self.get_response(request)
        return response