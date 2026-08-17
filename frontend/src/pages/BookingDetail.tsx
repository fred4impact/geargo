import { useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingApi, reviewApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import StarRatingInput from '../components/StarRatingInput';
import './BookingDetail.css';

const BookingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const paymentResult = searchParams.get('payment');
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');

  const { data: booking, isLoading, refetch } = useQuery({
    queryKey: ['booking', id],
    queryFn: async () => {
      const response = await bookingApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const { data: existingReview } = useQuery({
    queryKey: ['review', id],
    queryFn: async () => {
      const response = await reviewApi.list({ booking: id! });
      return response.data.results[0] ?? null;
    },
    enabled: !!id && booking?.status === 'completed',
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

  const confirmMutation = useMutation({
    mutationFn: async () => {
      const response = await bookingApi.confirm(id!);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', id] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: async () => {
      const response = await bookingApi.complete(id!);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', id] });
    },
  });

  const reviewMutation = useMutation({
    mutationFn: async () => {
      const response = await reviewApi.create({
        booking_id: id!,
        rating: reviewRating,
        comment: reviewComment,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review', id] });
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
  const canPay =
    isRenter && booking.payment_status === 'pending' && !['cancelled', 'completed'].includes(booking.status);
  const canCancel = (isRenter || isOwner) && ['pending', 'confirmed'].includes(booking.status);
  const canComplete = isOwner && ['confirmed', 'active'].includes(booking.status);
  const canConfirm = isOwner && booking.status === 'pending';
  const canReview = isRenter && booking.status === 'completed' && !existingReview;

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

        {canConfirm && (
          <button
            className="btn btn-primary confirm-button"
            onClick={() => confirmMutation.mutate()}
            disabled={confirmMutation.isPending}
          >
            {confirmMutation.isPending ? 'Confirming...' : 'Confirm Booking'}
          </button>
        )}
        {confirmMutation.isError && (
          <p className="payment-error">Couldn't confirm booking. Please try again.</p>
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

        {canComplete && (
          <button
            className="btn btn-secondary complete-button"
            onClick={() => completeMutation.mutate()}
            disabled={completeMutation.isPending}
          >
            {completeMutation.isPending ? 'Marking complete...' : 'Mark as Completed'}
          </button>
        )}
        {completeMutation.isError && (
          <p className="payment-error">Couldn't mark booking as completed. Please try again.</p>
        )}

        {existingReview && (
          <div className="review-summary">
            <h3>Your Review</h3>
            <div className="review-stars" aria-label={`${existingReview.rating} out of 5 stars`}>
              {'★'.repeat(existingReview.rating)}{'☆'.repeat(5 - existingReview.rating)}
            </div>
            <p>{existingReview.comment}</p>
          </div>
        )}

        {canReview && (
          <div className="review-form">
            <h3>Leave a Review</h3>
            <StarRatingInput value={reviewRating} onChange={setReviewRating} />
            <textarea
              placeholder="How was this rental?"
              value={reviewComment}
              onChange={(e) => setReviewComment(e.target.value)}
              rows={3}
            />
            <button
              type="button"
              className="btn btn-primary"
              disabled={reviewRating === 0 || !reviewComment.trim() || reviewMutation.isPending}
              onClick={() => reviewMutation.mutate()}
            >
              {reviewMutation.isPending ? 'Submitting...' : 'Submit Review'}
            </button>
            {reviewMutation.isError && (
              <p className="payment-error">Couldn't submit review. Please try again.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookingDetail;
