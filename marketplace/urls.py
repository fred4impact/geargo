from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Item views
    path('items/', views.item_list, name='item_list'),
    path('items/<uuid:item_id>/', views.item_detail, name='item_detail'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<uuid:item_id>/edit/', views.item_edit, name='item_edit'),
    
    # Booking views
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<uuid:booking_id>/payment/', views.booking_payment, name='booking_payment'),
    path('items/<uuid:item_id>/book/', views.booking_create, name='booking_create'),
    
    # Profile views
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Category views
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Service URLs
    path('services/', views.service_list, name='service_list'),
    path('services/<uuid:service_id>/', views.service_detail, name='service_detail'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<uuid:service_id>/edit/', views.service_edit, name='service_edit'),
    path('services/<uuid:service_id>/book/', views.service_booking_create, name='service_booking_create'),
    path('service-bookings/', views.service_booking_list, name='service_booking_list'),
    path('service-bookings/<uuid:booking_id>/', views.service_booking_detail, name='service_booking_detail'),
    path('service-bookings/<uuid:booking_id>/review/', views.service_review_create, name='service_review_create'),
    
    # KYC Verification
    path('kyc/submit/', views.kyc_submit, name='kyc_submit'),
    path('kyc/status/', views.kyc_status, name='kyc_status'),
]
