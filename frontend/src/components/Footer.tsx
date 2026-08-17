import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          <div className="footer-block">
            <h4 className="footer-heading">Contact</h4>
            <ul className="footer-links">
              <li><a href="/#contact">Contact Us</a></li>
              <li><a href="/#about">About Us</a></li>
              <li><span className="footer-muted">We&apos;re here to help!</span></li>
            </ul>
          </div>
          <div className="footer-block">
            <h4 className="footer-heading">Information</h4>
            <ul className="footer-links">
              <li><Link to="/items">Browse Items</Link></li>
              <li><a href="/#shipping">Shipping & Returns</a></li>
              <li><a href="/#privacy">Privacy Policy</a></li>
              <li><a href="/#terms">Terms & Conditions</a></li>
            </ul>
          </div>
          <div className="footer-block">
            <h4 className="footer-heading">GearGo</h4>
            <p className="footer-tagline">
              Rent equipment, book services, and connect with gear owners. Specialist advice, fast service.
            </p>
          </div>
        </div>
        <div className="footer-bottom">
          <p className="footer-copy">&copy; {new Date().getFullYear()} GearGo. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
