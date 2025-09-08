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
     * Update a list (title, color, etc.)
     * @param {Number|String} listId
     * @param {Object} data - Update data (title, color)
     */
    async updateList(listId, data) {
      try {
        if (!listId) throw new Error('listId is required');
        const res = await api.patch(`/lists/${listId}/`, data);
        
        // Update the list in cache
        const index = this.lists.findIndex(list => list.id == listId);
        if (index !== -1) {
          this.lists[index] = { ...this.lists[index], ...res.data };
        }
        
        return res.data;
      } catch (e) {
        console.error('Failed to update list', e);
        throw e.response?.data || e;
      }
    },

    /**
     * Create a new list
     * @param {Object} data - List data (title, board)
     */
    async createList(data) {
      try {
        if (!data.title) throw new Error('List title is required');
        if (!data.board) throw new Error('Board ID is required');
        
        const res = await api.post(`/boards/${data.board}/lists/`, {
          title: data.title,
          color: data.color || 'blue'
        });
        
        // Add the new list to cache
        this.lists.push(res.data);
        
        return res.data;
      } catch (e) {
        console.error('Failed to create list', e);
        throw e.response?.data || e;
      }
    },

    /**
     * Delete a list
     * @param {Number|String} listId
     */
    async deleteList(listId) {
      try {
        if (!listId) throw new Error('listId is required');
        await api.delete(`/lists/${listId}/`);
        
        // Remove the list from cache
        this.lists = this.lists.filter(list => list.id != listId);
      } catch (e) {
        console.error('Failed to delete list', e);
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
