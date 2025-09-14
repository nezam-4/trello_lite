<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40" @click.self="cancel">
    <div class="bg-white p-6 rounded w-full max-w-sm" dir="rtl">
      <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
      <input
        v-model="input"
        :placeholder="placeholder"
        class="w-full p-2 border rounded mb-4"
      />
      <div class="mb-4">
      <label class="block text-sm mb-1">نقش</label>
      <select v-model="role" class="w-full border p-2 rounded">
        <option value="member">عضو</option>
        <option value="admin">ادمین</option>
      </select>
    </div>
    <div class="flex justify-end space-x-2 rtl:space-x-reverse">
        <button @click="cancel" class="px-3 py-1 bg-gray-300 rounded">انصراف</button>
        <button @click="save" class="px-3 py-1 bg-blue-600 text-white rounded">ارسال</button>
      </div>
      <div v-if="errorMessages.length" class="mt-3 bg-red-50 border border-red-200 rounded p-2">
        <ul class="list-disc pr-5 text-red-700 text-sm space-y-1">
          <li v-for="(msg, idx) in errorMessages" :key="idx">{{ msg }}</li>
        </ul>
      </div>
      <p v-if="success" class="text-green-600 mt-2 text-sm">{{ success }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  visible: Boolean,
  type: { type: String, default: 'user' }, // 'user' or 'email'
  error: { type: [String, Object, Array], default: '' },
  success: String,
});
const emit = defineEmits(['cancel', 'submit']);
const role = ref('member');

const input = ref('');
watch(() => props.visible, (v) => { if (v) input.value = ''; });

const title = computed(() => props.type === 'user' ? 'دعوت کاربر موجود' : 'دعوت کاربر جدید با ایمیل');
const placeholder = computed(() => props.type === 'user' ? 'نام کاربری' : 'ایمیل');

const errorMessages = computed(() => flattenErrors(props.error));

function flattenErrors(err) {
  if (!err) return [];
  // If string, try to parse JSON, otherwise return as single message
  if (typeof err === 'string') {
    const s = err.trim();
    if ((s.startsWith('{') && s.endsWith('}')) || (s.startsWith('[') && s.endsWith(']'))) {
      try { return flattenErrors(JSON.parse(s)); } catch { return [s]; }
    }
    return [s];
  }
  // If array, flatten nested and stringify values
  if (Array.isArray(err)) {
    return err.flatMap(item => flattenErrors(item));
  }
  // If object, collect values (ignore keys)
  if (typeof err === 'object') {
    const vals = Object.values(err);
    if (!vals.length) return [];
    return vals.flatMap(v => flattenErrors(v));
  }
  // Fallback
  return [String(err)];
}

function cancel() { emit('cancel'); }
function save() { emit('submit', { value: input.value.trim(), role: role.value }); }
</script>
