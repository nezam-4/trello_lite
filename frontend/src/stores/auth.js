import { defineStore } from 'pinia';
import api from '../api';

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
        await this.fetchCurrentUser();
        return true;
      } catch (err) {
        console.error(err);
        return false;
      }
    },
    async logout() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
    },
    async fetchCurrentUser() {
      if (!this.access) return;
      try {
        const res = await api.get('/users/current/');
        this.user = res.data;
      } catch (e) {
        console.error(e);
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
