// User and Profile types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

export interface Profile {
  id: number;
  user: User;
  bio: string;
  phone: string;
  location: string;
  membership_tier: 'casual' | 'frequent' | 'premium';
  is_owner: boolean;
  is_renter: boolean;
  full_name: string;
  created_at: string;
  updated_at: string;
}

// Category types
export interface Category {
  id: number;
  name: string;
  description: string;
  icon: string;
  created_at: string;
}

// Item types
export interface ItemImage {
  id: number;
  image: string;
  image_url: string;
  thumbnail_url: string;
  optimized_url: string;
  is_primary: boolean;
  created_at: string;
}

export interface Item {
  id: string;
  owner: Profile;
  category: Category;
  title: string;
  description: string;
  daily_price: string;
  condition: 'excellent' | 'good' | 'fair' | 'poor';
  availability_status: 'available' | 'rented' | 'maintenance' | 'unavailable';
  location: string;
  is_available: boolean;
  images: ItemImage[];
  average_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

// Booking types
export interface Booking {
  id: string;
  renter: Profile;
  item: Item;
  start_date: string;
  end_date: string;
  total_amount: string;
  status: 'pending' | 'confirmed' | 'active' | 'completed' | 'cancelled';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  payment_date: string | null;
  payment_transaction_id: string;
  duration_days: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Review types
export interface Review {
  id: number;
  reviewer: Profile;
  item: Item | null;
  booking: Booking | null;
  rating: number;
  comment: string;
  created_at: string;
}

// Service types
export interface ServiceCategory {
  id: number;
  name: string;
  description: string;
  icon: string;
  created_at: string;
}

export interface Service {
  id: string;
  provider: Profile;
  category: ServiceCategory;
  title: string;
  description: string;
  hourly_rate: string;
  available: boolean;
  location: string;
  experience_years: number;
  certifications: string;
  average_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

export interface ServiceBooking {
  id: string;
  service: Service;
  customer: Profile;
  start_time: string;
  end_time: string;
  total_hours: string;
  total_cost: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceReview {
  id: number;
  service: Service;
  customer: Profile;
  booking: ServiceBooking;
  rating: number;
  comment: string;
  created_at: string;
}

// KYC types
export interface KYCVerification {
  id: number;
  profile: Profile;
  legal_name: string;
  id_type: 'passport' | 'driver_license' | 'national_id' | 'other';
  id_number: string;
  id_document: string;
  id_document_url: string;
  status: 'pending' | 'approved' | 'rejected';
  verified_at: string | null;
  rejection_reason: string;
  is_approved: boolean;
  is_pending: boolean;
  is_rejected: boolean;
  created_at: string;
  updated_at: string;
}

// Notification types
export interface Notification {
  id: string;
  notification_type:
    | 'booking_created'
    | 'booking_confirmed'
    | 'booking_cancelled'
    | 'booking_reminder'
    | 'payment_received'
    | 'item_reviewed'
    | 'system_message';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  related_booking: string | null;
  related_item: string | null;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
