from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Item, Profile, Booking, Category, Review
import logging

logger = logging.getLogger(__name__)


class SimpleRecommendationEngine:
    """Simplified recommendation engine without heavy ML dependencies"""
    
    def get_personalized_recommendations(self, user, limit=6):
        """Get personalized recommendations for a user"""
        try:
            if not user.is_authenticated:
                return self.get_popular_items(limit)
            
            # Get user profile
            profile = getattr(user, 'profile', None)
            if not profile:
                return self.get_popular_items(limit)
            
            recommendations = []
            
            # 1. Category-based recommendations (based on user's preferred categories)
            category_recs = self._get_category_based_recommendations(profile, limit//2)
            recommendations.extend(category_recs)
            
            # 2. Collaborative filtering (based on similar users)
            if len(recommendations) < limit:
                collab_recs = self._get_collaborative_recommendations(user, limit - len(recommendations))
                recommendations.extend(collab_recs)
            
            # 3. Fill with popular items if needed
            if len(recommendations) < limit:
                popular_recs = self.get_popular_items(limit - len(recommendations))
                recommendations.extend(popular_recs)
            
            # Remove duplicates and limit
            seen_ids = set()
            unique_recommendations = []
            for item in recommendations:
                if item.id not in seen_ids and len(unique_recommendations) < limit:
                    seen_ids.add(item.id)
                    unique_recommendations.append(item)
            
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return self.get_popular_items(limit)
    
    def _get_category_based_recommendations(self, profile, limit=3):
        """Get recommendations based on user's preferred categories"""
        try:
            # Get user's booking history to determine preferred categories
            user_bookings = Booking.objects.filter(renter=profile)
            if user_bookings.exists():
                # Get categories from user's booking history
                category_counts = user_bookings.values('item__category').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                preferred_categories = [cat['item__category'] for cat in category_counts[:2]]
                
                # Get items from preferred categories
                items = Item.objects.filter(
                    category_id__in=preferred_categories,
                    availability_status='available'
                ).exclude(
                    owner=profile  # Don't recommend user's own items
                ).order_by('-created_at')[:limit]
                
                return list(items)
            
            # If no booking history, use user's profile preferences
            if profile.is_owner:
                # Owners might prefer items they can rent out
                return list(Item.objects.filter(
                    availability_status='available'
                ).exclude(
                    owner=profile
                ).order_by('-created_at')[:limit])
            
            return []
            
        except Exception as e:
            logger.error(f"Error in category-based recommendations: {e}")
            return []
    
    def _get_collaborative_recommendations(self, user, limit=3):
        """Get recommendations based on similar users' behavior"""
        try:
            # Get users who have similar booking patterns
            user_bookings = Booking.objects.filter(renter__user=user)
            if not user_bookings.exists():
                return []
            
            # Get categories this user has booked
            user_categories = set(user_bookings.values_list('item__category_id', flat=True))
            
            # Find users who have booked similar categories
            similar_users = Booking.objects.filter(
                item__category_id__in=user_categories
            ).exclude(
                renter__user=user
            ).values('renter__user').annotate(
                common_categories=Count('item__category', distinct=True)
            ).filter(
                common_categories__gte=1
            ).order_by('-common_categories')[:5]
            
            if not similar_users:
                return []
            
            # Get items that similar users have booked
            similar_user_ids = [u['renter__user'] for u in similar_users]
            recommended_items = Item.objects.filter(
                bookings__renter__user_id__in=similar_user_ids,
                availability_status='available'
            ).exclude(
                owner__user=user
            ).annotate(
                booking_count=Count('bookings')
            ).order_by('-booking_count', '-created_at')[:limit]
            
            return list(recommended_items)
            
        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {e}")
            return []
    
    def get_popular_items(self, limit=6):
        """Get popular items based on booking count and ratings"""
        try:
            return list(Item.objects.filter(
                availability_status='available'
            ).annotate(
                booking_count=Count('bookings'),
                avg_rating=Avg('reviews__rating')
            ).order_by('-booking_count', '-avg_rating', '-created_at')[:limit])
            
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return list(Item.objects.filter(
                availability_status='available'
            ).order_by('-created_at')[:limit])
    
    def get_similar_items(self, item, limit=4):
        """Get items similar to a given item based on category and condition"""
        try:
            # Get items with same category and similar condition
            similar_items = Item.objects.filter(
                category=item.category,
                availability_status='available'
            ).exclude(
                id=item.id
            ).order_by('-created_at')[:limit]
            
            if similar_items.count() < limit:
                # Fill with items from same category
                additional_items = Item.objects.filter(
                    category=item.category,
                    availability_status='available'
                ).exclude(
                    id__in=[item.id] + list(similar_items.values_list('id', flat=True))
                ).order_by('-created_at')[:limit - similar_items.count()]
                
                similar_items = list(similar_items) + list(additional_items)
            
            return list(similar_items)
            
        except Exception as e:
            logger.error(f"Error getting similar items: {e}")
            return []
    
    def get_trending_categories(self, limit=3):
        """Get trending categories based on recent bookings"""
        try:
            # Get bookings from last 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            trending_categories = Category.objects.filter(
                items__bookings__created_at__gte=thirty_days_ago
            ).annotate(
                recent_bookings=Count('items__bookings')
            ).order_by('-recent_bookings')[:limit]
            
            return list(trending_categories)
            
        except Exception as e:
            logger.error(f"Error getting trending categories: {e}")
            return list(Category.objects.all()[:limit])


class SimpleSmartPricingEngine:
    """Simplified smart pricing engine"""
    
    def suggest_price(self, item_data):
        """Suggest optimal price for an item"""
        try:
            # Get similar items for price comparison
            similar_items = Item.objects.filter(
                category=item_data.get('category'),
                condition=item_data.get('condition', 'good')
            ).exclude(
                daily_price__isnull=True
            )
            
            if similar_items.exists():
                # Calculate average price for similar items
                avg_price = similar_items.aggregate(Avg('daily_price'))['daily_price__avg']
                
                # Apply seasonal adjustments
                seasonal_multiplier = self._get_seasonal_multiplier(item_data.get('category'))
                
                # Apply demand-based adjustments
                demand_multiplier = self._get_demand_multiplier(item_data.get('category'))
                
                suggested_price = avg_price * seasonal_multiplier * demand_multiplier
                
                # Round to nearest dollar
                return round(suggested_price, 2)
            
            # Default pricing if no similar items
            return self._get_default_price(item_data.get('category'))
            
        except Exception as e:
            logger.error(f"Error suggesting price: {e}")
            return 25.0  # Default fallback price
    
    def _get_seasonal_multiplier(self, category):
        """Get seasonal price multiplier"""
        try:
            month = timezone.now().month
            
            # Seasonal adjustments based on category
            if category:
                category_name = category.name.lower()
                
                if 'bike' in category_name:
                    # Bikes are more expensive in summer
                    if month in [6, 7, 8]:  # Summer
                        return 1.2
                    elif month in [12, 1, 2]:  # Winter
                        return 0.8
                
                elif 'instrument' in category_name:
                    # Instruments are more expensive during school year
                    if month in [9, 10, 11, 3, 4, 5]:  # School year
                        return 1.1
                    else:
                        return 0.9
                
                elif 'sound' in category_name:
                    # Sound equipment is more expensive on weekends/holidays
                    return 1.15
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error getting seasonal multiplier: {e}")
            return 1.0
    
    def _get_demand_multiplier(self, category):
        """Get demand-based price multiplier"""
        try:
            if not category:
                return 1.0
            
            # Calculate demand based on recent bookings
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            recent_bookings = Booking.objects.filter(
                item__category=category,
                created_at__gte=thirty_days_ago
            ).count()
            
            # Adjust multiplier based on demand
            if recent_bookings > 10:
                return 1.2  # High demand
            elif recent_bookings > 5:
                return 1.1  # Medium demand
            elif recent_bookings < 2:
                return 0.9  # Low demand
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error getting demand multiplier: {e}")
            return 1.0
    
    def _get_default_price(self, category):
        """Get default price for a category"""
        if category:
            category_name = category.name.lower()
            
            if 'bike' in category_name:
                return 30.0
            elif 'instrument' in category_name:
                return 25.0
            elif 'sound' in category_name:
                return 40.0
        
        return 25.0


# Global instances
simple_recommendation_engine = SimpleRecommendationEngine()
simple_smart_pricing_engine = SimpleSmartPricingEngine()
