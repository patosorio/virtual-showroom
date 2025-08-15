import axios, { AxiosInstance } from 'axios';
import { firebaseAuth } from '@/lib/firebase/auth';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await firebaseAuth.getIdToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      console.error('Server error:', error.response?.data || error.message);
      toast.error('Server error. Please check if the backend is running.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else if (error.code === 'ERR_NETWORK') {
      console.error('Network error:', error.message);
      toast.error('Cannot connect to server. Please check if the backend is running.');
    }
    return Promise.reject(error);
  }
);

export default apiClient;