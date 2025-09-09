<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[99999]" @click="$emit('close')">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto" @click.stop>
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">تنظیمات برد</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <p class="text-sm text-gray-600 mt-1">{{ board?.title }}</p>
      </div>

      <!-- Menu Options -->
      <div class="py-2">
        <button @click="$emit('activities', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>تاریخچه</span>
        </button>
        
        <button @click="$emit('members', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
          </svg>
          <span>کاربران</span>
        </button>
        
        <button 
          v-if="['owner','admin'].includes(board?.current_user_role)"
          @click="$emit('invitations', board.id)" 
          class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          <span>دعوت‌ها</span>
        </button>
        
        <template v-if="['owner','admin'].includes(board?.current_user_role)">
          <hr class="my-2">
          <button @click="$emit('invite-user', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
            <span>دعوت کاربر</span>
          </button>
          <button @click="$emit('invite-email', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zM12 8v1.5a3.5 3.5 0 017 0V8a3.5 3.5 0 013.5 3.5z"/>
            </svg>
            <span>دعوت کاربر با ایمیل</span>
          </button>
          <button @click="$emit('edit', board)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <span>ویرایش</span>
          </button>
        </template>
        
        <hr class="my-2">
        <template v-if="board?.current_user_role === 'owner'">
          <button @click="$emit('delete', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            <span>حذف برد</span>
          </button>
        </template>
        <template v-else>
          <button @click="$emit('leave', board.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            <span>ترک برد</span>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  board: {
    type: Object,
    default: null
  }
});

defineEmits([
  'close',
  'activities',
  'members', 
  'invitations',
  'invite-user',
  'invite-email',
  'edit',
  'delete',
  'leave'
]);
</script>
