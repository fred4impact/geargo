from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import (
    ProfileViewSet, CategoryViewSet, ItemViewSet, ItemImageViewSet,
    BookingViewSet, ReviewViewSet, ServiceCategoryViewSet, ServiceViewSet,
    ServiceBookingViewSet, ServiceReviewViewSet, KYCVerificationViewSet,
    RegisterView
)
from .payments import stripe_webhook

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'item-images', ItemImageViewSet, basename='itemimage')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-bookings', ServiceBookingViewSet, basename='servicebooking')
router.register(r'service-reviews', ServiceReviewViewSet, basename='servicereview')
router.register(r'kyc', KYCVerificationViewSet, basename='kyc')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('payments/webhook/', stripe_webhook, name='stripe-webhook'),
]
