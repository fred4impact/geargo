import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceBookingApi, serviceReviewApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import type { ServiceBooking } from '../types';
import StarRatingInput from '../components/StarRatingInput';
import './BookingList.css';

const ServiceBookingCard = ({ booking, currentUserId }: { booking: ServiceBooking; currentUserId?: number }) => {
  const queryClient = useQueryClient();
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');

  const isCustomer = booking.customer.id === currentUserId;
  const isProvider = booking.service.provider.id === currentUserId;
  const canCancel = isCustomer && ['pending', 'confirmed'].includes(booking.status);
  const canComplete = isProvider && ['confirmed', 'in_progress'].includes(booking.status);
  const canConfirm = isProvider && booking.status === 'pending';

  const { data: existingReview } = useQuery({
    queryKey: ['service-review', booking.id],
    queryFn: async () => {
      const response = await serviceReviewApi.list({ booking: booking.id });
      return response.data.results[0] ?? null;
    },
    enabled: isCustomer && booking.status === 'completed',
  });

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const response = await serviceBookingApi.update(booking.id, { status: 'cancelled' });
      return response.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['my-service-bookings'] }),
  });

  const confirmMutation = useMutation({
    mutationFn: async () => {
      const response = await serviceBookingApi.update(booking.id, { status: 'confirmed' });
      return response.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['my-service-bookings'] }),
  });

  const completeMutation = useMutation({
    mutationFn: async () => {
      const response = await serviceBookingApi.complete(booking.id);
      return response.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['my-service-bookings'] }),
  });

  const reviewMutation = useMutation({
    mutationFn: async () => {
      const response = await serviceReviewApi.create({
        booking_id: booking.id,
        rating: reviewRating,
        comment: reviewComment,
      });
      return response.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['service-review', booking.id] }),
  });

  const canReview = isCustomer && booking.status === 'completed' && !existingReview;

  return (
    <div className="booking-card">
      <h3>{booking.service.title}</h3>
      <p className="booking-dates">
        {new Date(booking.start_time).toLocaleString()} —{' '}
        {new Date(booking.end_time).toLocaleString()}
      </p>
      <p className="booking-amount">Total: ${booking.total_cost}</p>
      <div className="booking-status">
        <span className={`status-badge ${booking.status}`}>{booking.status}</span>
      </div>

      {canConfirm && (
        <button
          type="button"
          className="btn btn-primary"
          style={{ marginTop: '1rem' }}
          disabled={confirmMutation.isPending}
          onClick={() => confirmMutation.mutate()}
        >
          {confirmMutation.isPending ? 'Confirming...' : 'Confirm Booking'}
        </button>
      )}

      {canCancel && (
        <button
          type="button"
          className="btn btn-secondary"
          style={{ marginTop: '1rem' }}
          disabled={cancelMutation.isPending}
          onClick={() => cancelMutation.mutate()}
        >
          Cancel Booking
        </button>
      )}

      {canComplete && (
        <button
          type="button"
          className="btn btn-secondary"
          style={{ marginTop: '1rem' }}
          disabled={completeMutation.isPending}
          onClick={() => completeMutation.mutate()}
        >
          {completeMutation.isPending ? 'Marking complete...' : 'Mark as Completed'}
        </button>
      )}

      {existingReview && (
        <div className="review-summary">
          <div className="review-stars" aria-label={`${existingReview.rating} out of 5 stars`}>
            {'★'.repeat(existingReview.rating)}{'☆'.repeat(5 - existingReview.rating)}
          </div>
          <p>{existingReview.comment}</p>
        </div>
      )}

      {canReview && (
        <div className="review-form">
          <StarRatingInput value={reviewRating} onChange={setReviewRating} />
          <textarea
            placeholder="How was this service?"
            value={reviewComment}
            onChange={(e) => setReviewComment(e.target.value)}
            rows={2}
          />
          <button
            type="button"
            className="btn btn-primary"
            disabled={reviewRating === 0 || !reviewComment.trim() || reviewMutation.isPending}
            onClick={() => reviewMutation.mutate()}
          >
            {reviewMutation.isPending ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      )}
    </div>
  );
};

const ServiceBookingList = () => {
  const { user } = useAuth();

  const { data: bookingsData, isLoading } = useQuery({
    queryKey: ['my-service-bookings'],
    queryFn: async () => {
      const response = await serviceBookingApi.list();
      return response.data;
    },
  });

  if (isLoading) return <div className="loading">Loading service bookings...</div>;

  const bookings = bookingsData?.results || [];

  return (
    <div className="booking-list">
      <h1>My Service Bookings</h1>
      {bookings.length > 0 ? (
        <div className="bookings-grid">
          {bookings.map((booking) => (
            <ServiceBookingCard key={booking.id} booking={booking} currentUserId={user?.id} />
          ))}
        </div>
      ) : (
        <p className="no-bookings">No service bookings found.</p>
      )}
    </div>
  );
};

export default ServiceBookingList;
