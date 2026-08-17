import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceApi, serviceBookingApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './ServiceDetail.css';

const ServiceDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: service, isLoading } = useQuery({
    queryKey: ['service', id],
    queryFn: async () => {
      const response = await serviceApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const bookingMutation = useMutation({
    mutationFn: async (data: { start_time: string; end_time: string; notes: string }) => {
      const response = await serviceBookingApi.create({
        ...data,
        service_id: id!,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-service-bookings'] });
      navigate('/service-bookings');
    },
  });

  const handleBooking = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    const formData = new FormData(e.currentTarget);
    bookingMutation.mutate({
      start_time: formData.get('start_time') as string,
      end_time: formData.get('end_time') as string,
      notes: (formData.get('notes') as string) || '',
    });
  };

  if (isLoading) {
    return (
      <div className="service-detail">
        <div className="service-detail-container">
          <div className="loading">Loading service details...</div>
        </div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="service-detail">
        <div className="service-detail-container">
          <div className="error">Service not found</div>
        </div>
      </div>
    );
  }

  const isProvider = user?.user?.id === service.provider?.user?.id;
  const now = new Date().toISOString().slice(0, 16);

  return (
    <div className="service-detail">
      <div className="service-detail-container">
        <div className="service-info">
          <span className="category-badge">{service.category?.name}</span>

          <h1>{service.title}</h1>
          <p className="service-rate">
            ${service.hourly_rate}
            <span className="unit">/hour</span>
          </p>
          <p className="service-location">{service.location}</p>
          <p className="service-description">
            {service.description || 'No description available.'}
          </p>

          <div className="service-meta">
            <div className="meta-item">
              <strong>Experience</strong>
              <span>{service.experience_years} {service.experience_years === 1 ? 'year' : 'years'}</span>
            </div>
            <div className="meta-item">
              <strong>Availability</strong>
              <span className={`status-badge ${service.available ? 'available' : 'unavailable'}`}>
                {service.available ? 'Available' : 'Unavailable'}
              </span>
            </div>
            {service.average_rating > 0 && (
              <div className="meta-item">
                <strong>Rating</strong>
                <span>
                  {service.average_rating.toFixed(1)} ({service.total_reviews} {service.total_reviews === 1 ? 'review' : 'reviews'})
                </span>
              </div>
            )}
            <div className="meta-item">
              <strong>Provider</strong>
              <span>{service.provider?.full_name || service.provider?.user?.first_name || 'GearGo Provider'}</span>
            </div>
            {service.certifications && (
              <div className="meta-item meta-item-full">
                <strong>Certifications</strong>
                <span>{service.certifications}</span>
              </div>
            )}
          </div>

          {!isProvider && service.available && (
            <form onSubmit={handleBooking} className="booking-form">
              <h3>Book This Service</h3>
              <div className="form-group">
                <label htmlFor="start_time">Start Time</label>
                <input type="datetime-local" id="start_time" name="start_time" required min={now} />
              </div>
              <div className="form-group">
                <label htmlFor="end_time">End Time</label>
                <input type="datetime-local" id="end_time" name="end_time" required min={now} />
              </div>
              <div className="form-group">
                <label htmlFor="notes">Notes (optional)</label>
                <textarea id="notes" name="notes" rows={3} placeholder="Anything the provider should know?" />
              </div>
              <button type="submit" className="btn btn-primary" disabled={bookingMutation.isPending}>
                {bookingMutation.isPending ? 'Booking...' : 'Book Now'}
              </button>
              {bookingMutation.isError && (
                <p className="booking-error">Couldn't create booking. Check your times and try again.</p>
              )}
            </form>
          )}

          {!isProvider && !service.available && (
            <div className="booking-unavailable">
              <h3>Currently Unavailable</h3>
              <p>This provider isn't taking bookings right now.</p>
            </div>
          )}

          {isProvider && (
            <div className="owner-actions">
              <Link to="/services/create" className="btn btn-secondary">
                List Another Service
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ServiceDetail;
