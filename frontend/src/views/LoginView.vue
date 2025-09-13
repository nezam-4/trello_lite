<template>
  <div class="flex items-center justify-center h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-96">
      <h1 class="text-2xl font-bold mb-4">ورود</h1>
      <!-- Centered error message inside the card -->
      <div v-if="errorMessage" class="mb-4">
        <div class="text-center text-red-700 bg-red-50 border border-red-200 rounded px-4 py-3">
          {{ errorMessage }}
        </div>
      </div>
      <form @submit.prevent="login">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="email">ایمیل</label>
          <input v-model="email" id="email" type="email" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="password">رمز عبور</label>
          <input v-model="password" id="password" type="password" class="w-full border rounded px-3 py-2" required />
          <div class="text-left mt-2">
            <router-link to="/forgot-password" class="text-sky-600 hover:underline text-sm">فراموشی رمز عبور؟</router-link>
          </div>
        </div>
        <button type="submit" class="w-full bg-sky-600 text-white py-2 rounded hover:bg-sky-700">ورود</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '../stores/auth';
import { useErrorsStore } from '../stores/errors';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const authStore = useAuthStore();
const router = useRouter();
const errorsStore = useErrorsStore();
const { message: errorMessage } = storeToRefs(errorsStore);

const login = async () => {
  console.log('Login button clicked');
  console.log('Auth store object:', authStore);
  // Clear any previous error
  errorsStore.clear();
  if (await authStore.login(email.value, password.value)) {
    router.push('/boards');
  }
};
</script>
