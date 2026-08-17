import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itemApi, itemImageApi, bookingApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './ItemDetail.css';

const ItemDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const { data: item, isLoading } = useQuery({
    queryKey: ['item', id],
    queryFn: async () => {
      const response = await itemApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const uploadImageMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await itemImageApi.upload(id!, file, !item?.images?.length);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['item', id] });
    },
  });

  const handleAddPhotos = (e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files ?? []).forEach((file) => uploadImageMutation.mutate(file));
    e.target.value = '';
  };

  const bookingMutation = useMutation({
    mutationFn: async (data: { start_date: string; end_date: string }) => {
      const response = await bookingApi.create({
        ...data,
        item_id: id!,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] });
      navigate('/bookings');
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
      start_date: formData.get('start_date') as string,
      end_date: formData.get('end_date') as string,
    });
  };

  if (isLoading) {
    return (
      <div className="item-detail">
        <div className="item-detail-container">
          <div className="loading">Loading item details...</div>
        </div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="item-detail">
        <div className="item-detail-container">
          <div className="error">Item not found</div>
        </div>
      </div>
    );
  }

  const isOwner = user?.user?.id === item.owner?.user?.id;

  return (
    <div className="item-detail">
      <div className="item-detail-container">
        <div className="item-images">
          {item.images?.length > 0 ? (
            <>
              <img
                src={item.images[selectedImageIndex]?.optimized_url || item.images[selectedImageIndex]?.image_url}
                alt={item.title}
                className="main-image"
              />
              {item.images.length > 1 && (
                <div className="image-thumbnails">
                  {item.images.map((image, index) => (
                    <button
                      key={image.id}
                      type="button"
                      className={`image-thumbnail ${index === selectedImageIndex ? 'active' : ''}`}
                      onClick={() => setSelectedImageIndex(index)}
                      aria-label={`View photo ${index + 1}`}
                    >
                      <img src={image.thumbnail_url || image.image_url} alt="" />
                    </button>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="no-image">No image available</div>
          )}
        </div>

        <div className="item-details">
          <span className="category-badge">{item.category?.name}</span>

          <h1>{item.title}</h1>
          <p className="item-price">
            ${item.daily_price}
            <span className="unit">/day</span>
          </p>
          <p className="item-location">{item.location}</p>
          <p className="item-description">
            {item.description || 'No description available.'}
          </p>

          <div className="item-meta">
            <div className="meta-item">
              <strong>Condition</strong>
              <span style={{ textTransform: 'capitalize' }}>{item.condition}</span>
            </div>
            <div className="meta-item">
              <strong>Availability</strong>
              <span className={`status-badge ${item.availability_status}`} style={{ display: 'inline-block', textTransform: 'capitalize' }}>
                {item.availability_status}
              </span>
            </div>
            {item.average_rating > 0 && (
              <div className="meta-item">
                <strong>Rating</strong>
                <span>
                  {item.average_rating.toFixed(1)} ({item.total_reviews} {item.total_reviews === 1 ? 'review' : 'reviews'})
                </span>
              </div>
            )}
            {item.owner && (
              <div className="meta-item">
                <strong>Owner</strong>
                <span>{item.owner.full_name || item.owner.user?.first_name || 'GearGo User'}</span>
              </div>
            )}
          </div>

          {!isOwner && item.is_available && (
            <form onSubmit={handleBooking} className="booking-form">
              <h3>Rent This Item</h3>
              <div className="form-group">
                <label htmlFor="start_date">Start Date</label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div className="form-group">
                <label htmlFor="end_date">End Date</label>
                <input
                  type="date"
                  id="end_date"
                  name="end_date"
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={bookingMutation.isPending}>
                {bookingMutation.isPending ? 'Processing...' : 'Book Now'}
              </button>
            </form>
          )}

          {!isOwner && !item.is_available && (
            <div className="booking-unavailable">
              <h3>Currently Unavailable</h3>
              <p>This item is not available for booking at the moment.</p>
            </div>
          )}

          {isOwner && (
            <div className="owner-actions">
              <label htmlFor="add-photos" className="btn btn-secondary">
                {uploadImageMutation.isPending ? 'Uploading...' : 'Add Photos'}
              </label>
              <input
                type="file"
                id="add-photos"
                accept="image/*"
                multiple
                onChange={handleAddPhotos}
                disabled={uploadImageMutation.isPending}
                style={{ display: 'none' }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ItemDetail;
