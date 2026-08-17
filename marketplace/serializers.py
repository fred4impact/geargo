from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    Profile, Category, Item, ItemImage, Booking, Review,
    ServiceCategory, Service, ServiceBooking, ServiceReview, KYCVerification
)


class RegisterSerializer(serializers.Serializer):
    """Serializer for account registration (username is set to the email)"""
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        validate_password(attrs['password1'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password1'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.profile.phone = validated_data.get('phone', '')
        user.profile.location = validated_data.get('location', '')
        user.profile.is_renter = True
        user.profile.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id', 'username', 'is_staff']


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer with nested user"""
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'bio', 'phone', 'location', 'membership_tier',
            'is_owner', 'is_renter', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at']
        read_only_fields = ['id', 'created_at']


class ItemImageSerializer(serializers.ModelSerializer):
    """Item image serializer"""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    optimized_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemImage
        fields = ['id', 'item', 'image', 'image_url', 'thumbnail_url', 'optimized_url', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                # Return relative URL that works through nginx proxy
                return obj.image.url
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                # Return relative URL that works through nginx proxy
                return obj.thumbnail.url
            return obj.thumbnail.url
        return None
    
    def get_optimized_url(self, obj):
        if obj.optimized_image:
            request = self.context.get('request')
            if request:
                # Return relative URL that works through nginx proxy
                return obj.optimized_image.url
            return obj.optimized_image.url
        return None


class ItemSerializer(serializers.ModelSerializer):
    """Item serializer with nested relationships"""
    owner = ProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = ItemImageSerializer(many=True, read_only=True)
    is_available = serializers.ReadOnlyField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = [
            'id', 'owner', 'category', 'category_id', 'title', 'description',
            'daily_price', 'condition', 'availability_status', 'location',
            'is_available', 'images', 'average_rating', 'total_reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()
    
    def create(self, validated_data):
        # Set owner from request user
        validated_data['owner'] = self.context['request'].user.profile
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    reviewer = ProfileSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True,
        required=False
    )
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'item', 'item_id', 'booking', 'booking_id',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'item', 'booking', 'created_at']

    def validate_booking_id(self, booking):
        profile = self.context['request'].user.profile
        if booking.renter != profile:
            raise serializers.ValidationError('You can only review your own bookings.')
        if booking.status != 'completed':
            raise serializers.ValidationError('You can only review completed bookings.')
        if Review.objects.filter(reviewer=profile, booking=booking).exists():
            raise serializers.ValidationError('You have already reviewed this booking.')
        return booking

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user.profile
        validated_data['item'] = validated_data['booking'].item
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """Booking serializer"""
    renter = ProfileSerializer(read_only=True)
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )
    duration_days = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'renter', 'item', 'item_id', 'start_date', 'end_date',
            'total_amount', 'status', 'payment_status', 'payment_date',
            'payment_transaction_id', 'stripe_checkout_session_id',
            'duration_days', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'renter', 'total_amount', 'payment_transaction_id',
            'stripe_checkout_session_id', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['renter'] = self.context['request'].user.profile
        # Calculate total amount
        item = validated_data['item']
        days = (validated_data['end_date'] - validated_data['start_date']).days
        validated_data['total_amount'] = item.daily_price * days
        booking = super().create(validated_data)

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_booking_confirmation(booking)

        return booking


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Service category serializer"""
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon', 'created_at']
        read_only_fields = ['id', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    """Service serializer"""
    provider = ProfileSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        source='category',
        write_only=True
    )
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'provider', 'category', 'category_id', 'title', 'description',
            'hourly_rate', 'available', 'location', 'experience_years',
            'certifications', 'average_rating', 'total_reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['provider'] = self.context['request'].user.profile
        return super().create(validated_data)


class ServiceBookingSerializer(serializers.ModelSerializer):
    """Service booking serializer"""
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )
    customer = ProfileSerializer(read_only=True)
    
    class Meta:
        model = ServiceBooking
        fields = [
            'id', 'service', 'service_id', 'customer', 'start_time', 'end_time',
            'total_hours', 'total_cost', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'total_hours', 'total_cost', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user.profile
        booking = super().create(validated_data)

        from notifications.services import EmailNotificationService
        EmailNotificationService.send_notification(
            user=booking.service.provider.user,
            notification_type='booking_created',
            title='New Service Booking',
            message=f'You have a new booking request for "{booking.service.title}".',
        )

        return booking


class ServiceReviewSerializer(serializers.ModelSerializer):
    """Service review serializer"""
    service = ServiceSerializer(read_only=True)
    customer = ProfileSerializer(read_only=True)
    booking = ServiceBookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceBooking.objects.all(),
        source='booking',
        write_only=True
    )
    
    class Meta:
        model = ServiceReview
        fields = [
            'id', 'service', 'customer', 'booking', 'booking_id',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'service', 'customer', 'booking', 'created_at']

    def validate_booking_id(self, booking):
        profile = self.context['request'].user.profile
        if booking.customer != profile:
            raise serializers.ValidationError('You can only review your own bookings.')
        if booking.status != 'completed':
            raise serializers.ValidationError('You can only review completed bookings.')
        if ServiceReview.objects.filter(customer=profile, booking=booking).exists():
            raise serializers.ValidationError('You have already reviewed this booking.')
        return booking

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user.profile
        validated_data['service'] = validated_data['booking'].service
        return super().create(validated_data)


class KYCVerificationSerializer(serializers.ModelSerializer):
    """KYC verification serializer"""
    profile = ProfileSerializer(read_only=True)
    id_document_url = serializers.SerializerMethodField()
    is_approved = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_rejected = serializers.ReadOnlyField()
    
    class Meta:
        model = KYCVerification
        fields = [
            'id', 'profile', 'legal_name', 'id_type', 'id_number',
            'id_document', 'id_document_url', 'status', 'verified_at',
            'rejection_reason', 'is_approved', 'is_pending', 'is_rejected',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'profile', 'status', 'verified_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
    
    def get_id_document_url(self, obj):
        if obj.id_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.id_document.url)
            return obj.id_document.url
        return None
    
    def create(self, validated_data):
        validated_data['profile'] = self.context['request'].user.profile
        return super().create(validated_data)
