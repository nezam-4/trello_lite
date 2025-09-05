import { defineStore } from 'pinia';
import api from '../api';

/**
 * Pinia store for task operations scoped by list.
 */
export const useTasksStore = defineStore('tasks', {
  state: () => ({
    // { [listId]: Task[] }
    tasksByList: {},
    currentTask: null,
    modalOpen: false,
  }),
  getters: {
    /**
     * Get tasks array for a list id (or empty array if not yet fetched)
     */
    tasks: (state) => {
      return (listId) => state.tasksByList[listId] || [];
    },
  },
  actions: {
    /**
     * Fetch tasks of a particular list from API and cache.
     * @param {Number|String} listId
     */
    async fetchTasks(listId) {
      if (!listId) throw new Error('listId is required');
      try {
        const res = await api.get(`/tasks/lists/${listId}/tasks/`);
        this.tasksByList[listId] = res.data;
      } catch (e) {
        console.error('Failed to fetch tasks', e);
        throw e.response?.data || e;
      }
    },
    /**
     * Clear cache (e.g., leaving board view)
     */
    async createTask(listId, title) {
      if (!listId || !title) throw new Error('listId and title are required');
      try {
        const res = await api.post(`/tasks/lists/${listId}/tasks/`, { title });
        // if list not fetched yet create array
        if (!this.tasksByList[listId]) this.tasksByList[listId] = [];
        this.tasksByList[listId].push(res.data);
        return res.data;
      } catch (e) {
        console.error('Failed to create task', e);
        throw e.response?.data || e;
      }
    },

    async openTask(id) {
      await this.fetchTask(id);
      this.modalOpen = true;
    },

    async fetchTask(id) {
      try {
        const res = await api.get(`/tasks/tasks/${id}/`);
        this.currentTask = res.data;
        return res.data;
      } catch (e) {
        console.error('Failed to fetch task', e);
        throw e.response?.data || e;
      }
    },

    async toggleComplete(id) {
      try {
        const res = await api.post(`/tasks/tasks/${id}/toggle-complete/`);
        const updated = res.data.task || res.data;
        // Replace reference with new cloned object for deep reactivity
        this.currentTask = { ...updated };
        // update cache
        const listId = updated.list;
        if (this.tasksByList[listId]) {
          const idx = this.tasksByList[listId].findIndex(t => t.id === id);
          if (idx !== -1) {
          // Replace object reference for Vue reactivity
          this.tasksByList[listId][idx] = updated;
        }
        }
        return updated;
      } catch (e) {
        console.error('Failed to toggle completion', e);
        throw e.response?.data || e;
      }
    },

    async updateTask(id, data) {
      try {
        const res = await api.patch(`/tasks/tasks/${id}/`, data);
        const updated = res.data;
        // Replace reference with new cloned object for deep reactivity
        this.currentTask = { ...updated };
        // also update cached list
        const listId = updated.list;
        if (this.tasksByList[listId]) {
          const idx = this.tasksByList[listId].findIndex(t => t.id === id);
          if (idx !== -1) {
          // Replace object reference for Vue reactivity
          this.tasksByList[listId][idx] = updated;
        }
        }
        return updated;
      } catch (e) {
        console.error('Failed to update task', e);
        throw e.response?.data || e;
      }
    },

    closeTask() {
      this.modalOpen = false;
      this.currentTask = null;
    },

    clear() {
      this.tasksByList = {};
      this.currentTask = null;
    },
  },
});
