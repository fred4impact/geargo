import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { profileApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user, refreshUser } = useAuth();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    bio: user?.bio || '',
    phone: user?.phone || '',
    location: user?.location || '',
    membership_tier: user?.membership_tier || 'casual',
  });

  const updateMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await profileApi.updateMe(data);
      return response.data;
    },
    onSuccess: () => {
      refreshUser();
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  if (!user) return <div className="loading">Loading profile...</div>;

  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1>My Profile</h1>
        
        {!isEditing ? (
          <div className="profile-view">
            <div className="profile-header">
              <h2>{user.full_name}</h2>
              <span className="membership-badge">{user.membership_tier}</span>
            </div>
            
            <div className="profile-info">
              <div className="info-item">
                <strong>Email:</strong> {user.user.email}
              </div>
              <div className="info-item">
                <strong>Phone:</strong> {user.phone || 'Not provided'}
              </div>
              <div className="info-item">
                <strong>Location:</strong> {user.location || 'Not provided'}
              </div>
              <div className="info-item">
                <strong>Bio:</strong> {user.bio || 'No bio yet'}
              </div>
              <div className="info-item">
                <strong>User Type:</strong>{' '}
                {user.is_owner && user.is_renter
                  ? 'Owner & Renter'
                  : user.is_owner
                  ? 'Owner'
                  : 'Renter'}
              </div>
            </div>
            
            <div className="form-actions">
              <button onClick={() => setIsEditing(true)} className="btn btn-primary">
                Edit Profile
              </button>
              <Link to="/kyc" className="btn btn-secondary">
                Verify Identity
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="bio">Bio</label>
              <textarea
                id="bio"
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                rows={4}
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                type="text"
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                type="text"
                id="location"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="membership_tier">Membership Tier</label>
              <select
                id="membership_tier"
                value={formData.membership_tier}
                onChange={(e) =>
                  setFormData({ ...formData, membership_tier: e.target.value as any })
                }
              >
                <option value="casual">Casual</option>
                <option value="frequent">Frequent</option>
                <option value="premium">Premium</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Profile;
