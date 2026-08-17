import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { bookingApi, itemApi } from '../api/endpoints';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();

  const { data: myItems } = useQuery({
    queryKey: ['my-items'],
    queryFn: async () => {
      const response = await itemApi.list({ page: 1 });
      return response.data.results.filter((item) => item.owner.id === user?.id);
    },
    enabled: !!user,
  });

  const { data: bookings } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: async () => {
      const response = await bookingApi.list();
      return response.data.results;
    },
    enabled: !!user,
  });

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome, {user?.full_name || 'User'}!</h1>
        <p className="membership-badge">{user?.membership_tier || 'casual'}</p>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>My Items</h3>
          <p className="stat-number">{myItems?.length || 0}</p>
          <Link to="/items/create" className="stat-link">
            List New Item
          </Link>
        </div>
        <div className="stat-card">
          <h3>Active Bookings</h3>
          <p className="stat-number">
            {bookings?.filter((b) => b.status === 'active' || b.status === 'confirmed').length || 0}
          </p>
          <Link to="/bookings" className="stat-link">
            View All
          </Link>
        </div>
        <div className="stat-card">
          <h3>Total Bookings</h3>
          <p className="stat-number">{bookings?.length || 0}</p>
        </div>
      </div>

      <div className="dashboard-sections">
        <section className="dashboard-section">
          <h2>My Items</h2>
          {myItems && myItems.length > 0 ? (
            <div className="items-list">
              {myItems.map((item) => (
                <Link key={item.id} to={`/items/${item.id}`} className="item-card">
                  {item.images && item.images.length > 0 && (
                    <img
                      src={item.images[0].thumbnail_url || item.images[0].image_url}
                      alt={item.title}
                      className="item-image"
                    />
                  )}
                  <div className="item-info">
                    <h3>{item.title}</h3>
                    <p>${item.daily_price}/day</p>
                    <span className={`status-badge ${item.availability_status}`}>
                      {item.availability_status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p>You haven't listed any items yet.</p>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Recent Bookings</h2>
          {bookings && bookings.length > 0 ? (
            <div className="bookings-list">
              {bookings.slice(0, 5).map((booking) => (
                <div key={booking.id} className="booking-card">
                  <h3>{booking.item.title}</h3>
                  <p>
                    {new Date(booking.start_date).toLocaleDateString()} -{' '}
                    {new Date(booking.end_date).toLocaleDateString()}
                  </p>
                  <p>Total: ${booking.total_amount}</p>
                  <span className={`status-badge ${booking.status}`}>{booking.status}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>No bookings yet.</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
