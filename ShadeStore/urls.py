"""
URL configuration for ShadeStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from ecom.admin import custom_admin_site
from django.urls import path,include
from django.conf import settings 
from django.conf.urls.static import static   

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('',include('ecom.urls')),
    path('Showroom_staff/',include('Showroom_staff.urls')),
    path('painter/',include('painter.urls',namespace='painter')),
    path('chat/', include('chat.urls', namespace='chat')),
   # path('notifications/', include('notifications.urls', namespace='notifications')),
    path('logout/', include('django.contrib.auth.urls')), 
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
