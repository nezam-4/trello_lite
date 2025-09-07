<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50" @click.self="close">
    <div class="bg-gray-100 rounded-lg shadow-xl w-96 max-h-[70vh] overflow-y-auto p-6" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">اعضای برد</h3>
        <button @click="close" class="text-gray-600 hover:text-gray-700">✕</button>
      </div>
      <ul class="space-y-3">
        <li v-for="m in members" :key="m.id" class="py-3 px-3 bg-white rounded shadow text-sm flex flex-col gap-1">
          <div class="flex justify-between items-start">
            <span class="font-medium">{{ m.full_name || m.username }}</span>
            <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="{
                    'bg-indigo-100 text-indigo-700': m.role==='admin',
                    'bg-emerald-100 text-emerald-700': m.role==='member',
                    'bg-orange-100 text-orange-700': m.role==='owner'
                  }">
              {{ m.role }}
            </span>
          </div>
          <p class="text-xs text-gray-600">{{ m.email }}</p>
          <p class="text-xs text-gray-500">وضعیت: {{ m.status }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: Boolean,
  members: { type: Array, default: () => [] }
});
const emit = defineEmits(['close']);
function close() { emit('close'); }
</script>
