<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
    <div class="bg-white rounded shadow-lg w-80 p-6" @click.stop>
      <h3 class="text-lg font-bold mb-4 text-center">تأیید حذف</h3>
      <p class="text-sm mb-6 text-center">{{ message }}</p>
      <div class="flex justify-center gap-4">
        <button @click="$emit('cancel')" class="px-4 py-1 text-sm border rounded">انصراف</button>
        <button @click="$emit('confirm')" class="px-4 py-1 text-sm bg-red-600 text-white rounded">حذف</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: 'آیا از حذف مطمئن هستید؟' }
});
const emit = defineEmits(['confirm', 'cancel']);
</script>
