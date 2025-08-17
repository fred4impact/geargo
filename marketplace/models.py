from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Profile(models.Model):
    """Extended user profile for GearGo marketplace"""
    MEMBERSHIP_CHOICES = [
        ('casual', 'Casual'),
        ('frequent', 'Frequent'),
        ('premium', 'Premium'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    membership_tier = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='casual')
    is_owner = models.BooleanField(default=False)
    is_renter = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.membership_tier}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class Category(models.Model):
    """Categories for rental items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For frontend icons
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Item(models.Model):
    """Rental items"""
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('unavailable', 'Unavailable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='owned_items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    daily_price = models.DecimalField(max_digits=8, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.owner.user.email}"
    
    @property
    def is_available(self):
        return self.availability_status == 'available'


class ItemImage(models.Model):
    """Images for rental items with optimized versions"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/')
    optimized_image = models.ImageField(upload_to='item_images/optimized/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='item_images/thumbnails/', null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.item.title}"
    
    def save(self, *args, **kwargs):
        # Only process if this is a new image or the image has changed
        if not self.pk or 'image' in kwargs.get('update_fields', []):
            # Import here to avoid circular imports
            from .utils import optimize_image, create_thumbnail
            
            # Create optimized version
            if self.image:
                optimized_file = optimize_image(self.image, max_width=800, max_height=600)
                self.optimized_image.save(
                    f"opt_{self.image.name.split('/')[-1]}",
                    optimized_file,
                    save=False
                )
                
                # Create thumbnail
                thumbnail_file = create_thumbnail(self.image, size=(200, 150))
                self.thumbnail.save(
                    f"thumb_{self.image.name.split('/')[-1]}",
                    thumbnail_file,
                    save=False
                )
        
        super().save(*args, **kwargs)


class Booking(models.Model):
    """Rental bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    renter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='rentals')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.renter.user.email} - {self.item.title} ({self.start_date} to {self.end_date})"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date


class Review(models.Model):
    """Reviews and ratings for items and users"""
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_given')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['reviewer', 'booking']
    
    def __str__(self):
        return f"Review by {self.reviewer.user.email} - {self.rating} stars"
