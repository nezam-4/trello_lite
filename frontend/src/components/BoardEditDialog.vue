<template>
  <!-- Modal overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm z-50 p-4"
    @click="$emit('cancel')"
  >
    <!-- Modal box -->
    <div 
      class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden transform transition-all duration-300 scale-100"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-white flex items-center gap-3">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            ویرایش برد
          </h2>
          <button
            @click="$emit('cancel')"
            class="text-white hover:text-gray-200 transition-colors p-1 rounded-full hover:bg-white hover:bg-opacity-20"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 max-h-[calc(90vh-140px)] overflow-y-auto">
        <form @submit.prevent="submit" class="space-y-6">
          <!-- Title Field -->
          <div class="space-y-2">
            <label class="block text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
              </svg>
              عنوان برد
            </label>
            <input
              v-model="form.title"
              type="text"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
              placeholder="نام برد را وارد کنید..."
              required
            />
          </div>

          <!-- Description Field -->
          <div class="space-y-2">
            <label class="block text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
              </svg>
              توضیحات
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white resize-none"
              placeholder="توضیحات برد را وارد کنید..."
            ></textarea>
          </div>

          <!-- Color Selection -->
          <div class="space-y-3">
            <label class="block text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"/>
              </svg>
              رنگ برد
            </label>
            
            <!-- Predefined Colors -->
            <div class="grid grid-cols-6 gap-3 mb-4">
              <button
                v-for="color in predefinedColors"
                :key="color"
                type="button"
                @click="form.color = color"
                :class="[
                  'w-10 h-10 rounded-xl border-2 transition-all duration-200 hover:scale-110',
                  form.color === color ? 'border-gray-800 ring-2 ring-blue-500' : 'border-gray-200 hover:border-gray-400'
                ]"
                :style="{ backgroundColor: color }"
              >
                <svg v-if="form.color === color" class="w-5 h-5 text-white mx-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
              </button>
            </div>

            <!-- Custom Color Input -->
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
              <input
                v-model="form.color"
                type="color"
                class="w-12 h-10 rounded-lg border-2 border-gray-200 cursor-pointer"
              />
              <input
                v-model="form.color"
                type="text"
                placeholder="#RRGGBB"
                class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>

          <!-- Public Checkbox -->
          <div class="flex items-center gap-3 p-4 bg-blue-50 rounded-xl">
            <input 
              v-model="form.is_public" 
              type="checkbox" 
              id="publicChk"
              class="w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
            />
            <label for="publicChk" class="text-sm font-medium text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              برد عمومی باشد
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-xl">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p class="text-red-700 text-sm font-medium">{{ error }}</p>
            </div>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-6 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          انصراف
        </button>
        <button
          @click="submit"
          class="px-6 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          ذخیره تغییرات
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';

const props = defineProps({
  board: { type: Object, default: null },
  visible: { type: Boolean, default: false },
  error: { type: String, default: '' }
});
const emit = defineEmits(['save', 'cancel']);

// Predefined color palette
const predefinedColors = [
  '#3B82F6', // Blue
  '#8B5CF6', // Purple
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#F97316', // Orange
  '#EC4899', // Pink
  '#6366F1', // Indigo
  '#14B8A6', // Teal
  '#84CC16', // Lime
  '#F43F5E', // Rose
  '#6B7280'  // Gray
];

const form = reactive({
  title: '',
  description: '',
  color: '#3B82F6',
  is_public: false
});

watch(
  () => props.board,
  (b) => {
    if (b) {
      form.title = b.title;
      form.description = b.description || '';
      form.color = b.color || '#3B82F6';
      form.is_public = b.is_public;
    }
  },
  { immediate: true }
);

function submit() {
  emit('save', { ...form });
}
</script>
