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

export const webhooks = {
  list: async () => {
    const response = await api.get('/webhooks');
    return response.data;
  },
  
  create: async (data: { url: string; events: string }) => {
    const response = await api.post('/webhooks', data);
    return response.data;
  },
  
  get: async (id: number) => {
    const response = await api.get(`/webhooks/${id}`);
    return response.data;
  },
  
  update: async (id: number, data: { url?: string; events?: string; is_active?: boolean }) => {
    const response = await api.put(`/webhooks/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    const response = await api.delete(`/webhooks/${id}`);
    return response.data;
  },
};

export const teams = {
  list: async () => {
    const response = await api.get('/teams');
    return response.data;
  },
  
  create: async (name: string) => {
    const response = await api.post('/teams', { name });
    return response.data;
  },
  
  get: async (id: number) => {
    const response = await api.get(`/teams/${id}`);
    return response.data;
  },
  
  delete: async (id: number) => {
    const response = await api.delete(`/teams/${id}`);
    return response.data;
  },
  
  addMember: async (teamId: number, email: string, role: string = 'member') => {
    const response = await api.post(`/teams/${teamId}/members`, { email, role });
    return response.data;
  },
  
  removeMember: async (teamId: number, memberId: number) => {
    const response = await api.delete(`/teams/${teamId}/members/${memberId}`);
    return response.data;
  },
  
  updateMember: async (teamId: number, memberId: number, role: string) => {
    const response = await api.put(`/teams/${teamId}/members/${memberId}`, { role });
    return response.data;
  },
};

export const analytics = {
  get: async (days: number = 30) => {
    const response = await api.get(`/analytics?days=${days}`);
    return response.data;
  },
  
  export: async (format: 'json' | 'csv' = 'json') => {
    const response = await api.get(`/analytics/export?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const usageAlerts = {
  list: async () => {
    const response = await api.get('/usage/alerts');
    return response.data;
  },
  
  create: async (data: { threshold_percent: number; email: string }) => {
    const response = await api.post('/usage/alerts', data);
    return response.data;
  },
  
  delete: async (id: number) => {
    const response = await api.delete(`/usage/alerts/${id}`);
    return response.data;
  },
};

export const whiteLabel = {
  get: async () => {
    const response = await api.get('/white-label');
    return response.data;
  },
  
  create: async (data: {
    company_name?: string;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    custom_domain?: string;
    email_footer?: string;
  }) => {
    const response = await api.post('/white-label', data);
    return response.data;
  },
  
  update: async (data: {
    company_name?: string;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    email_footer?: string;
  }) => {
    const response = await api.put('/white-label', data);
    return response.data;
  },
  
  delete: async () => {
    const response = await api.delete('/white-label');
    return response.data;
  },
  
  verifyDomain: async (domain: string) => {
    const response = await api.get(`/white-label/verify-domain?domain=${domain}`);
    return response.data;
  },
};

export default api;
