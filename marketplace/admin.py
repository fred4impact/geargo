from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Category, Item, ItemImage, Booking, Review, ServiceCategory, Service, ServiceBooking, ServiceReview


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'category', 'daily_price', 'condition', 'availability_status', 'created_at']
    list_filter = ['category', 'condition', 'availability_status', 'created_at']
    search_fields = ['title', 'description', 'owner__user__email']
    inlines = [ItemImageInline]
    readonly_fields = ['id', 'created_at', 'updated_at']


class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'renter', 'item', 'start_date', 'end_date', 'total_amount', 'status']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['renter__user__email', 'item__title']
    readonly_fields = ['id', 'created_at', 'updated_at']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'item', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__user__email', 'item__title', 'comment']


class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'category', 'hourly_rate', 'available', 'average_rating', 'total_reviews']
    list_filter = ['category', 'available', 'created_at']
    search_fields = ['title', 'provider__user__email', 'description']
    readonly_fields = ['created_at', 'updated_at', 'average_rating', 'total_reviews']
    
    def average_rating(self, obj):
        return f"{obj.average_rating:.1f}"
    average_rating.short_description = 'Avg Rating'
    
    def total_reviews(self, obj):
        return obj.total_reviews
    total_reviews.short_description = 'Reviews'


class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['service', 'customer', 'start_time', 'end_time', 'total_cost', 'status']
    list_filter = ['status', 'start_time', 'created_at']
    search_fields = ['service__title', 'customer__user__email', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'total_hours', 'total_cost']


class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['service__title', 'customer__user__email', 'comment']
    readonly_fields = ['created_at']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Review, ReviewAdmin)

# Register service models
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceBooking, ServiceBookingAdmin)
admin.site.register(ServiceReview, ServiceReviewAdmin)
