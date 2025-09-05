<template>
  <div v-if="message" class="fixed top-4 inset-x-0 flex justify-center z-50">
    <div class="bg-red-500 text-white px-4 py-2 rounded shadow-lg flex items-center space-x-3 rtl:space-x-reverse max-w-lg w-full mx-4">
      <span class="flex-1">{{ message }}</span>
      <button @click="clear" class="text-white hover:text-gray-200">✕</button>
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
