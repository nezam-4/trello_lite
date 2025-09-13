<template>
  <div class="flex items-center justify-center min-h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-full max-w-md text-center">
      <h1 class="text-2xl font-bold mb-4">تأیید ایمیل</h1>

      <div v-if="loading" class="text-gray-600">در حال بررسی لینک تأیید...</div>

      <div v-else>
        <div v-if="success" class="text-green-700 bg-green-50 border border-green-200 rounded px-4 py-3 mb-4">
          {{ success }}
        </div>
        <div v-if="errorMessage" class="text-red-700 bg-red-50 border border-red-200 rounded px-4 py-3 mb-4">
          {{ errorMessage }}
        </div>
        <div class="space-y-3">
          <router-link to="/login" class="inline-block bg-sky-600 text-white px-4 py-2 rounded hover:bg-sky-700">رفتن به ورود</router-link>
          <div>
            <router-link to="/resend-verification" class="text-sky-600 hover:underline">ارسال مجدد ایمیل تأیید</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';

const route = useRoute();
const loading = ref(true);
const success = ref('');
const errorMessage = ref('');

onMounted(async () => {
  const uid = route.query.uid;
  const token = route.query.token;
  if (!uid || !token) {
    errorMessage.value = 'لینک نامعتبر است.';
    loading.value = false;
    return;
  }
  try {
    await api.get('/users/auth/verify-email/', { params: { uid, token } });
    success.value = 'ایمیل شما با موفقیت تأیید شد. اکنون می‌توانید وارد شوید.';
  } catch (e) {
    const data = e?.response?.data;
    errorMessage.value = (data && (data.detail || data.message)) || 'خطا در تأیید ایمیل';
  } finally {
    loading.value = false;
  }
});
</script>
