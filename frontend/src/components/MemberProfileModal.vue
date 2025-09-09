<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4"
    @click="closeModal"
  >
    <div 
      class="bg-white rounded-xl sm:rounded-2xl shadow-2xl max-w-xs sm:max-w-md w-full overflow-hidden"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-4 sm:px-6 py-3 sm:py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg sm:text-xl font-bold text-white">پروفایل عضو</h3>
          <button 
            @click="closeModal"
            class="text-white hover:text-gray-200 transition-colors p-1"
          >
            <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-4 sm:p-6" v-if="member">
        <!-- Avatar and Basic Info -->
        <div class="flex items-center space-x-3 sm:space-x-4 space-x-reverse mb-4 sm:mb-6">
          <UserAvatar
            :user="member"
            size="lg"
            :clickable="false"
          />
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-gray-900">{{ member.name || member.username }}</h4>
            <p class="text-gray-600">@{{ member.username }}</p>
            <div class="flex items-center mt-1">
              <span 
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getRoleClass(member.role)"
              >
                {{ getRoleText(member.role) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Member Details -->
        <div class="space-y-4">
          <div class="border-t border-gray-200 pt-4">
            <h5 class="text-sm font-medium text-gray-700 mb-3">اطلاعات عضویت</h5>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">نقش:</span>
                <span class="font-medium text-gray-900 mr-2">{{ getRoleText(member.role) }}</span>
              </div>
              <div>
                <span class="text-gray-500">وضعیت:</span>
                <span class="font-medium text-green-600 mr-2">فعال</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="border-t border-gray-200 pt-4" v-if="canManageMembers">
            <div class="flex justify-center">
              <button 
                v-if="member.role !== 'owner'"
                @click="removeMember"
                class="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-2 space-x-reverse"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                <span>حذف عضو</span>
              </button>
              <button 
                v-else
                @click="manageMember"
                class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-2 space-x-reverse"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span>مدیریت</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import UserAvatar from './UserAvatar.vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  member: {
    type: Object,
    default: null
  },
  canManageMembers: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'sendMessage', 'manageMember', 'removeMember']);

const closeModal = () => {
  emit('close');
};

const sendMessage = () => {
  emit('sendMessage', props.member);
  closeModal();
};

const manageMember = () => {
  emit('manageMember', props.member);
  closeModal();
};

const removeMember = () => {
  emit('removeMember', props.member);
  closeModal();
};

const getRoleClass = (role) => {
  switch (role) {
    case 'owner':
      return 'bg-purple-100 text-purple-800';
    case 'admin':
      return 'bg-blue-100 text-blue-800';
    case 'member':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getRoleText = (role) => {
  switch (role) {
    case 'owner':
      return 'مالک';
    case 'admin':
      return 'مدیر';
    case 'member':
      return 'عضو';
    default:
      return 'نامشخص';
  }
};

const getInitials = (fullName, username) => {
  if (fullName) {
    return fullName
      .split(' ')
      .map((part) => part[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  }
  if (username) {
    return username.slice(0, 2).toUpperCase();
  }
  return 'U';
};
</script>

<style scoped>
/* Modal animation */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9) translateY(-50px);
}
</style>
