import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Item, Profile, Booking, Category, Review
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """AI-powered recommendation engine for GearGo"""
    
    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self._fit_models()
    
    def _fit_models(self):
        """Fit the recommendation models with current data"""
        try:
            # Get all items for content-based filtering
            items = Item.objects.all()
            if items.exists():
                # Create item descriptions for TF-IDF
                item_descriptions = []
                for item in items:
                    desc = f"{item.title} {item.description} {item.category.name} {item.condition}"
                    item_descriptions.append(desc)
                
                # Fit TF-IDF vectorizer
                self.tfidf_matrix = self.tfidf.fit_transform(item_descriptions)
                self.item_ids = list(items.values_list('id', flat=True))
                
                logger.info(f"Fitted recommendation models with {len(items)} items")
            else:
                logger.warning("No items found for recommendation model fitting")
                
        except Exception as e:
            logger.error(f"Error fitting recommendation models: {e}")
    
    def get_personalized_recommendations(self, user, limit=6):
        """Get personalized recommendations for a user with category diversity"""
        try:
            if not user.is_authenticated:
                return self.get_popular_items(limit)
            
            # Get user profile
            profile = getattr(user, 'profile', None)
            if not profile:
                return self.get_popular_items(limit)
            
            recommendations = []
            
            # 1. Seasonal recommendations (1-2 items)
            seasonal_recs = self._get_seasonal_recommendations(min(2, limit//3))
            recommendations.extend(seasonal_recs)
            
            # 2. Category-based recommendations (1-2 items)
            category_recs = self._get_category_based_recommendations(profile, min(2, limit//3))
            recommendations.extend(category_recs)
            
            # 3. Collaborative filtering (1-2 items)
            if len(recommendations) < limit:
                collab_recs = self._get_collaborative_recommendations(user, min(2, limit - len(recommendations)))
                recommendations.extend(collab_recs)
            
            # 4. Content-based recommendations (1-2 items)
            if len(recommendations) < limit:
                content_recs = self._get_content_based_recommendations(user, min(2, limit - len(recommendations)))
                recommendations.extend(content_recs)
            
            # 5. Fill with diverse popular items if needed
            if len(recommendations) < limit:
                popular_recs = self.get_popular_items(limit - len(recommendations))
                recommendations.extend(popular_recs)
            
            # Remove duplicates and ensure category diversity
            seen_ids = set()
            category_counts = {}
            final_recommendations = []
            
            for item in recommendations:
                if item.id not in seen_ids and len(final_recommendations) < limit:
                    category_name = item.category.name
                    current_count = category_counts.get(category_name, 0)
                    
                    # Limit items per category to ensure diversity
                    max_per_category = max(2, limit // 3)  # At most 2 items per category for 6 total
                    
                    if current_count < max_per_category:
                        seen_ids.add(item.id)
                        category_counts[category_name] = current_count + 1
                        final_recommendations.append(item)
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return self.get_popular_items(limit)
    
    def _get_seasonal_recommendations(self, limit=2):
        """Get seasonal recommendations based on current time and upcoming events"""
        try:
            current_month = timezone.now().month
            current_day = timezone.now().day
            
            # Define seasonal categories and events
            seasonal_mapping = {
                # Summer months (June-August)
                6: ['Events & Entertainment', 'Sports & Recreation'],  # June - Summer parties, outdoor events
                7: ['Events & Entertainment', 'Sports & Recreation'],  # July - Independence Day, summer activities
                8: ['Events & Entertainment', 'Sports & Recreation'],  # August - Summer vacations, outdoor events
                
                # Fall months (September-November)
                9: ['Events & Entertainment', 'Home & Garden'],  # September - Back to school, fall cleanup
                10: ['Events & Entertainment', 'Home & Garden'],  # October - Halloween, fall decorations
                11: ['Events & Entertainment', 'Home & Garden'],  # November - Thanksgiving, fall cleanup
                
                # Winter months (December-February)
                12: ['Events & Entertainment', 'Sports & Recreation'],  # December - Christmas, New Year
                1: ['Events & Entertainment', 'Sports & Recreation'],   # January - New Year, winter sports
                2: ['Events & Entertainment', 'Sports & Recreation'],   # February - Valentine's Day, winter sports
                
                # Spring months (March-May)
                3: ['Home & Garden', 'Sports & Recreation'],  # March - Spring cleaning, outdoor activities
                4: ['Home & Garden', 'Sports & Recreation'],  # April - Easter, spring gardening
                5: ['Home & Garden', 'Sports & Recreation'],  # May - Mother's Day, outdoor activities
            }
            
            # Get seasonal categories
            seasonal_categories = seasonal_mapping.get(current_month, ['Events & Entertainment'])
            
            # Get items from seasonal categories
            seasonal_items = Item.objects.filter(
                category__name__in=seasonal_categories,
                availability_status='available'
            ).order_by('-created_at')[:limit*2]  # Get more to filter
            
            # Prioritize based on specific events
            prioritized_items = []
            for item in seasonal_items:
                priority_score = 0
                
                # Event-specific prioritization
                if current_month == 12:  # December - Christmas
                    if any(keyword in item.title.lower() for keyword in ['party', 'light', 'sound', 'camera', 'video']):
                        priority_score += 3
                elif current_month == 7:  # July - Independence Day
                    if any(keyword in item.title.lower() for keyword in ['party', 'sound', 'light', 'camera']):
                        priority_score += 3
                elif current_month == 10:  # October - Halloween
                    if any(keyword in item.title.lower() for keyword in ['party', 'light', 'camera', 'costume']):
                        priority_score += 3
                elif current_month in [3, 4, 5]:  # Spring - Gardening
                    if any(keyword in item.title.lower() for keyword in ['garden', 'lawn', 'tool', 'clean']):
                        priority_score += 3
                
                prioritized_items.append((item, priority_score))
            
            # Sort by priority and return top items
            prioritized_items.sort(key=lambda x: x[1], reverse=True)
            return [item for item, score in prioritized_items[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting seasonal recommendations: {e}")
            return []
    
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
    
    def _get_content_based_recommendations(self, user, limit=3):
        """Get recommendations based on item content similarity"""
        try:
            if not hasattr(self, 'tfidf_matrix') or not hasattr(self, 'item_ids'):
                return []
            
            # Get user's recent bookings
            recent_bookings = Booking.objects.filter(
                renter__user=user
            ).select_related('item').order_by('-created_at')[:3]
            
            if not recent_bookings.exists():
                return []
            
            # Calculate similarity with recent items
            all_items = Item.objects.filter(availability_status='available')
            if not all_items.exists():
                return []
            
            # Create TF-IDF matrix for current items
            item_descriptions = []
            current_item_ids = []
            for item in all_items:
                desc = f"{item.title} {item.description} {item.category.name} {item.condition}"
                item_descriptions.append(desc)
                current_item_ids.append(item.id)
            
            if not item_descriptions:
                return []
            
            # Transform current items
            current_tfidf = self.tfidf.transform(item_descriptions)
            
            # Calculate similarity with user's recent items
            recent_item_descriptions = []
            for booking in recent_bookings:
                desc = f"{booking.item.title} {booking.item.description} {booking.item.category.name} {booking.item.condition}"
                recent_item_descriptions.append(desc)
            
            if recent_item_descriptions:
                recent_tfidf = self.tfidf.transform(recent_item_descriptions)
                similarities = cosine_similarity(recent_tfidf, current_tfidf)
                
                # Get average similarity scores
                avg_similarities = np.mean(similarities, axis=0)
                
                # Get top similar items
                top_indices = np.argsort(avg_similarities)[::-1][:limit*2]  # Get more to filter
                
                recommended_items = []
                for idx in top_indices:
                    if idx < len(current_item_ids):
                        item = all_items.filter(id=current_item_ids[idx]).first()
                        if item and item.owner.user != user:
                            recommended_items.append(item)
                            if len(recommended_items) >= limit:
                                break
                
                return recommended_items
            
            return []
            
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {e}")
            return []
    
    def get_popular_items(self, limit=6):
        """Get popular items based on booking count and ratings from all categories"""
        try:
            # Get items from all categories, prioritizing popular ones
            items = Item.objects.filter(
                availability_status='available'
            ).annotate(
                booking_count=Count('bookings'),
                avg_rating=Avg('reviews__rating')
            ).order_by('-booking_count', '-avg_rating', '-created_at')
            
            # Ensure diversity by getting items from different categories
            category_items = {}
            final_items = []
            
            for item in items:
                category_name = item.category.name
                if category_name not in category_items:
                    category_items[category_name] = []
                category_items[category_name].append(item)
            
            # Take items from each category to ensure diversity
            max_per_category = max(1, limit // len(category_items)) if category_items else 1
            
            for category_name, category_item_list in category_items.items():
                final_items.extend(category_item_list[:max_per_category])
                if len(final_items) >= limit:
                    break
            
            # If we don't have enough diverse items, fill with remaining popular items
            if len(final_items) < limit:
                remaining_items = [item for item in items if item not in final_items]
                final_items.extend(remaining_items[:limit - len(final_items)])
            
            return final_items[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return list(Item.objects.filter(
                availability_status='available'
            ).order_by('-created_at')[:limit])
    
    def get_similar_items(self, item, limit=4):
        """Get items similar to a given item"""
        try:
            if not hasattr(self, 'tfidf_matrix') or not hasattr(self, 'item_ids'):
                return []
            
            # Find the item in our TF-IDF matrix
            if item.id not in self.item_ids:
                return []
            
            item_idx = self.item_ids.index(item.id)
            item_vector = self.tfidf_matrix[item_idx:item_idx+1]
            
            # Calculate similarity with all other items
            similarities = cosine_similarity(item_vector, self.tfidf_matrix).flatten()
            
            # Get top similar items (excluding the item itself)
            similar_indices = np.argsort(similarities)[::-1][1:limit+1]
            
            similar_items = []
            for idx in similar_indices:
                if idx < len(self.item_ids):
                    similar_item = Item.objects.filter(
                        id=self.item_ids[idx],
                        availability_status='available'
                    ).first()
                    if similar_item and similar_item != item:
                        similar_items.append(similar_item)
            
            return similar_items
            
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
    
    def get_event_based_recommendations(self, event_type=None, limit=4):
        """Get recommendations based on specific events"""
        try:
            if not event_type:
                # Auto-detect event type based on current date
                current_month = timezone.now().month
                current_day = timezone.now().day
                
                if current_month == 12:
                    event_type = 'christmas'
                elif current_month == 7 and current_day >= 4:
                    event_type = 'independence_day'
                elif current_month == 10 and current_day >= 25:
                    event_type = 'halloween'
                elif current_month == 2 and current_day >= 10:
                    event_type = 'valentines'
                elif current_month in [3, 4, 5]:
                    event_type = 'spring_cleaning'
                else:
                    event_type = 'general'
            
            # Event-specific item keywords
            event_keywords = {
                'christmas': ['party', 'light', 'sound', 'camera', 'video', 'music', 'speaker'],
                'independence_day': ['party', 'sound', 'light', 'camera', 'speaker', 'music'],
                'halloween': ['party', 'light', 'camera', 'costume', 'sound', 'speaker'],
                'valentines': ['camera', 'light', 'music', 'speaker', 'party'],
                'spring_cleaning': ['clean', 'garden', 'lawn', 'tool', 'pressure'],
                'general': ['party', 'camera', 'sound', 'tool', 'sport']
            }
            
            keywords = event_keywords.get(event_type, ['party', 'camera', 'sound'])
            
            # Search for items matching event keywords
            event_items = Item.objects.filter(
                availability_status='available'
            ).filter(
                Q(title__icontains=keywords[0]) |
                Q(description__icontains=keywords[0]) |
                Q(category__name__icontains='Events & Entertainment')
            ).order_by('-created_at')[:limit]
            
            return list(event_items)
            
        except Exception as e:
            logger.error(f"Error getting event-based recommendations: {e}")
            return []


class SmartPricingEngine:
    """AI-powered smart pricing engine"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
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
                
                # Apply event-based adjustments
                event_multiplier = self._get_event_multiplier(item_data.get('category'))
                
                suggested_price = avg_price * seasonal_multiplier * demand_multiplier * event_multiplier
                
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
            current_month = timezone.now().month
            
            # Seasonal adjustments based on category
            if category:
                category_name = category.name.lower()
                
                if 'bike' in category_name:
                    # Bikes are more expensive in summer
                    if current_month in [6, 7, 8]:  # Summer
                        return 1.2
                    elif current_month in [12, 1, 2]:  # Winter
                        return 0.8
                
                elif 'instrument' in category_name:
                    # Instruments are more expensive during school year
                    if current_month in [9, 10, 11, 3, 4, 5]:  # School year
                        return 1.1
                    else:
                        return 0.9
                
                elif 'sound' in category_name:
                    # Sound equipment is more expensive on weekends/holidays
                    return 1.15
                
                elif 'events' in category_name or 'entertainment' in category_name:
                    # Event equipment pricing varies by season
                    if current_month in [6, 7, 8]:  # Summer - outdoor events
                        return 1.3
                    elif current_month in [12]:  # December - holiday season
                        return 1.4
                    elif current_month in [10]:  # October - Halloween
                        return 1.25
                    elif current_month in [2]:  # February - Valentine's Day
                        return 1.2
                    else:
                        return 1.1
            
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
    
    def _get_event_multiplier(self, category):
        """Get event-based price multiplier"""
        try:
            if not category:
                return 1.0
            
            current_month = timezone.now().month
            current_day = timezone.now().day
            
            category_name = category.name.lower()
            
            if 'events' in category_name or 'entertainment' in category_name:
                # Event equipment pricing for specific events
                if current_month == 12:  # Christmas season
                    return 1.3
                elif current_month == 7 and current_day >= 4:  # Independence Day
                    return 1.25
                elif current_month == 10 and current_day >= 25:  # Halloween
                    return 1.2
                elif current_month == 2 and current_day >= 10:  # Valentine's Day
                    return 1.15
                elif current_month in [6, 7, 8]:  # Summer events
                    return 1.1
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error getting event multiplier: {e}")
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
            elif 'events' in category_name or 'entertainment' in category_name:
                return 50.0  # Event equipment typically more expensive
        
        return 25.0


class AIPoweredFeatures:
    """Advanced AI-powered features for GearGo"""
    
    @staticmethod
    def get_weather_based_recommendations(weather_condition, limit=4):
        """Get recommendations based on weather conditions"""
        try:
            weather_keywords = {
                'sunny': ['bike', 'outdoor', 'sport', 'camera', 'party'],
                'rainy': ['indoor', 'game', 'music', 'instrument', 'movie'],
                'snowy': ['sport', 'winter', 'indoor', 'game', 'music'],
                'cloudy': ['camera', 'outdoor', 'sport', 'bike', 'party']
            }
            
            keywords = weather_keywords.get(weather_condition, ['party', 'camera', 'sound'])
            
            weather_items = Item.objects.filter(
                availability_status='available'
            ).filter(
                Q(title__icontains=keywords[0]) |
                Q(description__icontains=keywords[0]) |
                Q(category__name__in=['Sports & Recreation', 'Events & Entertainment'])
            ).order_by('-created_at')[:limit]
            
            return list(weather_items)
            
        except Exception as e:
            logger.error(f"Error getting weather-based recommendations: {e}")
            return []
    
    @staticmethod
    def get_weekend_recommendations(limit=4):
        """Get recommendations optimized for weekend activities"""
        try:
            weekend_items = Item.objects.filter(
                availability_status='available'
            ).filter(
                Q(category__name__in=['Events & Entertainment', 'Sports & Recreation']) |
                Q(title__icontains='party') |
                Q(title__icontains='game') |
                Q(title__icontains='sport') |
                Q(title__icontains='camera')
            ).order_by('-created_at')[:limit]
            
            return list(weekend_items)
            
        except Exception as e:
            logger.error(f"Error getting weekend recommendations: {e}")
            return []
    
    @staticmethod
    def get_budget_recommendations(max_price, limit=4):
        """Get recommendations within a specific budget"""
        try:
            budget_items = Item.objects.filter(
                availability_status='available',
                daily_price__lte=max_price
            ).order_by('daily_price', '-created_at')[:limit]
            
            return list(budget_items)
            
        except Exception as e:
            logger.error(f"Error getting budget recommendations: {e}")
            return []
    
    @staticmethod
    def get_trending_items(days=7, limit=4):
        """Get trending items based on recent activity"""
        try:
            recent_date = timezone.now() - timedelta(days=days)
            
            trending_items = Item.objects.filter(
                availability_status='available',
                bookings__created_at__gte=recent_date
            ).annotate(
                recent_bookings=Count('bookings')
            ).order_by('-recent_bookings', '-created_at')[:limit]
            
            return list(trending_items)
            
        except Exception as e:
            logger.error(f"Error getting trending items: {e}")
            return []


# Global instances
recommendation_engine = RecommendationEngine()
smart_pricing_engine = SmartPricingEngine()
ai_features = AIPoweredFeatures()
