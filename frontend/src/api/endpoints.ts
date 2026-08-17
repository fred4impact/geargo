import api from './client';
import type {
  Profile,
  Category,
  Item,
  ItemImage,
  Booking,
  Review,
  Service,
  ServiceCategory,
  ServiceBooking,
  ServiceReview,
  KYCVerification,
  Notification,
  PaginatedResponse,
} from '../types';

// Profile endpoints
export const profileApi = {
  getMe: () => api.get<Profile>('/profiles/me/'),
  updateMe: (data: Partial<Profile>) => api.patch<Profile>('/profiles/update_me/', data),
  getProfile: (id: number) => api.get<Profile>(`/profiles/${id}/`),
};

// Category endpoints
export const categoryApi = {
  list: () => api.get<PaginatedResponse<Category>>('/categories/'),
  get: (id: number) => api.get<Category>(`/categories/${id}/`),
};

// Item endpoints
export const itemApi = {
  list: (params?: {
    category?: number;
    available?: boolean;
    min_price?: number;
    max_price?: number;
    search?: string;
    page?: number;
  }) => api.get<PaginatedResponse<Item>>('/items/', { params }),
  get: (id: string) => api.get<Item>(`/items/${id}/`),
  create: (data: Partial<Item>) => api.post<Item>('/items/', data),
  update: (id: string, data: Partial<Item>) => api.patch<Item>(`/items/${id}/`, data),
  delete: (id: string) => api.delete(`/items/${id}/`),
  getRecommendations: () => api.get<Item[]>('/items/recommendations/'),
  getPricingSuggestion: (id: string) => api.get<{ suggested_price: number }>(`/items/${id}/pricing_suggestion/`),
};

// Item image endpoints
export const itemImageApi = {
  upload: (itemId: string, image: File, isPrimary: boolean) => {
    const formData = new FormData();
    formData.append('item', itemId);
    formData.append('image', image);
    formData.append('is_primary', String(isPrimary));
    return api.post<ItemImage>('/item-images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: number) => api.delete(`/item-images/${id}/`),
};

// Booking endpoints
export const bookingApi = {
  list: (params?: { status?: string; page?: number }) =>
    api.get<PaginatedResponse<Booking>>('/bookings/', { params }),
  get: (id: string) => api.get<Booking>(`/bookings/${id}/`),
  create: (data: Partial<Booking> & { item_id?: string }) => api.post<Booking>('/bookings/', data),
  confirm: (id: string) => api.post<Booking>(`/bookings/${id}/confirm/`),
  cancel: (id: string) => api.post<Booking>(`/bookings/${id}/cancel/`),
  complete: (id: string) => api.post<Booking>(`/bookings/${id}/complete/`),
  createCheckoutSession: (id: string) =>
    api.post<{ checkout_url: string; session_id: string }>(`/bookings/${id}/create_checkout_session/`),
};

// Review endpoints
export const reviewApi = {
  list: (params?: { item?: string; booking?: string; rating?: number }) =>
    api.get<PaginatedResponse<Review>>('/reviews/', { params }),
  create: (data: { booking_id: string; rating: number; comment: string }) =>
    api.post<Review>('/reviews/', data),
};

// Service Category endpoints
export const serviceCategoryApi = {
  list: () => api.get<ServiceCategory[]>('/service-categories/'),
  get: (id: number) => api.get<ServiceCategory>(`/service-categories/${id}/`),
};

// Service endpoints
export const serviceApi = {
  list: (params?: { category?: number; available?: boolean; search?: string }) =>
    api.get<PaginatedResponse<Service>>('/services/', { params }),
  get: (id: string) => api.get<Service>(`/services/${id}/`),
  create: (data: Partial<Service>) => api.post<Service>('/services/', data),
  update: (id: string, data: Partial<Service>) => api.patch<Service>(`/services/${id}/`, data),
};

// Service Booking endpoints
export const serviceBookingApi = {
  list: (params?: { status?: string }) =>
    api.get<PaginatedResponse<ServiceBooking>>('/service-bookings/', { params }),
  get: (id: string) => api.get<ServiceBooking>(`/service-bookings/${id}/`),
  create: (data: Partial<ServiceBooking> & { service_id?: string }) =>
    api.post<ServiceBooking>('/service-bookings/', data),
  update: (id: string, data: Partial<ServiceBooking>) =>
    api.patch<ServiceBooking>(`/service-bookings/${id}/`, data),
  complete: (id: string) => api.post<ServiceBooking>(`/service-bookings/${id}/complete/`),
};

// Service Review endpoints
export const serviceReviewApi = {
  list: (params?: { service?: string; booking?: string }) =>
    api.get<PaginatedResponse<ServiceReview>>('/service-reviews/', { params }),
  create: (data: { booking_id: string; rating: number; comment: string }) =>
    api.post<ServiceReview>('/service-reviews/', data),
};

// Notification endpoints
export const notificationApi = {
  list: () => api.get<PaginatedResponse<Notification>>('/notifications/'),
  unreadCount: () => api.get<{ unread_count: number }>('/notifications/unread_count/'),
  markRead: (id: string) => api.post<Notification>(`/notifications/${id}/mark_read/`),
  markAllRead: () => api.post<{ status: string }>('/notifications/mark_all_read/'),
};

// KYC endpoints
export const kycApi = {
  getMyStatus: () => api.get<KYCVerification | { status: string }>('/kyc/my_status/'),
  create: (data: FormData) => api.post<KYCVerification>('/kyc/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  get: (id: number) => api.get<KYCVerification>(`/kyc/${id}/`),
  list: () => api.get<PaginatedResponse<KYCVerification>>('/kyc/'),
  approve: (id: number) => api.post<KYCVerification>(`/kyc/${id}/approve/`),
  reject: (id: number, rejection_reason: string) =>
    api.post<KYCVerification>(`/kyc/${id}/reject/`, { rejection_reason }),
};
