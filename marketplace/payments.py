import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Booking

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session_for_booking(booking):
    """Create a Stripe Checkout Session for a booking and persist its id."""
    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(booking.total_amount * 100),
                'product_data': {
                    'name': booking.item.title,
                    'description': f"Rental from {booking.start_date} to {booking.end_date}",
                },
            },
            'quantity': 1,
        }],
        metadata={'booking_id': str(booking.id)},
        success_url=f"{settings.FRONTEND_URL}/bookings/{booking.id}?payment=success",
        cancel_url=f"{settings.FRONTEND_URL}/bookings/{booking.id}?payment=cancelled",
    )
    booking.stripe_checkout_session_id = session.id
    booking.save(update_fields=['stripe_checkout_session_id'])
    return session


def _mark_booking_paid(booking_id, payment_intent_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        logger.error(f"Stripe webhook: booking {booking_id} not found")
        return
    booking.payment_status = 'paid'
    booking.payment_date = timezone.now()
    booking.payment_transaction_id = payment_intent_id or ''
    if booking.status == 'pending':
        booking.status = 'confirmed'
    booking.save()
    logger.info(f"Booking {booking_id} marked as paid via Stripe")

    from notifications.services import EmailNotificationService
    EmailNotificationService.send_notification(
        user=booking.renter.user,
        notification_type='payment_received',
        title='Payment Received',
        message=f'Your payment for "{booking.item.title}" was received. Your booking is confirmed.',
        related_booking=booking,
    )


def _mark_booking_failed(booking_id):
    Booking.objects.filter(id=booking_id, payment_status='pending').update(payment_status='failed')
    logger.info(f"Booking {booking_id} payment marked as failed/expired")


@csrf_exempt
def stripe_webhook(request):
    """Handle asynchronous Stripe events (checkout completion, expiry)."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning(f"Invalid Stripe webhook payload/signature: {e}")
        return HttpResponse(status=400)

    event_type = event['type']
    session = event['data']['object']
    booking_id = session.get('metadata', {}).get('booking_id')

    if event_type == 'checkout.session.completed' and booking_id:
        _mark_booking_paid(booking_id, session.get('payment_intent', ''))
    elif event_type == 'checkout.session.expired' and booking_id:
        _mark_booking_failed(booking_id)

    return HttpResponse(status=200)
