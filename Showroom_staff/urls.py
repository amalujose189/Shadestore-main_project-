from django.urls import path
from . import views


urlpatterns = [
    
    path('',views.showroomdash,name='showroomstaff_dashboard'),
    path('profile/update/', views.update_showroom_staff, name='showroom_staff_profile_update'),
    path('order-details/', views.order_details, name='order_details'), 
    path('invoice/<int:order_id>/', views.order_invoice, name='order_invoice'),
    path('add-product/', views.add_product, name='add_product'),
    path('inventory/',views.inventory,name='inventory'),
    path('inventory/update/<int:product_id>/', views.update_inventory, name='update_inventory'),
    path('inventory/view/<int:product_id>/', views.view_product, name='view_product_details'),
    path('inventory-dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    #path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # Download Report URL
    
    path('download-report/', views.download_report, name='download_report'),
    # URL for generating the invoice (PDF)
    #path('generate-invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'), 
    # New AJAX endpoint for product details
    #path('get_product_details/', views.get_product_details, name='get_product_details'),

]