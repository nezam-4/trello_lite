<template>
  <div
    class="bg-white p-2 rounded shadow mb-2 hover:bg-gray-50 cursor-grab active:cursor-grabbing transition-all duration-200 hover:shadow-md"
    @click="goDetail"
    :data-task-id="card.id"
  >
    <div class="flex items-center justify-between mb-1">
      <span class="truncate mr-2">{{ card.title }}</span>
      <button
        @click.stop="toggle"
        :class="['w-5 h-5 border rounded flex-shrink-0 flex items-center justify-center', card.is_completed ? 'bg-green-500 text-white' : 'bg-white']"
        title="Toggle complete"
      >
        <span v-if="card.is_completed">✓</span>
      </button>
    </div>
    
    <!-- Due date indicator -->
    <div v-if="card.due_date" class="flex items-center mb-1">
      <span 
        :class="[
          'text-xs px-2 py-1 rounded flex items-center',
          isOverdue ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
        ]"
      >
        <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
        </svg>
        {{ formatDueDate(card.due_date) }}
        <span v-if="isOverdue" class="mr-1">⚠️</span>
      </span>
    </div>
    
    <!-- Assigned users circles -->
    <div v-if="card.assigned_users && card.assigned_users.length > 0" class="flex items-center space-x-1 rtl:space-x-reverse">
      <div
        v-for="user in card.assigned_users"
        :key="user.id"
        class="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-semibold"
        :title="user.full_name || user.username"
      >
        {{ user.initials }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTasksStore } from '../stores/tasks';

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const tasksStore = useTasksStore();

function goDetail() {
  tasksStore.openTask(props.card.id);
}

async function toggle() {
  await tasksStore.toggleComplete(props.card.id);
}

// Check if task is overdue
const isOverdue = computed(() => {
  if (!props.card.due_date || props.card.is_completed) return false;
  return new Date(props.card.due_date) < new Date();
});

// Format due date for display
function formatDueDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = date - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return 'امروز';
  } else if (diffDays === 1) {
    return 'فردا';
  } else if (diffDays === -1) {
    return 'دیروز';
  } else if (diffDays > 1 && diffDays <= 7) {
    return `${diffDays} روز دیگر`;
  } else if (diffDays < -1 && diffDays >= -7) {
    return `${Math.abs(diffDays)} روز پیش`;
  } else {
    // Format as Persian date
    return date.toLocaleDateString('fa-IR', {
      month: 'short',
      day: 'numeric'
    });
  }
}
</script>
