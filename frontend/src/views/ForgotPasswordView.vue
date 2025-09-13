<template>
  <div class="flex items-center justify-center min-h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-full max-w-md">
      <h1 class="text-2xl font-bold mb-4">فراموشی رمز عبور</h1>

      <div v-if="successMessage" class="mb-4">
        <div class="text-center text-green-700 bg-green-50 border border-green-200 rounded px-4 py-3">
          {{ successMessage }}
        </div>
      </div>

      <div v-if="errorMessage" class="mb-4">
        <div class="text-center text-red-700 bg-red-50 border border-red-200 rounded px-4 py-3">
          {{ errorMessage }}
        </div>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" for="email">ایمیل</label>
          <input v-model="email" id="email" type="email" class="w-full border rounded px-3 py-2" required />
        </div>
        <button type="submit" :disabled="loading" class="w-full bg-sky-600 text-white py-2 rounded hover:bg-sky-700 disabled:opacity-60">
          <span v-if="loading">در حال ارسال...</span>
          <span v-else>ارسال لینک بازیابی</span>
        </button>
      </form>

      <div class="mt-4 text-center">
        <router-link to="/login" class="text-sky-600 hover:underline">بازگشت به ورود</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { storeToRefs } from 'pinia';
import { useErrorsStore } from '../stores/errors';

const email = ref('');
const loading = ref(false);
const successMessage = ref('');
const errorsStore = useErrorsStore();
const { message: errorMessage } = storeToRefs(errorsStore);

const submit = async () => {
  errorsStore.clear();
  successMessage.value = '';
  loading.value = true;
  try {
    await api.post('/users/auth/password/reset/', { email: email.value });
    successMessage.value = 'اگر ایمیلی با این مشخصات وجود داشته باشد، لینک بازیابی برای شما ارسال خواهد شد.';
  } catch (e) {
    // 400 errors won't be pushed to global errors store by interceptor
    // but we still show anything set there; otherwise show generic
    if (!errorMessage.value) {
      successMessage.value = '';
    }
  } finally {
    loading.value = false;
  }
};
</script>
