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
        const res = await api.get(`/tasks/lists/${listId}/`);
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
        const res = await api.post(`/tasks/lists/${listId}/`, { title });
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
        const res = await api.get(`/tasks/${id}/`);
        this.currentTask = res.data;
        return res.data;
      } catch (e) {
        console.error('Failed to fetch task', e);
        throw e.response?.data || e;
      }
    },

    async toggleComplete(id) {
      try {
        const res = await api.post(`/tasks/${id}/toggle-complete/`);
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
        const res = await api.patch(`/tasks/${id}/`, data);
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

    async deleteTask(id) {
      try {
        await api.delete(`/tasks/${id}/`);
        // Determine the list that contains this task
        let listId = null;
        if (this.currentTask && this.currentTask.id === id) {
          listId = this.currentTask.list;
        } else {
          for (const key in this.tasksByList) {
            if (this.tasksByList[key]?.some?.(t => t.id === id)) {
              listId = key;
              break;
            }
          }
        }
        // Remove from cache if found
        if (listId !== null && this.tasksByList[listId]) {
          this.tasksByList[listId] = this.tasksByList[listId].filter(t => t.id !== id);
        }
        // Close modal if this was the open task
        if (this.currentTask && this.currentTask.id === id) {
          this.closeTask();
        }
        return true;
      } catch (e) {
        console.error('Failed to delete task', e);
        throw e.response?.data || e;
      }
    },

    closeTask() {
      this.modalOpen = false;
      this.currentTask = null;
    },

    async moveTask(taskId, newListId, newPosition) {
      try {
        const payload = {};
        if (newListId) payload.new_list = newListId;
        if (newPosition !== undefined) payload.new_position = newPosition;
        
        const res = await api.post(`/tasks/${taskId}/move/`, payload);
        const updated = res.data;
        
        // Instead of manually updating cache, refresh affected lists
        // This ensures positions are accurate after backend processing
        const affectedLists = new Set();
        
        // Find old list
        for (const listId in this.tasksByList) {
          const taskIndex = this.tasksByList[listId].findIndex(t => t.id === taskId);
          if (taskIndex !== -1) {
            affectedLists.add(listId);
            break;
          }
        }
        
        // Add new list if different
        if (newListId) {
          affectedLists.add(newListId.toString());
        }
        
        // Refresh all affected lists
        for (const listId of affectedLists) {
          await this.fetchTasks(listId);
        }
        
        return updated;
      } catch (e) {
        console.error('Failed to move task', e);
        throw e.response?.data || e;
      }
    },

    clear() {
      this.tasksByList = {};
      this.currentTask = null;
    },
  },
});
