import { defineStore } from 'pinia';

export const useErrorsStore = defineStore('errors', {
  state: () => ({
    message: null,
  }),
  actions: {
    setError(msg) {
      this.message = msg;
    },
    clear() {
      this.message = null;
    },
  },
});
