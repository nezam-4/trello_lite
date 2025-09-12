<template>
  <div v-if="message" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="bg-red-500 text-white px-4 py-3 rounded shadow-lg max-w-lg w-[90%] mx-auto flex items-center gap-3">
      <span class="flex-1 text-center">{{ message }}</span>
      <button @click="clear" class="text-white/90 hover:text-white">✕</button>
    </div>
  </div>
  
</template>

<script setup>
import { storeToRefs } from 'pinia';
import { useErrorsStore } from '../stores/errors';

const errorsStore = useErrorsStore();
const { message } = storeToRefs(errorsStore);

function clear() {
  errorsStore.clear();
}
</script>
