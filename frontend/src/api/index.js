import axios from 'axios';
import router from '../router';
import { useErrorsStore } from '../stores/errors';

const apiClient = axios.create({
  // Use 127.0.0.1 as default to prevent IPv6 localhost resolution issues in some browsers
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const errorsStore = useErrorsStore();
    if (error.response?.data) {
      const msg = typeof error.response.data === 'string' ? error.response.data : error.response.data.detail || JSON.stringify(error.response.data);
      errorsStore.setError(msg);
    } else {
      errorsStore.setError(error.message || 'خطای ناشناخته');
    }

    if (status === 401) {
      // Clean stored tokens
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      // Redirect to login if not already there
      if (router.currentRoute.value.name !== 'login') {
        router.push({ name: 'login' });
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
