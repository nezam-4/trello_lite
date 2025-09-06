<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
    <div class="bg-gray-100 rounded-lg shadow-xl w-96 max-h-[70vh] overflow-y-auto p-6" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">تاریخچه فعالیت‌ها</h3>
        <button @click="$emit('close')" class="text-gray-600 hover:text-gray-700">✕</button>
      </div>
      <ul class="space-y-3">
        <li v-for="act in activities" :key="act.id" class="py-3 px-3 bg-gray-50 rounded shadow text-sm flex flex-col gap-1">
          <div class="flex justify-between">
            <span class="font-medium">{{ act.user_username || 'سیستم' }}</span>
            <span class="text-xs text-gray-600">{{ formatDate(act.created_at) }}</span>
          </div>
          <p class="text-gray-800">{{ act.action_display }} - {{ act.description }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: Boolean,
  activities: { type: Array, default: () => [] }
});
const emit = defineEmits(['close']);

function formatDate(val) {
  try {
    return new Date(val).toLocaleString('fa-IR', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit'
    });
  } catch {
    return val;
  }
}
</script>
