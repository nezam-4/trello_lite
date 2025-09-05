<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-30">
    <div class="bg-white rounded shadow-lg w-96 p-6" @click.stop>
      <h2 class="text-lg font-bold mb-4 text-center">ایجاد برد جدید</h2>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="block text-sm mb-1">عنوان</label>
          <input v-model="form.title" type="text" class="w-full border rounded px-2 py-1" required />
        </div>
        <div class="mb-3">
          <label class="block text-sm mb-1">توضیحات</label>
          <textarea v-model="form.description" rows="2" class="w-full border rounded px-2 py-1"></textarea>
        </div>
        <div class="mb-3">
          <label class="block text-sm mb-1">رنگ</label>
          <div class="flex items-center gap-2">
            <input v-model="form.color" type="color" class="w-10 h-8 p-0 border rounded" />
            <input v-model="form.color" type="text" placeholder="#RRGGBB" class="flex-1 border rounded px-2 py-1" />
          </div>
        </div>
        <div class="mb-4 flex items-center gap-2">
          <input v-model="form.is_public" type="checkbox" id="publicNewChk" />
          <label for="publicNewChk" class="text-sm">عمومی باشد</label>
        </div>
        <p v-if="error" class="text-red-600 text-sm mb-2">{{ error }}</p>
        <div class="flex justify-end gap-2">
          <button type="button" @click="$emit('cancel')" class="px-3 py-1 text-sm border rounded">انصراف</button>
          <button type="submit" class="px-3 py-1 text-sm bg-sky-600 text-white rounded">ایجاد</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  visible: { type: Boolean, default: false },
  error: { type: String, default: '' }
});
const emit = defineEmits(['save', 'cancel']);

const form = reactive({
  title: '',
  description: '',
  color: '#ffffff',
  is_public: false
});

function submit() {
  emit('save', { ...form });
  // Keep form values for convenience; parent will close dialog
}
</script>
