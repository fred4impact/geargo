import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import './Navbar.css';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/items?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/items');
    }
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-text">GearGo</span>
        </Link>

        <nav className="navbar-menu">
          <Link to="/items" className="navbar-link">
            Browse
          </Link>
          <Link to="/services" className="navbar-link">
            Services
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/items/create" className="navbar-link">
                List Item
              </Link>
              <Link to="/services/create" className="navbar-link">
                Offer Service
              </Link>
              <Link to="/bookings" className="navbar-link">
                My Bookings
              </Link>
              <Link to="/service-bookings" className="navbar-link">
                My Service Bookings
              </Link>
              {user?.user?.is_staff && (
                <Link to="/kyc/review" className="navbar-link">
                  KYC Review
                </Link>
              )}
              <NotificationBell />
              <Link to="/profile" className="navbar-link navbar-link-profile">
                {user?.full_name || 'Profile'}
              </Link>
              <button type="button" onClick={handleLogout} className="navbar-link navbar-btn-text">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">
                Login
              </Link>
              <Link to="/register" className="navbar-cta">
                Sign Up
              </Link>
            </>
          )}
        </nav>

        <form onSubmit={handleSearch} className="navbar-search">
          <input
            type="search"
            placeholder="Search items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="navbar-search-input"
            aria-label="Search items"
          />
          <button type="submit" className="navbar-search-btn" aria-label="Search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
          </button>
        </form>
      </div>
    </header>
  );
};

export default Navbar;
