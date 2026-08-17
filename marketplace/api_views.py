import stripe
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .payments import create_checkout_session_for_booking

from .models import (
    Profile, Category, Item, ItemImage, Booking, Review,
    ServiceCategory, Service, ServiceBooking, ServiceReview, KYCVerification
)
from .serializers import (
    ProfileSerializer, CategorySerializer, ItemSerializer, ItemImageSerializer,
    BookingSerializer, ReviewSerializer, ServiceCategorySerializer,
    ServiceSerializer, ServiceBookingSerializer, ServiceReviewSerializer,
    KYCVerificationSerializer, RegisterSerializer
)


class RegisterView(APIView):
    """Create a new user account and return an auth token"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'user': ProfileSerializer(user.profile).data},
            status=status.HTTP_201_CREATED,
        )

# Import AI services with fallback
try:
    from .ai_services import recommendation_engine, smart_pricing_engine
    AI_AVAILABLE = True
except ImportError:
    try:
        from .simple_ai import simple_recommendation_engine, simple_smart_pricing_engine
        recommendation_engine = simple_recommendation_engine
        smart_pricing_engine = simple_smart_pricing_engine
        AI_AVAILABLE = True
    except ImportError:
        AI_AVAILABLE = False
        recommendation_engine = None
        smart_pricing_engine = None


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'location']
    ordering_fields = ['created_at', 'membership_tier']
    
    def get_queryset(self):
        # Users can only see their own profile or all profiles if admin
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's profile"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories (read-only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for rental items"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'availability_status', 'condition', 'owner']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'daily_price', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Item.objects.select_related('owner', 'category').prefetch_related('images', 'reviews')
        
        # Filter by availability if requested
        availability = self.request.query_params.get('available', None)
        if availability == 'true':
            queryset = queryset.filter(availability_status='available')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(daily_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(daily_price__lte=max_price)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get AI-powered recommendations"""
        if AI_AVAILABLE and recommendation_engine:
            if request.user.is_authenticated:
                items = recommendation_engine.get_personalized_recommendations(request.user, limit=10)
            else:
                items = recommendation_engine.get_popular_items(limit=10)
        else:
            # Fallback to popular items
            items = Item.objects.filter(availability_status='available').order_by('-created_at')[:10]
        
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pricing_suggestion(self, request, pk=None):
        """Get AI-powered pricing suggestion"""
        item = self.get_object()
        if AI_AVAILABLE and smart_pricing_engine:
            suggestion = smart_pricing_engine.suggest_price(item)
            return Response({'suggested_price': suggestion})
        return Response({'suggested_price': item.daily_price})


class ItemImageViewSet(viewsets.ModelViewSet):
    """ViewSet for item images"""
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        item_id = self.request.query_params.get('item', None)
        if item_id:
            return ItemImage.objects.filter(item_id=item_id)
        return ItemImage.objects.all()

    def perform_create(self, serializer):
        item = serializer.validated_data['item']
        if item.owner != self.request.user.profile:
            raise PermissionDenied('Only the item owner can add images.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.item.owner != self.request.user.profile:
            raise PermissionDenied('Only the item owner can remove images.')
        instance.delete()


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for bookings"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'item', 'renter']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see their own bookings or bookings for their items
        if self.request.user.is_staff:
            return Booking.objects.all()
        
        user_profile = self.request.user.profile
        return Booking.objects.filter(
            Q(renter=user_profile) | Q(item__owner=user_profile)
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking"""
        booking = self.get_object()
        if booking.item.owner != request.user.profile:
            return Response(
                {'error': 'Only the item owner can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        booking.status = 'confirmed'
        booking.save()

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=booking.renter.user,
            notification_type='booking_confirmed',
            title='Booking Confirmed',
            message=f'Your booking for "{booking.item.title}" has been confirmed.',
            related_booking=booking,
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        if booking.renter != request.user.profile and booking.item.owner != request.user.profile:
            return Response(
                {'error': 'Only the renter or owner can cancel bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        booking.status = 'cancelled'
        booking.save()

        from notifications.services import EmailNotificationService
        cancelling_user = request.user.profile
        notify_user = booking.item.owner.user if cancelling_user == booking.renter else booking.renter.user
        EmailNotificationService.send_notification(
            user=notify_user,
            notification_type='booking_cancelled',
            title='Booking Cancelled',
            message=f'The booking for "{booking.item.title}" has been cancelled.',
            related_booking=booking,
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a booking as completed (owner only)"""
        booking = self.get_object()
        if booking.item.owner != request.user.profile:
            return Response(
                {'error': 'Only the item owner can mark a booking as completed'},
                status=status.HTTP_403_FORBIDDEN
            )
        if booking.status not in ['confirmed', 'active']:
            return Response(
                {'error': 'Only confirmed or active bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'completed'
        booking.save()

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=booking.renter.user,
            notification_type='system_message',
            title='Rental Completed',
            message=f'Your rental of "{booking.item.title}" has been marked as completed. Leave a review!',
            related_booking=booking,
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_checkout_session(self, request, pk=None):
        """Create a Stripe Checkout session for paying this booking"""
        booking = self.get_object()
        if booking.renter != request.user.profile:
            return Response(
                {'error': 'Only the renter can pay for this booking'},
                status=status.HTTP_403_FORBIDDEN
            )
        if booking.payment_status == 'paid':
            return Response(
                {'error': 'Booking is already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if booking.status in ['cancelled', 'completed']:
            return Response(
                {'error': f'Cannot pay for a {booking.status} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            session = create_checkout_session_for_booking(booking)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({'checkout_url': session.url, 'session_id': session.id})


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'booking', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service categories"""
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'available', 'provider']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'hourly_rate', 'average_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Service.objects.select_related('provider', 'category')
        
        # Filter by availability
        available = self.request.query_params.get('available', None)
        if available == 'true':
            queryset = queryset.filter(available=True)
        
        return queryset


class ServiceBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for service bookings"""
    queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'customer']
    ordering_fields = ['created_at', 'start_time']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see their own service bookings or bookings for their services
        if self.request.user.is_staff:
            return ServiceBooking.objects.all()
        
        user_profile = self.request.user.profile
        return ServiceBooking.objects.filter(
            Q(customer=user_profile) | Q(service__provider=user_profile)
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a service booking as completed (provider only)"""
        booking = self.get_object()
        if booking.service.provider != request.user.profile:
            return Response(
                {'error': 'Only the service provider can mark a booking as completed'},
                status=status.HTTP_403_FORBIDDEN
            )
        if booking.status not in ['confirmed', 'in_progress']:
            return Response(
                {'error': 'Only confirmed or in-progress bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'completed'
        booking.save()

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=booking.customer.user,
            notification_type='system_message',
            title='Service Completed',
            message=f'Your booking for "{booking.service.title}" has been marked as completed. Leave a review!',
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ServiceReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for service reviews"""
    queryset = ServiceReview.objects.all()
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'booking', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']


class KYCVerificationViewSet(viewsets.ModelViewSet):
    """ViewSet for KYC verification"""
    queryset = KYCVerification.objects.all()
    serializer_class = KYCVerificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own KYC verification
        if self.request.user.is_staff:
            return KYCVerification.objects.all()
        return KYCVerification.objects.filter(profile__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_status(self, request):
        """Get current user's KYC status"""
        try:
            kyc = KYCVerification.objects.get(profile__user=request.user)
            serializer = self.get_serializer(kyc)
            return Response(serializer.data)
        except KYCVerification.DoesNotExist:
            return Response({'status': 'not_submitted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a KYC submission (staff only)"""
        if not request.user.is_staff:
            return Response({'error': 'Only staff can review KYC submissions'}, status=status.HTTP_403_FORBIDDEN)
        kyc = self.get_object()
        kyc.status = 'approved'
        kyc.verified_at = timezone.now()
        kyc.verified_by = request.user
        kyc.rejection_reason = ''
        kyc.save()

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=kyc.profile.user,
            notification_type='system_message',
            title='Identity Verified',
            message='Your identity verification has been approved.',
        )

        serializer = self.get_serializer(kyc)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a KYC submission (staff only)"""
        if not request.user.is_staff:
            return Response({'error': 'Only staff can review KYC submissions'}, status=status.HTTP_403_FORBIDDEN)
        reason = request.data.get('rejection_reason', '').strip()
        if not reason:
            return Response({'error': 'rejection_reason is required'}, status=status.HTTP_400_BAD_REQUEST)
        kyc = self.get_object()
        kyc.status = 'rejected'
        kyc.verified_at = timezone.now()
        kyc.verified_by = request.user
        kyc.rejection_reason = reason
        kyc.save()

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=kyc.profile.user,
            notification_type='system_message',
            title='Identity Verification Rejected',
            message=f'Your identity verification was rejected: {reason}',
        )

        serializer = self.get_serializer(kyc)
        return Response(serializer.data)
