import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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
