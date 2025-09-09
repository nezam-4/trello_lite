<template>
  <header class="bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-50">
    <nav class="w-full flex items-center justify-between px-3 sm:px-4 md:px-6 py-3 sm:py-4">
      <!-- Logo -->
      <div class="flex items-center space-x-2 sm:space-x-4 space-x-reverse flex-shrink-0">
        <router-link to="/boards" class="flex items-center space-x-1 sm:space-x-2 space-x-reverse group">
          <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-md sm:rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-3 h-3 sm:w-5 sm:h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
            </svg>
          </div>
          <h1 class="text-base sm:text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent group-hover:from-blue-600 group-hover:to-purple-600 transition-all duration-300 whitespace-nowrap">
            Trello Lite
          </h1>
        </router-link>
      </div>

      <!-- Navigation -->
      <div class="flex items-center space-x-2 sm:space-x-4 md:space-x-6 space-x-reverse flex-shrink-0">
        <!-- Mobile Menu Button -->
        <button 
          v-if="auth.isAuthenticated"
          @click="showMobileMenu = !showMobileMenu"
          class="md:hidden p-1.5 sm:p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-5 h-5 sm:w-6 sm:h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <!-- Desktop Navigation -->
        <nav v-if="auth.isAuthenticated" class="hidden md:flex items-center space-x-4 lg:space-x-6 space-x-reverse">
          <router-link 
            to="/boards" 
            class="px-2 lg:px-4 py-2 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-blue-50 font-medium transition-all duration-200 flex items-center space-x-1 lg:space-x-2 space-x-reverse text-sm lg:text-base"
          >
            <svg class="w-3 h-3 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            <span class="whitespace-nowrap">بردها</span>
          </router-link>
        </nav>

        <!-- User Menu -->
        <div v-if="auth.isAuthenticated" class="relative">
          <button 
            @click="toggleMenu" 
            class="flex items-center space-x-2 sm:space-x-3 space-x-reverse p-1.5 sm:p-2 rounded-lg sm:rounded-xl hover:bg-gray-100 transition-all duration-200 profile-menu group"
          >
            <div class="hidden sm:flex flex-col items-end">
              <span class="text-xs sm:text-sm font-medium text-gray-900 truncate max-w-20 lg:max-w-none">{{ auth.user?.first_name || 'کاربر' }}</span>
              <span class="text-xs text-gray-500 truncate max-w-20 lg:max-w-none">{{ auth.user?.email }}</span>
            </div>
            <div class="relative flex-shrink-0">
              <div class="ring-2 ring-gray-200 group-hover:ring-blue-300 transition-all duration-200 rounded-lg sm:rounded-xl overflow-hidden">
                <UserAvatar
                  v-if="auth.user"
                  :user="auth.user"
                  size="sm"
                  :clickable="false"
                />
              </div>
              <div class="absolute -bottom-0.5 -right-0.5 sm:-bottom-1 sm:-right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-400 border-2 border-white rounded-full"></div>
            </div>
          </button>
          
          <!-- Dropdown Menu -->
          <div v-if="showMenu" class="absolute left-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200/50 py-2 z-20 profile-menu">
            <div class="px-4 py-3 border-b border-gray-100">
              <p class="text-sm font-medium text-gray-900">{{ auth.user?.first_name || 'کاربر' }}</p>
              <p class="text-xs text-gray-500">{{ auth.user?.email }}</p>
            </div>
            
            <router-link 
              to="/profile" 
              class="flex items-center space-x-3 space-x-reverse px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <span>ویرایش پروفایل</span>
            </router-link>
            
            <router-link 
              to="/change-password" 
              class="flex items-center space-x-3 space-x-reverse px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              <span>تغییر رمز</span>
            </router-link>
            
            <hr class="my-2">
            
            <button 
              @click="logout" 
              class="flex items-center space-x-3 space-x-reverse w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              <span>خروج</span>
            </button>
          </div>
        </div>

        <!-- Auth Links -->
        <div v-else class="flex items-center space-x-2 sm:space-x-4 space-x-reverse">
          <router-link 
            to="/login" 
            class="px-2 sm:px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors text-sm sm:text-base whitespace-nowrap"
          >
            ورود
          </router-link>
          <router-link 
            to="/register" 
            class="px-3 sm:px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 font-medium shadow-md hover:shadow-lg transition-all duration-200 text-sm sm:text-base whitespace-nowrap"
          >
            ثبت نام
          </router-link>
        </div>
      </div>
    </nav>
    
    <!-- Mobile Menu Overlay -->
    <div 
      v-if="showMobileMenu && auth.isAuthenticated" 
      class="md:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      @click="showMobileMenu = false"
    >
      <div class="bg-white w-72 sm:w-80 h-full shadow-xl" @click.stop>
        <div class="p-4 sm:p-6 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-base sm:text-lg font-bold text-gray-900">منو</h2>
            <button @click="showMobileMenu = false" class="p-1.5 sm:p-2 hover:bg-gray-100 rounded-lg">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-4 sm:p-6 space-y-3 sm:space-y-4">
          <router-link 
            to="/boards" 
            @click="showMobileMenu = false"
            class="flex items-center space-x-2 sm:space-x-3 space-x-reverse p-2 sm:p-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            <span class="font-medium text-gray-900 text-sm sm:text-base">بردها</span>
          </router-link>
          
          <router-link 
            to="/profile" 
            @click="showMobileMenu = false"
            class="flex items-center space-x-2 sm:space-x-3 space-x-reverse p-2 sm:p-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <span class="font-medium text-gray-900 text-sm sm:text-base">پروفایل</span>
          </router-link>
          
          <router-link 
            to="/change-password" 
            @click="showMobileMenu = false"
            class="flex items-center space-x-2 sm:space-x-3 space-x-reverse p-2 sm:p-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
            <span class="font-medium text-gray-900 text-sm sm:text-base">تغییر رمز</span>
          </router-link>
          
          <hr class="my-3 sm:my-4">
          
          <button 
            @click="logout; showMobileMenu = false" 
            class="flex items-center space-x-2 sm:space-x-3 space-x-reverse w-full p-2 sm:p-3 rounded-lg hover:bg-red-50 transition-colors text-red-600"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            <span class="font-medium text-sm sm:text-base">خروج</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import UserAvatar from './UserAvatar.vue';

const auth = useAuthStore();
const router = useRouter();
const showMenu = ref(false);
const showMobileMenu = ref(false);

function handleOutside(e) {
  if (!e.target.closest('.profile-menu')) {
    showMenu.value = false;
  }
}

onMounted(async () => {
  console.log('Header mounted - isAuthenticated:', auth.isAuthenticated, 'user:', auth.user);
  console.log('Access token exists:', !!auth.access);
  
  if (auth.isAuthenticated) {
    // Always fetch current user to ensure we have latest profile data
    console.log('Calling fetchCurrentUser from Header...');
    try {
      await auth.fetchCurrentUser();
      console.log('fetchCurrentUser completed, user:', auth.user);
    } catch (error) {
      console.error('Error in fetchCurrentUser:', error);
    }
  }
  window.addEventListener('click', handleOutside);
});

onBeforeUnmount(() => {
  window.removeEventListener('click', handleOutside);
});

function toggleMenu() {
  showMenu.value = !showMenu.value;
}

function logout() {
  auth.logout();
  router.push('/login');
}
</script>
