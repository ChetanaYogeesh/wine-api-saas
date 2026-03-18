import axios from 'axios';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

let routerInstance: any = null;

export const setRouter = (router: any) => {
  routerInstance = router;
};

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        if (routerInstance) {
          routerInstance.push('/login');
        } else {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const auth = {
  register: async (email: string, password: string, fullName: string) => {
    const response = await api.post('/register', { email, password, full_name: fullName });
    return response.data;
  },
  
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  forgotPassword: async (email: string) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/auth/reset-password', { token, new_password: newPassword });
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', { 
      current_password: currentPassword, 
      new_password: newPassword 
    });
    return response.data;
  },
};

export const user = {
  getProfile: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
  
  updateProfile: async (data: { full_name?: string; email?: string }) => {
    const response = await api.put('/users/me', data);
    return response.data;
  },
};

export const subscription = {
  get: async () => {
    const response = await api.get('/subscription');
    return response.data;
  },
  
  createCheckout: async (priceId: string) => {
    const response = await api.post('/subscription/checkout', { price_id: priceId });
    return response.data;
  },
  
  createPortal: async () => {
    const response = await api.post('/subscription/portal');
    return response.data;
  },
  
  cancel: async () => {
    const response = await api.post('/subscription/cancel');
    return response.data;
  },
};

export const invoices = {
  list: async () => {
    const response = await api.get('/invoices');
    return response.data;
  },
};

export const apiKeys = {
  list: async () => {
    const response = await api.get('/api-keys');
    return response.data;
  },
  
  create: async (name: string, tier: string = 'free') => {
    const response = await api.post('/api-keys', { name, tier });
    return response.data;
  },
};

export const usage = {
  getStats: async () => {
    const response = await api.get('/usage');
    return response.data;
  },
};

export const tiers = {
  list: async () => {
    const response = await api.get('/tiers');
    return response.data;
  },
};

export default api;
