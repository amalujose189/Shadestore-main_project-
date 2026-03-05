from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('product/<int:product_id>', views.product_detail, name='product_detail'),
    path('category/<int:category_id>', views.category_detail, name='category_detail'),
    path('login', views.login_view, name='login_view'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('fieldstaff', views.fieldstaff_dashboard, name="fieldstaff_dashboard"),
    path('profile/', views.profile_update, name='profile'),
    path('fetch-print-data/', views.fetch_print_data, name='fetch_print_data'),
    path('site-visit/<int:pk>/', views.SiteVisitDetailView.as_view(), name='site_visit_detailView'),
    path('fieldstaff/site-visits/', views.site_visit_list, name='site_visit_list'),
    path('fieldstaff/site-visits/create/', views.create_site_visit, name='create_site_visit'),
    path('fieldstaff/site-visits/<int:pk>/', views.site_visit_detail, name='site_visit_detail'),
    path('fieldstaff/site-visits/<int:pk>/edit/', views.edit_site_visit, name='edit_site_visit'),
    path('fieldstaff/site-visits/<int:pk>/delete/', views.delete_site_visit, name='delete_site_visit'),
    path('fieldstaff/site-visits/download-csv/', views.download_site_visits_csv, name='download_site_visits_csv'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
  #  path('check-customer-address/', views.check_customer_address, name='check_customer_address'),
    path('category/<int:category_id>/', views.filter_by_category, name='filter_by_category'),
    path('api/product/<int:product_id>/', views.get_product_details, name='get_product_details'),
    path('customer/profile/update/', views.customer_profile_update, name='customer_profile_update'),
    path('search/', views.search_products, name='search_products'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
  
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),  # ✅ FIXED
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('delivery/<int:order_id>/', views.delivery_details, name='delivery_details'),
    
    # Staff Delivery Dashboard
    path('staff/delivery-dashboard/', views.staff_delivery_dashboard, name='staff_delivery_dashboard'),
    path('fieldstaff/assigned-deliveries/', views.assigned_deliveries, name='assigned_deliveries'),
    path('assigned_order/<int:order_id>/', views.assigned_order_detail, name='assigned_order_detail'),
    path("update_delivery_prediction/<int:order_id>/", views.update_delivery_prediction, name="update_delivery_prediction"),
    path('fieldstaff/delivered-orders/', views.fieldstaff_delivered_orders, name='fieldstaff_delivered_orders'),

    
    # Review-related URLs
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/helpful/', views.mark_review_helpful, name='mark_review_helpful'),
    path('review/<int:review_id>/report/', views.report_review, name='report_review'),
    path('update-booking-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
     path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/', views.Customer_painter_bookingDetail, name='Customer_painter_bookingDetail'),
]