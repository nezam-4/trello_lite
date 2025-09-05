<template>
  <div class="max-w-md mx-auto p-6" dir="rtl">
    <h2 class="text-2xl font-bold mb-6 text-center">تغییر رمز عبور</h2>

    <form @submit.prevent="submit">
      <div class="mb-4">
        <label class="block text-sm mb-1">رمز عبور فعلی</label>
        <input v-model="form.old_password" type="password" class="w-full border rounded px-3 py-2" required />
      </div>
      <div class="mb-4">
        <label class="block text-sm mb-1">رمز عبور جدید</label>
        <input v-model="form.new_password1" type="password" class="w-full border rounded px-3 py-2" required />
      </div>
      <div class="mb-4">
        <label class="block text-sm mb-1">تکرار رمز عبور جدید</label>
        <input v-model="form.new_password2" type="password" class="w-full border rounded px-3 py-2" required />
      </div>

      <p v-if="error" class="text-red-600 text-sm mb-2 text-center">{{ error }}</p>
      <p v-if="success" class="text-green-600 text-sm mb-2 text-center">{{ success }}</p>

      <div class="text-center">
        <button type="submit" class="bg-sky-600 text-white px-4 py-2 rounded hover:bg-sky-700">ذخیره</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  old_password: '',
  new_password1: '',
  new_password2: ''
});

const error = ref('');
const success = ref('');

async function submit() {
  error.value = '';
  success.value = '';
  // Basic client-side check
  if (form.new_password1 !== form.new_password2) {
    error.value = 'رمزهای جدید مطابقت ندارند';
    return;
  }
  try {
    await auth.changePassword(form.old_password, form.new_password1, form.new_password2);
    success.value = 'رمز عبور با موفقیت تغییر کرد';
    // optionally redirect or clear fields
    form.old_password = form.new_password1 = form.new_password2 = '';
    setTimeout(() => router.push('/profile'), 1000);
  } catch (e) {
    error.value = typeof e === 'string' ? e : (e.detail || JSON.stringify(e));
  }
}
</script>
