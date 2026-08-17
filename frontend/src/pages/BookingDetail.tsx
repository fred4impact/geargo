import { useParams, useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './BookingDetail.css';

const BookingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const paymentResult = searchParams.get('payment');

  const { data: booking, isLoading, refetch } = useQuery({
    queryKey: ['booking', id],
    queryFn: async () => {
      const response = await bookingApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const payMutation = useMutation({
    mutationFn: async () => {
      const response = await bookingApi.createCheckoutSession(id!);
      return response.data;
    },
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const response = await bookingApi.cancel(id!);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', id] });
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] });
    },
  });

  if (isLoading) return <div className="loading">Loading booking...</div>;

  if (!booking) {
    return (
      <div className="booking-detail">
        <p className="no-bookings">Booking not found.</p>
      </div>
    );
  }

  const isRenter = booking.renter.id === user?.id;
  const isOwner = booking.item.owner.id === user?.id;
  const canPay = isRenter && booking.payment_status === 'pending' && booking.status !== 'cancelled';
  const canCancel = (isRenter || isOwner) && ['pending', 'confirmed'].includes(booking.status);

  return (
    <div className="booking-detail">
      <Link to="/bookings" className="back-link">← Back to my bookings</Link>

      {paymentResult === 'success' && (
        <div className="payment-banner payment-banner-success">
          Payment received — we'll update the status shortly once Stripe confirms it.
          <button className="link-button" onClick={() => refetch()}>Refresh</button>
        </div>
      )}
      {paymentResult === 'cancelled' && (
        <div className="payment-banner payment-banner-cancelled">
          Payment was cancelled. You can try again below.
        </div>
      )}

      <div className="booking-detail-card">
        <h1>{booking.item.title}</h1>
        <p className="booking-dates">
          {new Date(booking.start_date).toLocaleDateString()} —{' '}
          {new Date(booking.end_date).toLocaleDateString()} ({booking.duration_days} days)
        </p>
        <p className="booking-amount">Total: ${booking.total_amount}</p>

        <div className="booking-status">
          <span className={`status-badge ${booking.status}`}>{booking.status}</span>
          <span className={`status-badge ${booking.payment_status}`}>{booking.payment_status}</span>
        </div>

        {canPay && (
          <button
            className="btn btn-primary pay-button"
            onClick={() => payMutation.mutate()}
            disabled={payMutation.isPending}
          >
            {payMutation.isPending ? 'Redirecting to Stripe...' : 'Pay Now'}
          </button>
        )}
        {payMutation.isError && (
          <p className="payment-error">Couldn't start checkout. Please try again.</p>
        )}

        {canCancel && (
          <button
            className="btn btn-secondary cancel-button"
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
          >
            {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Booking'}
          </button>
        )}
        {cancelMutation.isError && (
          <p className="payment-error">Couldn't cancel booking. Please try again.</p>
        )}
      </div>
    </div>
  );
};

export default BookingDetail;
