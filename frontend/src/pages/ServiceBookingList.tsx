import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceBookingApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './BookingList.css';

const ServiceBookingList = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: bookingsData, isLoading } = useQuery({
    queryKey: ['my-service-bookings'],
    queryFn: async () => {
      const response = await serviceBookingApi.list();
      return response.data;
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await serviceBookingApi.update(id, { status: 'cancelled' });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-service-bookings'] });
    },
  });

  if (isLoading) return <div className="loading">Loading service bookings...</div>;

  const bookings = bookingsData?.results || [];

  return (
    <div className="booking-list">
      <h1>My Service Bookings</h1>
      {bookings.length > 0 ? (
        <div className="bookings-grid">
          {bookings.map((booking) => {
            const isCustomer = booking.customer.id === user?.id;
            const canCancel = isCustomer && ['pending', 'confirmed'].includes(booking.status);
            return (
              <div key={booking.id} className="booking-card">
                <h3>{booking.service.title}</h3>
                <p className="booking-dates">
                  {new Date(booking.start_time).toLocaleString()} —{' '}
                  {new Date(booking.end_time).toLocaleString()}
                </p>
                <p className="booking-amount">Total: ${booking.total_cost}</p>
                <div className="booking-status">
                  <span className={`status-badge ${booking.status}`}>{booking.status}</span>
                </div>
                {canCancel && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ marginTop: '1rem' }}
                    disabled={cancelMutation.isPending}
                    onClick={() => cancelMutation.mutate(booking.id)}
                  >
                    Cancel Booking
                  </button>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="no-bookings">No service bookings found.</p>
      )}
    </div>
  );
};

export default ServiceBookingList;
