<template>
  <div class="flex items-center justify-center h-screen bg-sky-100">
    <div class="bg-white p-8 shadow-lg rounded w-96">
      <h1 class="text-2xl font-bold mb-4">ثبت نام</h1>
      <p v-if="error" class="text-red-600 mb-4 text-sm">{{ error }}</p>
      <p v-if="successMsg" class="text-green-600 mb-4 text-sm">{{ successMsg }}</p>
      <form @submit.prevent="register">
                <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="username">نام کاربری</label>
          <input v-model="username" id="username" type="text" class="w-full border rounded px-3 py-2" required />
          <p v-if="fieldErrors.username" class="text-red-600 text-xs mt-1">{{ fieldErrors.username[0] }}</p>
        </div>
        <div class="mb-4 flex space-x-2 rtl:space-x-reverse">
          <div class="flex-1">
            <label class="block text-sm font-medium mb-1" for="first">نام</label>
            <input v-model="firstName" id="first" type="text" class="w-full border rounded px-3 py-2" />
            <p v-if="fieldErrors.first_name" class="text-red-600 text-xs mt-1">{{ fieldErrors.first_name[0] }}</p>
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium mb-1" for="last">نام خانوادگی</label>
            <input v-model="lastName" id="last" type="text" class="w-full border rounded px-3 py-2" />
            <p v-if="fieldErrors.last_name" class="text-red-600 text-xs mt-1">{{ fieldErrors.last_name[0] }}</p>
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="email">ایمیل</label>
          <input v-model="email" id="email" type="email" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.email" class="text-red-600 text-xs mt-1">{{ fieldErrors.email[0] }}</p>
        </div>
                <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="password">رمز عبور</label>
          <input v-model="password1" id="password" type="password" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.password1" class="text-red-600 text-xs mt-1">{{ fieldErrors.password1[0] }}</p>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1" for="password2">تکرار رمز عبور</label>
          <input v-model="password2" id="password2" type="password" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.password2" class="text-red-600 text-xs mt-1">{{ fieldErrors.password2[0] }}</p>
        </div>
        <button type="submit" class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">ثبت نام</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import api from '../api';
import { useRouter } from 'vue-router';

const username = ref('');
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const error = ref('');
const fieldErrors = reactive({});
const successMsg = ref('');
const router = useRouter();

const register = async () => {
  try {
    const res = await api.post('/auth/register/', {
      email: email.value,
      username: username.value,
      first_name: firstName.value,
      last_name: lastName.value,
      password1: password1.value,
      password2: password2.value,
    });
    successMsg.value = (res && res.data && res.data.message) ? res.data.message : 'ثبت نام انجام شد. لطفاً ایمیل خود را برای تأیید بررسی کنید.';
    Object.keys(fieldErrors).forEach(k=>delete fieldErrors[k]);
    // router.push('/login');
    } catch (err) {
    let msg = 'خطا';
    const e = err.response?.data || err;
    Object.keys(fieldErrors).forEach(k=>delete fieldErrors[k]);
    if (typeof e === 'string') {
      msg = e;
    } else if (e.detail) {
      msg = e.detail;
    } else if (typeof e === 'object') {
      Object.assign(fieldErrors, e);
      msg = Object.values(e).flat().join(' | ');
    }
    error.value = msg;
      }
};
</script>
