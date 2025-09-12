import { defineStore } from 'pinia';
import api from '../api';
import { useErrorsStore } from './errors';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null
  }),
  getters: {
    isAuthenticated: (state) => !!state.access
  },
  actions: {
    async login(email, password) {
      try {
        console.log('LOGIN URL Test →', api.defaults.baseURL + '/users/auth/token/');
        const response = await api.post('/users/auth/token/', { email, password });
        this.access = response.data.access;
        this.refresh = response.data.refresh;
        localStorage.setItem('access', this.access);
        localStorage.setItem('refresh', this.refresh);
        console.log('Login successful, fetching current user...');
        await this.fetchCurrentUser();
        return true;
      } catch (err) {
        console.error('Login error:', err);
        // Extract server-provided message if available
        const errorsStore = useErrorsStore();
        let message = 'خطا در ورود';
        const data = err?.response?.data;
        if (data) {
          if (typeof data === 'string') {
            message = data;
          } else if (data.detail) {
            message = data.detail;
          } else if (data.non_field_errors) {
            message = Array.isArray(data.non_field_errors) ? data.non_field_errors.join('، ') : String(data.non_field_errors);
          } else if (data.error) {
            message = Array.isArray(data.error) ? data.error.join('، ') : String(data.error);
          } else if (typeof data === 'object') {
            // Flatten first few field errors
            const parts = [];
            for (const [key, val] of Object.entries(data)) {
              const text = Array.isArray(val) ? val.join('، ') : String(val);
              parts.push(`${key}: ${text}`);
              if (parts.length >= 3) break;
            }
            if (parts.length) {
              message = parts.join(' | ');
            } else {
              message = JSON.stringify(data);
            }
          }
        } else if (err?.message) {
          message = err.message;
        }
        errorsStore.setError(message);
        return false;
      }
    },
    async logout() {
      try {
        // Call backend logout endpoint to blacklist refresh token
        if (this.refresh) {
          await api.post('/users/auth/logout/', { 
            refresh_token: this.refresh 
          });
        }
      } catch (error) {
        console.error('Logout API error:', error);
        // Continue with local logout even if API call fails
      }
      
      // Clear local storage and state
      this.access = null;
      this.refresh = null;
      this.user = null;
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
    },
    async fetchCurrentUser() {
      if (!this.access) return;
      try {
        console.log('Fetching current user...');
        const res = await api.get('/users/current/');
        console.log('Current user response:', res.data);
        this.user = res.data;
      } catch (e) {
        console.error('Error fetching current user:', e);
      }
    },
    async fetchProfile() {
      if (!this.access) throw 'Not authenticated';
      try {
        const res = await api.get('/users/profile/');
        // res.data = {user: {...}, profile: {...}}
        this.user = res.data.user;
        this.user.profile = res.data.profile;
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async updateProfile(data) {
      if (!this.access) throw 'Not authenticated';
      try {
        const config = data instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {};
        const res = await api.patch('/users/profile/', data, config);
        // res.data = {user, profile}
        this.user = res.data.user;
        this.user.profile = res.data.profile;
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async changePassword(oldPassword, newPassword1, newPassword2) {
      if (!this.access) throw 'Not authenticated';
      try {
        const payload = { old_password: oldPassword, new_password1: newPassword1, new_password2: newPassword2 };
        await api.post('/users/change-password/', payload);
        return true;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    }
  }
});
