<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40" @click.self="cancel">
    <div class="bg-white p-6 rounded w-full max-w-sm" dir="rtl">
      <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
      <input
        v-model="input"
        :placeholder="placeholder"
        class="w-full p-2 border rounded mb-4"
      />
      <div class="flex justify-end space-x-2 rtl:space-x-reverse">
        <button @click="cancel" class="px-3 py-1 bg-gray-300 rounded">انصراف</button>
        <button @click="save" class="px-3 py-1 bg-blue-600 text-white rounded">ارسال</button>
      </div>
      <p v-if="error" class="text-red-600 mt-2 text-sm">{{ error }}</p>
      <p v-if="success" class="text-green-600 mt-2 text-sm">{{ success }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  visible: Boolean,
  type: { type: String, default: 'user' }, // 'user' or 'email'
  error: String,
  success: String,
});
const emit = defineEmits(['cancel', 'submit']);

const input = ref('');
watch(() => props.visible, (v) => { if (v) input.value = ''; });

const title = props.type === 'user' ? 'دعوت کاربر موجود' : 'دعوت با ایمیل';
const placeholder = props.type === 'user' ? 'نام کاربری' : 'ایمیل';

function cancel() { emit('cancel'); }
function save() { emit('submit', input.value.trim()); }
</script>
