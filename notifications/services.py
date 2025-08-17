from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import Notification, EmailTemplate, EmailLog
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for handling email notifications"""
    
    @staticmethod
    def send_notification(user, notification_type, title, message, related_booking=None, related_item=None):
        """Create and send a notification"""
        try:
            # Create notification record
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_booking=related_booking,
                related_item=related_item
            )
            
            # Send email if user has email
            if user.email:
                EmailNotificationService.send_email_notification(user, notification_type, notification)
            
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def send_email_notification(user, notification_type, notification):
        """Send email notification"""
        try:
            # Get email template
            template = EmailTemplate.objects.filter(
                template_type=notification_type,
                is_active=True
            ).first()
            
            if not template:
                logger.warning(f"No email template found for {notification_type}")
                return
            
            # Prepare context
            context = {
                'user': user,
                'notification': notification,
                'site_name': 'GearGo',
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            # Render email content
            html_content = template.html_content
            text_content = template.text_content
            
            # Replace placeholders
            for key, value in context.items():
                if isinstance(value, str):
                    html_content = html_content.replace(f'{{{{ {key} }}}}', str(value))
                    text_content = text_content.replace(f'{{{{ {key} }}}}', str(value))
            
            # Create email log
            email_log = EmailLog.objects.create(
                user=user,
                template=template,
                subject=template.subject,
                recipient_email=user.email,
                status='pending'
            )
            
            # Send email
            success = send_mail(
                subject=template.subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False
            )
            
            if success:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
                email_log.save()
                logger.info(f"Email sent successfully to {user.email}")
            else:
                email_log.status = 'failed'
                email_log.error_message = 'Email send failed'
                email_log.save()
                logger.error(f"Failed to send email to {user.email}")
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            if 'email_log' in locals():
                email_log.status = 'failed'
                email_log.error_message = str(e)
                email_log.save()
    
    @staticmethod
    def send_booking_confirmation(booking):
        """Send booking confirmation emails"""
        # Email to renter
        EmailNotificationService.send_notification(
            user=booking.renter.user,
            notification_type='booking_created',
            title='Booking Confirmation',
            message=f'Your booking for "{booking.item.title}" has been created successfully.',
            related_booking=booking
        )
        
        # Email to owner
        EmailNotificationService.send_notification(
            user=booking.item.owner.user,
            notification_type='booking_created',
            title='New Booking Request',
            message=f'You have received a new booking request for "{booking.item.title}".',
            related_booking=booking
        )
    
    @staticmethod
    def send_booking_reminder(booking):
        """Send booking reminder email"""
        EmailNotificationService.send_notification(
            user=booking.renter.user,
            notification_type='booking_reminder',
            title='Upcoming Rental Reminder',
            message=f'Your rental for "{booking.item.title}" starts tomorrow.',
            related_booking=booking
        )
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new users"""
        EmailNotificationService.send_notification(
            user=user,
            notification_type='system_message',
            title='Welcome to GearGo!',
            message='Thank you for joining GearGo. Start exploring items to rent or list your own!'
        )
