<template>
  <div class="max-w-md mx-auto p-6" dir="rtl">
    <h2 class="text-2xl font-bold mb-6 text-center">تغییر رمز عبور</h2>

    <form @submit.prevent="submit">
      <div class="mb-4">
        <label class="block text-sm mb-1">رمز عبور فعلی</label>
        <input v-model="form.old_password" @input="clearFieldError('old_password')" type="password" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.old_password" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.old_password) }}</p>
      </div>
      <div class="mb-4">
        <label class="block text-sm mb-1">رمز عبور جدید</label>
        <input v-model="form.new_password1" @input="clearFieldError('new_password1')" type="password" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.new_password1" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.new_password1) }}</p>
      </div>
      <div class="mb-4">
        <label class="block text-sm mb-1">تکرار رمز عبور جدید</label>
        <input v-model="form.new_password2" @input="clearFieldError('new_password2')" type="password" class="w-full border rounded px-3 py-2" required />
        <p v-if="fieldErrors.new_password2" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.new_password2) }}</p>
      </div>

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

const success = ref('');
const fieldErrors = reactive({});

async function submit() {
  success.value = '';
  // Clear previous field errors
  for (const k in fieldErrors) delete fieldErrors[k];
  // Client-side check: password mismatch
  if (form.new_password1 !== form.new_password2) {
    fieldErrors.new_password2 = 'رمزهای جدید مطابقت ندارند';
    return;
  }
  try {
    await auth.changePassword(form.old_password, form.new_password1, form.new_password2);
    success.value = 'رمز عبور با موفقیت تغییر کرد';
    // optionally redirect or clear fields
    form.old_password = form.new_password1 = form.new_password2 = '';
    setTimeout(() => router.push('/profile'), 1000);
  } catch (e) {
    const fields = parsePasswordErrors(e);
    Object.assign(fieldErrors, fields);
  }
}

function parsePasswordErrors(err) {
  const fields = {};
  if (err && typeof err === 'object') {
    if (err.old_password) fields.old_password = err.old_password;
    if (err.new_password1) fields.new_password1 = err.new_password1;
    if (err.new_password2) fields.new_password2 = err.new_password2;
    if (err.non_field_errors) {
      const msg = Array.isArray(err.non_field_errors) ? err.non_field_errors.join('، ') : String(err.non_field_errors);
      fields.new_password2 = msg;
    }
    if (err.detail && !fields.old_password && !fields.new_password1 && !fields.new_password2) {
      fields.old_password = err.detail;
    }
  }
  return fields;
}

function formatErr(val) {
  if (!val) return '';
  return Array.isArray(val) ? val.join('، ') : String(val);
}

function clearFieldError(field) {
  if (field in fieldErrors) delete fieldErrors[field];
}
</script>
