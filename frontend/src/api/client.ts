import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';

// Always use relative path when served from nginx (production/Docker)
// This allows nginx to proxy the requests correctly
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Log API URL for debugging
console.log('API Base URL:', API_BASE_URL);
console.log('Environment:', import.meta.env.MODE);

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Important for session-based auth
    });

    // Request interceptor to add auth token if available
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  get instance() {
    return this.client;
  }

  // Auth methods
  async login(username: string, password: string) {
    // Try token auth first, fallback to session auth
    try {
      const response = await this.client.post('/auth/token/', {
        username,
        password,
      });
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
      }
      return response.data;
    } catch (error: any) {
      // If token auth fails, try session-based login
      // This will use Django's session authentication
      const sessionResponse = await this.client.post('/accounts/login/', {
        login: username,
        password: password,
      });
      return sessionResponse.data;
    }
  }

  logout() {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }
}

export const apiClient = new ApiClient();
export default apiClient.instance;
