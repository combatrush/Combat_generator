import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  logout: async () => {
    await api.post('/auth/logout');
  }
};

export const animationAPI = {
  getAnimations: async () => {
    const response = await api.get('/animations');
    return response.data;
  },
  saveAnimation: async (animationData: any) => {
    const response = await api.post('/animations', animationData);
    return response.data;
  }
};

export default api;
