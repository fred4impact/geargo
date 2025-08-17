from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .models import Item, Category, Booking, Profile, Review
from .forms import ItemForm, BookingForm, ProfileForm, UserForm
from notifications.models import Notification
from notifications.services import EmailNotificationService
# Import AI services with fallback
try:
    from .ai_services import recommendation_engine, smart_pricing_engine
    AI_AVAILABLE = True
except ImportError:
    # Fallback to simple AI services
    try:
        from .simple_ai import simple_recommendation_engine, simple_smart_pricing_engine
        recommendation_engine = simple_recommendation_engine
        smart_pricing_engine = simple_smart_pricing_engine
        AI_AVAILABLE = True
    except ImportError:
        AI_AVAILABLE = False
        recommendation_engine = None
        smart_pricing_engine = None


def home(request):
    """Home page view with AI recommendations"""
    # Get AI-powered recommendations if available
    if AI_AVAILABLE and recommendation_engine:
        if request.user.is_authenticated:
            recommended_items = recommendation_engine.get_personalized_recommendations(request.user, limit=6)
            trending_categories = recommendation_engine.get_trending_categories(limit=3)
        else:
            recommended_items = recommendation_engine.get_popular_items(limit=6)
            trending_categories = Category.objects.all()[:3]
    else:
        # Fallback to basic recommendations
        recommended_items = Item.objects.filter(availability_status='available').order_by('-created_at')[:6]
        trending_categories = Category.objects.all()[:3]
    
    # Get featured items (newest available)
    featured_items = Item.objects.filter(availability_status='available').order_by('-created_at')[:6]
    
    context = {
        'featured_items': featured_items,
        'recommended_items': recommended_items,
        'trending_categories': trending_categories,
        'categories': Category.objects.all(),
        'ai_available': AI_AVAILABLE,
    }
    return render(request, 'marketplace/home.html', context)


def item_list(request):
    """List all available items"""
    items = Item.objects.filter(availability_status='available').order_by('-created_at')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(title__icontains=search_query)
    
    # Pagination
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    }
    return render(request, 'marketplace/item_list.html', context)


def item_detail(request, item_id):
    """Detail view for a specific item with AI-powered similar items"""
    item = get_object_or_404(Item, id=item_id)
    
    # Get AI-powered similar items if available
    if AI_AVAILABLE and recommendation_engine:
        similar_items = recommendation_engine.get_similar_items(item, limit=4)
        # Fallback to category-based items if no AI recommendations
        if not similar_items:
            similar_items = Item.objects.filter(category=item.category).exclude(id=item.id)[:4]
    else:
        # Fallback to category-based items
        similar_items = Item.objects.filter(category=item.category).exclude(id=item.id)[:4]
    
    context = {
        'item': item,
        'similar_items': similar_items,
        'ai_available': AI_AVAILABLE,
    }
    return render(request, 'marketplace/item_detail.html', context)


@login_required
def item_create(request):
    """Create a new item with AI-powered smart pricing"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user.profile
            
            # Get AI-suggested price if not provided and AI is available
            if not item.daily_price and AI_AVAILABLE and smart_pricing_engine:
                suggested_price = smart_pricing_engine.suggest_price({
                    'category': item.category,
                    'condition': item.condition,
                    'title': item.title,
                    'description': item.description
                })
                item.daily_price = suggested_price
            
            item.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for image in images:
                from .models import ItemImage
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, 'Item created successfully!')
            return redirect('marketplace:item_detail', item_id=item.id)
    else:
        form = ItemForm()
    
    # Get AI-suggested price for the form
    suggested_price = None
    if AI_AVAILABLE and smart_pricing_engine and request.GET.get('category'):
        try:
            category = Category.objects.get(id=request.GET.get('category'))
            suggested_price = smart_pricing_engine.suggest_price({'category': category})
        except Category.DoesNotExist:
            pass
    
    context = {
        'form': form,
        'title': 'Create New Item',
        'suggested_price': suggested_price,
        'ai_available': AI_AVAILABLE,
    }
    return render(request, 'marketplace/item_form.html', context)


@login_required
def item_edit(request, item_id):
    """Edit an existing item"""
    item = get_object_or_404(Item, id=item_id, owner=request.user.profile)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            for image in images:
                from .models import ItemImage
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, 'Item updated successfully!')
            return redirect('marketplace:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'title': 'Edit Item',
    }
    return render(request, 'marketplace/item_form.html', context)


@login_required
def booking_list(request):
    """List user's bookings"""
    if request.user.profile.is_owner:
        # Show bookings for items owned by the user
        bookings = Booking.objects.filter(item__owner=request.user.profile)
    else:
        # Show bookings made by the user
        bookings = Booking.objects.filter(renter=request.user.profile)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Filter by date range
    date_range = request.GET.get('date_range')
    today = timezone.now().date()
    
    if date_range == 'upcoming':
        bookings = bookings.filter(start_date__gt=today)
    elif date_range == 'past':
        bookings = bookings.filter(end_date__lt=today)
    elif date_range == 'current':
        bookings = bookings.filter(start_date__lte=today, end_date__gte=today)
    
    # Order by creation date
    bookings = bookings.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
    }
    return render(request, 'marketplace/booking_list.html', context)


@login_required
def booking_detail(request, booking_id):
    """Detail view for a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to view this booking
    if booking.renter != request.user.profile and booking.item.owner != request.user.profile:
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('marketplace:booking_list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'marketplace/booking_detail.html', context)


@login_required
def booking_create(request, item_id):
    """Create a new booking"""
    item = get_object_or_404(Item, id=item_id, availability_status='available')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.renter = request.user.profile
            booking.item = item
            booking.total_amount = item.daily_price * booking.duration_days
            booking.save()
            
            # Update item availability
            item.availability_status = 'rented'
            item.save()
            
            # Send email notifications
            try:
                EmailNotificationService.send_booking_confirmation(booking)
            except Exception as e:
                # Log error but don't fail the booking creation
                print(f"Error sending email notification: {e}")
            
            messages.success(request, 'Booking created successfully!')
            return redirect('marketplace:booking_detail', booking_id=booking.id)
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'marketplace/booking_form.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    profile = request.user.profile
    
    # Get user's items if they're an owner
    owned_items = []
    if profile.is_owner:
        owned_items = Item.objects.filter(owner=profile).order_by('-created_at')
    
    # Get user's bookings
    bookings = Booking.objects.filter(renter=profile).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'owned_items': owned_items,
        'recent_bookings': bookings,
    }
    return render(request, 'marketplace/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('marketplace:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    context = {
        'form': form,
    }
    return render(request, 'marketplace/profile_form.html', context)


def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'marketplace/category_list.html', context)


def category_detail(request, category_id):
    """Detail view for a specific category"""
    category = get_object_or_404(Category, id=category_id)
    items = Item.objects.filter(category=category, availability_status='available').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'marketplace/category_detail.html', context)


@login_required
def dashboard(request):
    """Enhanced user dashboard with statistics and analytics"""
    user = request.user
    profile = user.profile
    
    # Get date ranges for analytics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    if profile.is_owner:
        # Owner dashboard statistics
        my_items = Item.objects.filter(owner=profile)
        total_items = my_items.count()
        active_items = my_items.filter(availability_status='available').count()
        
        # Booking statistics
        my_bookings = Booking.objects.filter(item__owner=profile)
        total_bookings = my_bookings.count()
        pending_bookings = my_bookings.filter(status='pending').count()
        active_bookings = my_bookings.filter(status='active').count()
        completed_bookings = my_bookings.filter(status='completed').count()
        
        # Earnings statistics
        total_earnings = my_bookings.filter(status__in=['confirmed', 'active', 'completed']).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_earnings = my_bookings.filter(
            status__in=['confirmed', 'active', 'completed'],
            created_at__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Recent activity
        recent_bookings = my_bookings.order_by('-created_at')[:5]
        recent_reviews = Review.objects.filter(item__owner=profile).order_by('-created_at')[:5]
        
        # Popular items
        popular_items = my_items.annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')[:5]
        
    else:
        # Renter dashboard statistics
        my_bookings = Booking.objects.filter(renter=profile)
        total_bookings = my_bookings.count()
        active_bookings = my_bookings.filter(status='active').count()
        completed_bookings = my_bookings.filter(status='completed').count()
        upcoming_bookings = my_bookings.filter(
            start_date__gte=today,
            status='confirmed'
        ).count()
        
        # Spending statistics
        total_spent = my_bookings.filter(status__in=['confirmed', 'active', 'completed']).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_spent = my_bookings.filter(
            status__in=['confirmed', 'active', 'completed'],
            created_at__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Recent activity
        recent_bookings = my_bookings.order_by('-created_at')[:5]
        recent_reviews = Review.objects.filter(reviewer=profile).order_by('-created_at')[:5]
        
        # Favorite categories
        favorite_categories = Category.objects.filter(
            items__bookings__renter=profile
        ).annotate(
            booking_count=Count('items__bookings')
        ).order_by('-booking_count')[:5]
    
    # Notifications
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    # Quick stats
    if profile.is_owner:
        quick_stats = [
            {
                'title': 'Total Items',
                'value': total_items,
                'change': '+2',
                'change_type': 'positive',
                'icon': 'fas fa-box',
                'color': 'primary'
            },
            {
                'title': 'Active Rentals',
                'value': active_bookings,
                'change': '+5',
                'change_type': 'positive',
                'icon': 'fas fa-calendar-check',
                'color': 'success'
            },
            {
                'title': 'Monthly Earnings',
                'value': f'${monthly_earnings:.2f}',
                'change': '+12.5%',
                'change_type': 'positive',
                'icon': 'fas fa-dollar-sign',
                'color': 'warning'
            },
            {
                'title': 'Pending Requests',
                'value': pending_bookings,
                'change': '-3',
                'change_type': 'negative',
                'icon': 'fas fa-clock',
                'color': 'info'
            }
        ]
    else:
        quick_stats = [
            {
                'title': 'Total Rentals',
                'value': total_bookings,
                'change': '+3',
                'change_type': 'positive',
                'icon': 'fas fa-calendar-check',
                'color': 'primary'
            },
            {
                'title': 'Active Rentals',
                'value': active_bookings,
                'change': '+1',
                'change_type': 'positive',
                'icon': 'fas fa-play',
                'color': 'success'
            },
            {
                'title': 'Monthly Spending',
                'value': f'${monthly_spent:.2f}',
                'change': '+8.2%',
                'change_type': 'positive',
                'icon': 'fas fa-credit-card',
                'color': 'warning'
            },
            {
                'title': 'Upcoming Rentals',
                'value': upcoming_bookings,
                'change': '+2',
                'change_type': 'positive',
                'icon': 'fas fa-calendar-plus',
                'color': 'info'
            }
        ]
    
    context = {
        'profile': profile,
        'quick_stats': quick_stats,
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    if profile.is_owner:
        context.update({
            'total_earnings': total_earnings,
            'monthly_earnings': monthly_earnings,
            'popular_items': popular_items,
            'active_items': active_items,
            'pending_bookings': pending_bookings,
            'completed_bookings': completed_bookings,
        })
    else:
        context.update({
            'total_spent': total_spent,
            'monthly_spent': monthly_spent,
            'favorite_categories': favorite_categories,
            'upcoming_bookings': upcoming_bookings,
            'completed_bookings': completed_bookings,
        })
    
    return render(request, 'marketplace/dashboard.html', context)
