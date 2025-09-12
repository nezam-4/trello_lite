<template>
  <div 
    v-if="visible" 
    class="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-50 p-4"
    @click.self="$emit('cancel')"
  >
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col" @click.stop>
      <!-- Header -->
      <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3 space-x-reverse">
            <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <h2 class="text-xl font-bold text-gray-900">ایجاد برد جدید</h2>
          </div>
          <button 
            @click="$emit('cancel')"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="error" class="p-6 pt-6">
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
            {{ error }}
          </div>
        </div>
        <form @submit.prevent="submit" class="p-6 space-y-6">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">عنوان برد</label>
          <input 
            v-model="form.title" 
            type="text" 
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200" 
            placeholder="نام برد را وارد کنید..."
            required 
          />
          <p v-if="errors && errors.title" class="mt-2 text-sm text-red-600">
            {{ formatErr(errors.title) }}
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">توضیحات</label>
          <textarea 
            v-model="form.description" 
            rows="3" 
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
            placeholder="توضیحات برد (اختیاری)..."
          ></textarea>
          <p v-if="errors && errors.description" class="mt-2 text-sm text-red-600">
            {{ formatErr(errors.description) }}
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-3">رنگ برد</label>
          <div class="grid grid-cols-6 gap-3 mb-4">
            <button
              v-for="color in predefinedColors"
              :key="color"
              type="button"
              @click="form.color = color"
              :class="[
                'w-12 h-12 rounded-xl border-3 transition-all duration-200 hover:scale-110 hover:shadow-lg',
                form.color === color ? 'border-gray-800 ring-2 ring-gray-400' : 'border-gray-200 hover:border-gray-300'
              ]"
              :style="{ backgroundColor: color }"
            >
              <svg v-if="form.color === color" class="w-6 h-6 mx-auto text-white drop-shadow-lg" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </button>
          </div>
          <div class="flex items-center space-x-3 space-x-reverse">
            <input 
              v-model="form.color" 
              type="color" 
              class="w-12 h-12 border-2 border-gray-300 rounded-xl cursor-pointer hover:border-blue-500 transition-colors" 
            />
            <input 
              v-model="form.color" 
              type="text" 
              placeholder="#3B82F6" 
              class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200" 
            />
          </div>
          <p v-if="errors && errors.color" class="mt-2 text-sm text-red-600">
            {{ formatErr(errors.color) }}
          </p>
        </div>
        
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-100">
          <div class="flex items-start space-x-3 space-x-reverse">
            <input 
              v-model="form.is_public" 
              type="checkbox" 
              id="publicNewChk" 
              class="w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 mt-0.5"
            />
            <div class="flex-1">
              <label for="publicNewChk" class="text-sm font-semibold text-gray-800 cursor-pointer block mb-1">
                برد عمومی
              </label>
              <p class="text-xs text-gray-600">
                همه کاربران می‌توانند این برد را مشاهده کنند و به آن دسترسی داشته باشند
              </p>
            </div>
            <div class="text-blue-500">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
          </div>
        </div>
        <p v-if="errors && errors.is_public" class="text-sm text-red-600">
          {{ formatErr(errors.is_public) }}
        </p>
        
        </form>
      </div>
      
      <!-- Fixed Footer with Buttons -->
      <div class="border-t border-gray-200 p-6 bg-gray-50">
        <div class="flex space-x-3 space-x-reverse">
          <button 
            type="button" 
            @click="$emit('cancel')" 
            class="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-medium transition-all duration-200"
          >
            انصراف
          </button>
          <button 
            type="submit" 
            @click="submit"
            class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
          >
            ایجاد برد
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  visible: { type: Boolean, default: false },
  error: { type: String, default: '' },
  errors: { type: Object, default: null }
});
const emit = defineEmits(['submit', 'cancel']);

const predefinedColors = [
  '#3B82F6', // Blue
  '#8B5CF6', // Purple  
  '#10B981', // Emerald
  '#F59E0B', // Amber
  '#EF4444', // Red
  '#EC4899', // Pink
  '#6366F1', // Indigo
  '#14B8A6', // Teal
  '#F97316', // Orange
  '#84CC16', // Lime
  '#6B7280', // Gray
  '#1F2937'  // Dark Gray
];

const form = reactive({
  title: '',
  description: '',
  color: '#3B82F6',
  is_public: false
});

function submit() {
  emit('submit', { ...form });
  // Reset form after submission
  form.title = '';
  form.description = '';
  form.color = '#3B82F6';
  form.is_public = false;
}

function formatErr(val) {
  if (!val) return '';
  if (Array.isArray(val)) return val.join('، ');
  return typeof val === 'string' ? val : String(val);
}
</script>
