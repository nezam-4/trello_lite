<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
    <div class="bg-gray-100 rounded-lg shadow-xl w-96 max-h-[70vh] overflow-y-auto p-6" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">دعوت‌های برد</h3>
        <button @click="$emit('close')" class="text-gray-600 hover:text-gray-700">✕</button>
      </div>
      <ul class="space-y-3">
        <li v-for="inv in invitations" :key="inv.id" class="py-3 px-3 bg-white rounded shadow text-sm flex flex-col gap-1">
          <div class="flex justify-between">
            <span class="font-medium">{{ inv.invited_email || inv.user_username }}</span>
            <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="{
                    'bg-amber-100 text-amber-700': inv.status==='pending',
                    'bg-emerald-100 text-emerald-700': inv.status==='accepted',
                    'bg-red-100 text-red-700 line-through': inv.status==='rejected'
                  }">
              {{ inv.status === 'pending' ? 'در انتظار' : inv.status === 'accepted' ? 'پذیرفته' : 'رد شده' }}
            </span>
          </div>
          <div class="flex justify-between text-xs text-gray-600">
            <span>نقش: {{ inv.role }}</span>
            <span>{{ new Date(inv.created_at).toLocaleDateString('fa-IR') }}</span>
          </div>
          <p class="text-xs text-gray-500">ارسال‌کننده: {{ inv.invited_by_username || 'سیستم' }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: Boolean,
  invitations: { type: Array, default: () => [] }
});
const emit = defineEmits(['close']);
</script>
