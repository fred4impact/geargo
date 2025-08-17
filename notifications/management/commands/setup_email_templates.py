from django.core.management.base import BaseCommand
from notifications.models import EmailTemplate


class Command(BaseCommand):
    help = 'Set up default email templates for notifications'

    def handle(self, *args, **options):
        templates_data = [
            {
                'template_type': 'booking_created',
                'subject': 'Booking Confirmation - GearGo',
                'html_content': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .footer { text-align: center; padding: 20px; color: #666; }
                        .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>GearGo</h1>
                        </div>
                        <div class="content">
                            <h2>Booking Confirmation</h2>
                            <p>Hello {{ user.first_name }},</p>
                            <p>Your booking has been created successfully!</p>
                            <p><strong>Item:</strong> {{ notification.related_booking.item.title }}</p>
                            <p><strong>Start Date:</strong> {{ notification.related_booking.start_date }}</p>
                            <p><strong>End Date:</strong> {{ notification.related_booking.end_date }}</p>
                            <p><strong>Total Amount:</strong> ${{ notification.related_booking.total_amount }}</p>
                            <p><a href="{{ site_url }}/bookings/{{ notification.related_booking.id }}/" class="btn">View Booking Details</a></p>
                        </div>
                        <div class="footer">
                            <p>Thank you for using GearGo!</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Booking Confirmation - GearGo
                
                Hello {{ user.first_name }},
                
                Your booking has been created successfully!
                
                Item: {{ notification.related_booking.item.title }}
                Start Date: {{ notification.related_booking.start_date }}
                End Date: {{ notification.related_booking.end_date }}
                Total Amount: ${{ notification.related_booking.total_amount }}
                
                View your booking: {{ site_url }}/bookings/{{ notification.related_booking.id }}/
                
                Thank you for using GearGo!
                '''
            },
            {
                'template_type': 'booking_reminder',
                'subject': 'Upcoming Rental Reminder - GearGo',
                'html_content': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .footer { text-align: center; padding: 20px; color: #666; }
                        .btn { display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>GearGo</h1>
                        </div>
                        <div class="content">
                            <h2>Upcoming Rental Reminder</h2>
                            <p>Hello {{ user.first_name }},</p>
                            <p>This is a friendly reminder that your rental starts tomorrow!</p>
                            <p><strong>Item:</strong> {{ notification.related_booking.item.title }}</p>
                            <p><strong>Start Date:</strong> {{ notification.related_booking.start_date }}</p>
                            <p><strong>End Date:</strong> {{ notification.related_booking.end_date }}</p>
                            <p><a href="{{ site_url }}/bookings/{{ notification.related_booking.id }}/" class="btn">View Booking Details</a></p>
                        </div>
                        <div class="footer">
                            <p>Thank you for using GearGo!</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Upcoming Rental Reminder - GearGo
                
                Hello {{ user.first_name }},
                
                This is a friendly reminder that your rental starts tomorrow!
                
                Item: {{ notification.related_booking.item.title }}
                Start Date: {{ notification.related_booking.start_date }}
                End Date: {{ notification.related_booking.end_date }}
                
                View your booking: {{ site_url }}/bookings/{{ notification.related_booking.id }}/
                
                Thank you for using GearGo!
                '''
            },
            {
                'template_type': 'welcome',
                'subject': 'Welcome to GearGo!',
                'html_content': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .footer { text-align: center; padding: 20px; color: #666; }
                        .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to GearGo!</h1>
                        </div>
                        <div class="content">
                            <h2>Hello {{ user.first_name }},</h2>
                            <p>Welcome to GearGo - your AI-powered rental marketplace!</p>
                            <p>We're excited to have you join our community. Here's what you can do:</p>
                            <ul>
                                <li>Browse and rent items from other users</li>
                                <li>List your own items for rent</li>
                                <li>Earn money by sharing your gear</li>
                                <li>Connect with other gear enthusiasts</li>
                            </ul>
                            <p><a href="{{ site_url }}/" class="btn">Start Exploring</a></p>
                        </div>
                        <div class="footer">
                            <p>Thank you for joining GearGo!</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Welcome to GearGo!
                
                Hello {{ user.first_name }},
                
                Welcome to GearGo - your AI-powered rental marketplace!
                
                We're excited to have you join our community. Here's what you can do:
                - Browse and rent items from other users
                - List your own items for rent
                - Earn money by sharing your gear
                - Connect with other gear enthusiasts
                
                Start exploring: {{ site_url }}/
                
                Thank you for joining GearGo!
                '''
            }
        ]

        for template_data in templates_data:
            template, created = EmailTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created email template: {template.template_type}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Email template already exists: {template.template_type}')
                )

        self.stdout.write(
            self.style.SUCCESS('Email templates setup completed!')
        )
