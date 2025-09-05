<template>
  <header class="bg-sky-600 text-white">
    <nav class="container mx-auto flex items-center justify-between p-4">
      <h1 class="text-xl font-bold">
        <router-link to="/boards" class="hover:text-sky-200">Trello Lite</router-link>
      </h1>
      <ul class="flex gap-4 items-center relative">
        <li v-if="!auth.isAuthenticated">
          <router-link to="/login" class="hover:text-sky-200">ورود</router-link>
        </li>
        <li v-if="!auth.isAuthenticated">
          <router-link to="/register" class="hover:text-sky-200">ثبت نام</router-link>
        </li>
        <li v-if="auth.isAuthenticated">
          <router-link to="/boards" class="hover:text-sky-200">بردها</router-link>
        </li>
        <!-- user dropdown -->
        <li v-if="auth.isAuthenticated" class="relative">
          <button @click="toggleMenu" class="flex items-center gap-2 focus:outline-none">
            <template v-if="auth.user && auth.user.profile && auth.user.profile.avatar">
              <img :src="auth.user.profile.avatar" alt="avatar" class="w-8 h-8 rounded-full object-cover" />
            </template>
            <template v-else>
              <span class="bg-white text-sky-600 w-8 h-8 flex items-center justify-center rounded-full font-bold">
                {{ (auth.user?.first_name || auth.user?.email || '?')[0] }}
              </span>
            </template>
          </button>
          <!-- dropdown -->
          <div v-if="showMenu" class="absolute right-0 mt-2 bg-white text-gray-800 rounded shadow w-40 z-20">
            <router-link to="/profile" class="block px-4 py-2 hover:bg-gray-100">ویرایش پروفایل</router-link>
            <router-link to="/change-password" class="block px-4 py-2 hover:bg-gray-100">تغییر رمز</router-link>
            <button @click="logout" class="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600">خروج</button>
          </div>
        </li>
      </ul>
    </nav>
  </header>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();
const showMenu = ref(false);

onMounted(() => {
  if (auth.isAuthenticated && !auth.user) {
    auth.fetchCurrentUser();
  }
});

function toggleMenu() {
  showMenu.value = !showMenu.value;
}

function logout() {
  auth.logout();
  router.push('/login');
}
</script>
