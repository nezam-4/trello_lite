<template>
  <div class="max-w-xl mx-auto p-4 sm:p-6" dir="rtl">
    <h2 class="text-xl sm:text-2xl font-bold mb-4 text-center">ویرایش پروفایل</h2>

    <form @submit.prevent="submit">
      <div class="flex flex-col items-center mb-4">
        <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-full overflow-hidden border mb-2 bg-gray-100 flex items-center justify-center">
          <img
            v-if="avatarPreview"
            :src="avatarPreview"
            alt="avatar"
            class="w-full h-full object-cover"
            @error="onImageError"
          />
          <span v-else class="text-gray-500 text-2xl">
            {{ auth.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
          </span>
        </div>
        <input type="file" accept="image/*" @change="onFileChange" />
        <p v-if="fieldErrors.avatar" class="text-red-600 text-sm mt-2">{{ formatErr(fieldErrors.avatar) }}</p>
      </div>

      <div class="mb-3">
        <label class="block text-xs sm:text-sm mb-1">نام کاربری</label>
        <input v-model="form.username" @input="clearFieldError('username')" type="text" class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base" />
        <p v-if="fieldErrors.username" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.username) }}</p>
      </div>
      <div class="mb-3">
        <label class="block text-xs sm:text-sm mb-1">نام</label>
        <input v-model="form.first_name" @input="clearFieldError('first_name')" type="text" class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base" />
        <p v-if="fieldErrors.first_name" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.first_name) }}</p>
      </div>
      <div class="mb-3">
        <label class="block text-xs sm:text-sm mb-1">نام خانوادگی</label>
        <input v-model="form.last_name" @input="clearFieldError('last_name')" type="text" class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base" />
        <p v-if="fieldErrors.last_name" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.last_name) }}</p>
      </div>
      <div class="mb-3">
        <label class="block text-xs sm:text-sm mb-1">ایمیل</label>
        <input v-model="form.email" type="email" readonly class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base bg-gray-100 text-gray-500 cursor-not-allowed" />
        <p class="text-gray-500 text-xs mt-1">ایمیل قابل تغییر نیست</p>
      </div>
      <div class="mb-3">
        <label class="block text-xs sm:text-sm mb-1">بیو</label>
        <textarea v-model="form.bio" @input="clearFieldError('bio')" rows="3" class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base"></textarea>
        <p v-if="fieldErrors.bio" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.bio) }}</p>
      </div>
      <div class="mb-4">
        <label class="block text-xs sm:text-sm mb-1">زبان ترجیحی</label>
        <select v-model="form.preferred_language" @change="clearFieldError('preferred_language')" class="w-full border rounded-lg px-3 py-2 text-sm sm:text-base">
          <option value="fa">فارسی</option>
          <option value="en">English</option>
        </select>
        <p v-if="fieldErrors.preferred_language" class="text-red-600 text-sm mt-1">{{ formatErr(fieldErrors.preferred_language) }}</p>
      </div>

      <p v-if="success" class="text-green-600 text-sm mb-2 text-center">{{ success }}</p>

      <div class="text-center">
        <button type="submit" class="bg-sky-600 text-white px-4 py-2 rounded hover:bg-sky-700">ذخیره تغییرات</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const form = reactive({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  bio: '',
  preferred_language: 'fa',
  avatar: null
});
const avatarPreview = ref('');
const error = ref('');
const success = ref('');
const fieldErrors = reactive({});

onMounted(async () => {
  console.log('ProfileView mounted - auth.user:', auth.user);
  if (auth.isAuthenticated) {
    try {
      console.log('Fetching profile data...');
      await auth.fetchProfile();
      console.log('Profile fetched, user data:', auth.user);
      populate();
    } catch (e) {
      console.error('Error fetching profile:', e);
      error.value = 'خطا در دریافت پروفایل';
    }
  }
});

function populate() {
  if (!auth.user) return;
  form.username = auth.user.username || '';
  form.first_name = auth.user.first_name || '';
  form.last_name = auth.user.last_name || '';
  form.email = auth.user.email || '';
  form.bio = auth.user.profile?.bio || '';
  form.preferred_language = auth.user.profile?.preferred_language || 'fa';
  
  // Use thumbnail URL if available, otherwise use original avatar
  let avatarUrl = auth.user.profile?.avatar_thumbnail_url || auth.user.profile?.avatar || '';
  
  // Ensure we have absolute URL for avatar display
  if (avatarUrl && !avatarUrl.startsWith('http')) {
    avatarUrl = `http://127.0.0.1:8000${avatarUrl}`;
  }
  
  avatarPreview.value = avatarUrl;
  console.log('ProfileView - avatarPreview set to:', avatarPreview.value);
}

function onFileChange(e) {
  const file = e.target.files[0];
  if (file) {
    form.avatar = file;
    avatarPreview.value = URL.createObjectURL(file);
  }
}

function onImageError() {
  console.log('ProfileView - Image load error for:', avatarPreview.value);
  avatarPreview.value = '';
}

async function submit() {
  error.value = '';
  success.value = '';
  // clear previous field errors
  for (const k in fieldErrors) delete fieldErrors[k];
  const data = new FormData();
  data.append('username', form.username);
  data.append('first_name', form.first_name);
  data.append('last_name', form.last_name);
  data.append('bio', form.bio);
  data.append('preferred_language', form.preferred_language);
  if (form.avatar) data.append('avatar', form.avatar);

  try {
    await auth.updateProfile(data);
    success.value = 'پروفایل با موفقیت به‌روزرسانی شد';
    // Refresh header by fetching current user
    await auth.fetchCurrentUser();
  } catch (err) {
    const { message, fields } = parseProfileErrors(err);
    error.value = message;
    Object.assign(fieldErrors, fields);
  }
}

function parseProfileErrors(err) {
  let message = typeof err === 'string' ? err : (err?.detail || (Array.isArray(err?.non_field_errors) ? err.non_field_errors.join('، ') : err?.non_field_errors) || '');
  const fields = {};
  if (err && typeof err === 'object') {
    // Nested user/profile errors
    if (err.user && typeof err.user === 'object') {
      for (const [k, v] of Object.entries(err.user)) fields[k] = v;
    }
    if (err.profile && typeof err.profile === 'object') {
      for (const [k, v] of Object.entries(err.profile)) fields[k] = v;
    }
    // Top-level fields (fallback)
    for (const [k, v] of Object.entries(err)) {
      if (['detail', 'non_field_errors', 'user', 'profile'].includes(k)) continue;
      fields[k] = v;
    }
    if (!message) {
      const parts = [];
      for (const val of Object.values(fields)) {
        const text = Array.isArray(val) ? val.join('، ') : String(val);
        parts.push(text);
        if (parts.length >= 1) break;
      }
      if (parts.length) message = parts.join(' | ');
    }
  }
  if (!message && err) message = JSON.stringify(err);
  return { message, fields };
}

function formatErr(val) {
  if (!val) return '';
  return Array.isArray(val) ? val.join('، ') : String(val);
}

function clearFieldError(field) {
  if (field in fieldErrors) {
    delete fieldErrors[field];
  }
}
</script>
