import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (name: string, email: string, password: string) =>
    api.post('/auth/register', { name, email, password }),

  logout: () => api.post('/auth/logout'),
};

export const candidatesAPI = {
  list: (params: {
    page?: number;
    page_size?: number;
    status?: string;
    role_applied?: string;
    skill?: string;
    keyword?: string;
  }) => api.get('/candidates/', { params }),

  getById: (id: number) => api.get(`/candidates/${id}`),

  createScore: (id: number, data: { category: string; score: number; note?: string }) =>
    api.post(`/candidates/${id}/scores`, data),

  generateSummary: (id: number) => api.post(`/candidates/${id}/summary`),

  streamUpdates: (id: number) => {
    const token = localStorage.getItem('token');
    const url = new URL(`${API_BASE_URL}/candidates/${id}/stream`);
    if (token) {
      url.searchParams.set('token', token);
    }
    return new EventSource(url.toString());
  },
};

export default api;
