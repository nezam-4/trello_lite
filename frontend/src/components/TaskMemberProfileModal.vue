<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4"
    @click="closeModal"
  >
    <div 
      class="bg-white rounded-xl sm:rounded-2xl shadow-2xl max-w-xs sm:max-w-sm w-full overflow-hidden"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-500 to-blue-600 px-4 sm:px-6 py-3 sm:py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-base sm:text-lg font-bold text-white">عضو تسک</h3>
          <button 
            @click="closeModal"
            class="text-white hover:text-gray-200 transition-colors p-1"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-4 sm:p-6" v-if="member">
        <!-- Avatar and Basic Info -->
        <div class="flex items-center space-x-2 sm:space-x-3 space-x-reverse mb-3 sm:mb-4">
          <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm sm:text-lg font-semibold flex-shrink-0">
            {{ getInitials(member.full_name || member.username) }}
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-sm sm:text-base font-semibold text-gray-900 truncate">{{ member.full_name || member.username }}</h4>
            <p class="text-xs sm:text-sm text-gray-600 truncate">@{{ member.username }}</p>
          </div>
        </div>

        <!-- Task Info -->
        <div class="bg-gray-50 rounded-lg p-4 mb-4">
          <h5 class="text-sm font-medium text-gray-700 mb-2">اطلاعات تسک</h5>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">عنوان تسک:</span>
              <span class="font-medium text-gray-900">{{ task?.title || 'نامشخص' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">وضعیت:</span>
              <span :class="task?.is_completed ? 'text-green-600 font-medium' : 'text-orange-600 font-medium'">
                {{ task?.is_completed ? 'تکمیل شده' : 'در حال انجام' }}
              </span>
            </div>
            <div v-if="task?.due_date" class="flex justify-between">
              <span class="text-gray-600">سررسید:</span>
              <span class="text-blue-600 font-medium">{{ formatDate(task.due_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-center">
          <button
            @click="viewTaskDetails"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 space-x-reverse"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            <span>مشاهده تسک</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  member: {
    type: Object,
    default: null
  },
  task: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'viewTask']);

const closeModal = () => {
  emit('close');
};

const viewTaskDetails = () => {
  emit('viewTask', props.task);
  closeModal();
};


const getInitials = (name) => {
  if (!name) return 'U';
  
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = date - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'امروز';
  if (diffDays === 1) return 'فردا';
  if (diffDays === -1) return 'دیروز';
  if (diffDays > 0) return `${diffDays} روز دیگر`;
  if (diffDays < 0) return `${Math.abs(diffDays)} روز پیش`;
  
  return date.toLocaleDateString('fa-IR');
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
