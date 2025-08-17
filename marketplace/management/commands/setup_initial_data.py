from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Category, Profile, Item
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial categories and sample data for GearGo marketplace'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for GearGo...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Bikes',
                'description': 'Mountain bikes, road bikes, electric bikes, and more',
                'icon': 'fas fa-bicycle'
            },
            {
                'name': 'Instruments',
                'description': 'Guitars, pianos, drums, and other musical instruments',
                'icon': 'fas fa-music'
            },
            {
                'name': 'Sound Equipment',
                'description': 'Speakers, microphones, mixers, and audio gear',
                'icon': 'fas fa-volume-up'
            },
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            email='test@geargo.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('Created test user: test@geargo.com (password: testpass123)')
        else:
            self.stdout.write('Test user already exists: test@geargo.com')
        
        # Create sample items if they don't exist
        sample_items = [
            {
                'title': 'Mountain Bike - Trek Marlin 7',
                'description': 'Excellent condition mountain bike perfect for trails and city riding. 29-inch wheels, 21-speed Shimano drivetrain.',
                'category_name': 'Bikes',
                'daily_price': Decimal('25.00'),
                'condition': 'excellent',
                'location': 'San Francisco, CA'
            },
            {
                'title': 'Acoustic Guitar - Fender CD-60',
                'description': 'Beautiful acoustic guitar with warm tone. Perfect for beginners and intermediate players. Includes case.',
                'category_name': 'Instruments',
                'daily_price': Decimal('15.00'),
                'condition': 'good',
                'location': 'Los Angeles, CA'
            },
            {
                'title': 'PA Speaker System - JBL EON615',
                'description': 'Professional PA speaker system with 1000W power. Perfect for events, parties, and small venues.',
                'category_name': 'Sound Equipment',
                'daily_price': Decimal('75.00'),
                'condition': 'excellent',
                'location': 'New York, NY'
            },
            {
                'title': 'Electric Bike - Rad Power RadCity',
                'description': 'Electric bike with 750W motor and 45-mile range. Perfect for commuting and recreational riding.',
                'category_name': 'Bikes',
                'daily_price': Decimal('40.00'),
                'condition': 'good',
                'location': 'Seattle, WA'
            },
            {
                'title': 'Drum Kit - Pearl Export Series',
                'description': 'Complete 5-piece drum kit with cymbals and hardware. Great for practice and small gigs.',
                'category_name': 'Instruments',
                'daily_price': Decimal('35.00'),
                'condition': 'fair',
                'location': 'Austin, TX'
            },
            {
                'title': 'Wireless Microphone Set - Shure BLX24',
                'description': 'Professional wireless microphone system with 2 handheld mics. Ideal for presentations and performances.',
                'category_name': 'Sound Equipment',
                'daily_price': Decimal('45.00'),
                'condition': 'excellent',
                'location': 'Chicago, IL'
            }
        ]
        
        for item_data in sample_items:
            category = Category.objects.get(name=item_data['category_name'])
            
            # Check if item already exists
            existing_item = Item.objects.filter(title=item_data['title']).first()
            if not existing_item:
                item = Item.objects.create(
                    owner=test_user.profile,
                    category=category,
                    title=item_data['title'],
                    description=item_data['description'],
                    daily_price=item_data['daily_price'],
                    condition=item_data['condition'],
                    location=item_data['location']
                )
                self.stdout.write(f'Created sample item: {item.title}')
            else:
                self.stdout.write(f'Sample item already exists: {existing_item.title}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Run the development server: python manage.py runserver')
        self.stdout.write('2. Visit http://127.0.0.1:8000 to see the marketplace')
        self.stdout.write('3. Login with test@geargo.com / testpass123')
        self.stdout.write('4. Access admin at http://127.0.0.1:8000/admin')
