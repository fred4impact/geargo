import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { bookingApi } from '../api/endpoints';
import './BookingList.css';

const BookingList = () => {
  const { data: bookingsData, isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: async () => {
      const response = await bookingApi.list();
      return response.data;
    },
  });

  if (isLoading) return <div className="loading">Loading bookings...</div>;

  const bookings = bookingsData?.results || [];

  return (
    <div className="booking-list">
      <h1>My Bookings</h1>
      {bookings.length > 0 ? (
        <div className="bookings-grid">
          {bookings.map((booking) => (
            <Link key={booking.id} to={`/bookings/${booking.id}`} className="booking-card">
              <h3>{booking.item.title}</h3>
              <p className="booking-dates">
                {new Date(booking.start_date).toLocaleDateString()} -{' '}
                {new Date(booking.end_date).toLocaleDateString()}
              </p>
              <p className="booking-amount">Total: ${booking.total_amount}</p>
              <div className="booking-status">
                <span className={`status-badge ${booking.status}`}>{booking.status}</span>
                <span className={`status-badge ${booking.payment_status}`}>
                  {booking.payment_status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <p className="no-bookings">No bookings found.</p>
      )}
    </div>
  );
};

export default BookingList;
