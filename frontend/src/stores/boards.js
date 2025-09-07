import { defineStore } from 'pinia';
import api from '../api';

export const useBoardsStore = defineStore('boards', {
  state: () => ({
    boards: [],
    currentBoard: null
  }),
  actions: {
    async fetchBoards() {
      try {
        const res = await api.get('/boards/');
        this.boards = res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async createBoard(data) {
      try {
        const payload = typeof data === 'string' ? { title: data } : data;
        const res = await api.post('/boards/', payload);
        this.boards.push(res.data);
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async updateBoard(id, data) {
      try {
        const res = await api.patch(`/boards/${id}/`, data);
        // Update local list
        const idx = this.boards.findIndex(b => b.id === id);
        if (idx !== -1) this.boards[idx] = res.data;
        // if editing current board
        if (this.currentBoard && this.currentBoard.id === id) this.currentBoard = res.data;
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async deleteBoard(id) {
      try {
        await api.delete(`/boards/${id}/`);
        this.boards = this.boards.filter(b => b.id !== id);
        if (this.currentBoard && this.currentBoard.id === id) this.currentBoard = null;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async leaveBoard(id) {
      try {
        await api.post(`/boards/${id}/leave/`);
        this.boards = this.boards.filter(b => b.id !== id);
        if (this.currentBoard && this.currentBoard.id === id) this.currentBoard = null;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async inviteMember(boardId, username, role = 'member') {
      try {
        const res = await api.post(`/boards/${boardId}/invite/user/`, { identifier: username, role });
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async fetchInvitations(boardId) {
      try {
        const res = await api.get(`/boards/${boardId}/invite/`);
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async fetchMembers(boardId) {
      try {
        const res = await api.get(`/boards/${boardId}/members/`);
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },

    async fetchActivities(boardId) {
      try {
        const res = await api.get(`/boards/${boardId}/activities/`);
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },
    async inviteEmail(boardId, email, role='member') {
      try {
        const res = await api.post(`/boards/${boardId}/invite/`, { invited_email: email, role });
        return res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    },

    async fetchBoard(id) {
      try {
        const res = await api.get(`/boards/${id}/`);
        this.currentBoard = res.data;
      } catch (e) {
        console.error(e);
        throw e.response?.data || e;
      }
    }
  }
});
