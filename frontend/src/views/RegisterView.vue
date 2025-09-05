<template>
  <div class="flex items-center justify-center h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-96">
      <h1 class="text-2xl font-bold mb-4">ثبت نام</h1>
      <form @submit.prevent="register">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="email">ایمیل</label>
          <input v-model="email" id="email" type="email" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="password">رمز عبور</label>
          <input v-model="password" id="password" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <button type="submit" class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">ثبت نام</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();

const register = async () => {
  try {
    await api.post('/users/auth/register/', { email: email.value, password: password.value });
    router.push('/login');
  } catch (e) {
    console.error(e);
  }
};
</script>
