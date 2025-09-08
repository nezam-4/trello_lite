<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="cancel"
  >
    <div 
      class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden transform transition-all duration-300"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3 space-x-reverse">
            <div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white">{{ title }}</h3>
          </div>
          <button 
            @click="cancel"
            class="text-white hover:text-gray-200 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Icon and Message -->
        <div class="text-center mb-6">
          <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </div>
          <p class="text-gray-700 text-lg leading-relaxed">{{ message }}</p>
        </div>

        <!-- Member Info (if provided) -->
        <div v-if="memberInfo" class="bg-gray-50 rounded-xl p-4 mb-6">
          <div class="flex items-center space-x-3 space-x-reverse">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-bold">
              {{ memberInfo.name ? memberInfo.name[0].toUpperCase() : 'U' }}
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">{{ memberInfo.name || memberInfo.username }}</h4>
              <p class="text-sm text-gray-600">@{{ memberInfo.username }}</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3 space-x-reverse">
          <button 
            @click="cancel"
            class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-3 rounded-lg font-medium transition-colors"
          >
            انصراف
          </button>
          <button 
            @click="confirm"
            class="flex-1 bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'تأیید عملیات'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'تأیید'
  },
  memberInfo: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['confirm', 'cancel']);

const confirm = () => {
  emit('confirm');
};

const cancel = () => {
  emit('cancel');
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
