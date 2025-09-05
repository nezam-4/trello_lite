import { defineStore } from 'pinia';
import api from '../api';

export const useListsStore = defineStore('lists', {
  state: () => ({
    lists: [],
    boardId: null,
  }),
  actions: {
    /**
     * Fetch all lists for a board and cache them in state.
     * @param {Number|String} boardId
     */
    async fetchLists(boardId) {
      try {
        if (!boardId) throw new Error('boardId is required');
        const res = await api.get(`/boards/${boardId}/lists/`);
        this.lists = res.data;
        this.boardId = boardId;
      } catch (e) {
        console.error('Failed to fetch lists', e);
        throw e.response?.data || e;
      }
    },

    /**
     * Clear cached lists (e.g., when leaving the board view)
     */
    clear() {
      this.lists = [];
      this.boardId = null;
    },
  },
});
