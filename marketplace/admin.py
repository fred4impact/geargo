from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Category, Item, ItemImage, Booking, Review


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


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Review, ReviewAdmin)
