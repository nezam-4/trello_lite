import { defineStore } from 'pinia';
import api from '../api';

export const useInvitationsStore = defineStore('invitations', {
  state: () => ({
    invitations: []
  }),
  actions: {
    async fetchInvitations() {
      try {
        const res = await api.get('/boards/invitations/');
        this.invitations = res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async respondInvitation(id, action = 'accept') {
      // action: 'accept' or 'reject'
      try {
        const res = await api.post(`/boards/invitations/${id}/respond/`, { action });
        // remove from list after response
        this.invitations = this.invitations.filter(inv => inv.id !== id);
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    }
  }
});
