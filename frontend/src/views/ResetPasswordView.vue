<template>
  <div class="flex items-center justify-center min-h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-full max-w-md">
      <h1 class="text-2xl font-bold mb-4">بازنشانی رمز عبور</h1>

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
          <label class="block text-sm font-medium mb-1" for="password1">رمز عبور جدید</label>
          <input v-model="password1" id="password1" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" for="password2">تکرار رمز عبور جدید</label>
          <input v-model="password2" id="password2" type="password" class="w-full border rounded px-3 py-2" required />
        </div>

        <button type="submit" :disabled="loading" class="w-full bg-sky-600 text-white py-2 rounded hover:bg-sky-700 disabled:opacity-60">
          <span v-if="loading">در حال اعمال...</span>
          <span v-else>تایید و اعمال</span>
        </button>
      </form>

      <div class="mt-4 text-center">
        <router-link to="/login" class="text-sky-600 hover:underline">بازگشت به ورود</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import { useRoute, useRouter } from 'vue-router';
import { useErrorsStore } from '../stores/errors';
import { storeToRefs } from 'pinia';

const route = useRoute();
const router = useRouter();
const errorsStore = useErrorsStore();
const { message: errorMessage } = storeToRefs(errorsStore);

const uid = ref('');
const token = ref('');
const password1 = ref('');
const password2 = ref('');
const loading = ref(false);
const successMessage = ref('');

onMounted(() => {
  errorsStore.clear();
  uid.value = route.query.uid || '';
  token.value = route.query.token || '';
  if (!uid.value || !token.value) {
    errorsStore.setError('لینک نامعتبر است. لطفاً دوباره درخواست بازیابی ارسال کنید.');
  }
});

const submit = async () => {
  errorsStore.clear();
  successMessage.value = '';

  if (!uid.value || !token.value) {
    errorsStore.setError('پارامترهای لینک ناقص است.');
    return;
  }
  if (password1.value !== password2.value) {
    errorsStore.setError('رمزهای عبور یکسان نیستند.');
    return;
  }

  loading.value = true;
  try {
    await api.post('/users/auth/password/reset/confirm/', {
      uid: uid.value,
      token: token.value,
      new_password1: password1.value,
      new_password2: password2.value
    });
    successMessage.value = 'رمز عبور با موفقیت بازنشانی شد. اکنون می‌توانید وارد شوید.';
  } catch (e) {
    // If backend returns validation errors, interceptor may not set global error for 400
    if (!errorMessage.value) {
      errorsStore.setError('خطا در بازنشانی رمز عبور');
    }
  } finally {
    loading.value = false;
  }
};
</script>
