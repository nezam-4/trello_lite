<template>
  <div
    class="bg-white p-2 sm:p-3 rounded-lg shadow-sm mb-2 hover:bg-gray-50 cursor-grab active:cursor-grabbing transition-all duration-200 hover:shadow-md border border-gray-100"
    @click="goDetail"
    :data-task-id="card.id"
  >
    <div class="flex items-center justify-between mb-1">
      <span class="truncate mr-2 text-sm sm:text-base font-medium text-gray-900">{{ card.title }}</span>
      <button
        @click.stop="toggle"
        :class="['w-4 h-4 sm:w-5 sm:h-5 border rounded flex-shrink-0 flex items-center justify-center text-xs', card.is_completed ? 'bg-green-500 text-white border-green-500' : 'bg-white border-gray-300 hover:border-gray-400']"
        title="Toggle complete"
      >
        <span v-if="card.is_completed">✓</span>
      </button>
    </div>
    
    <!-- Priority and Due date row -->
    <div class="flex items-center justify-between mb-2 gap-2">
      <!-- Priority indicator -->
      <div v-if="card.priority" class="flex items-center flex-shrink-0">
        <span 
          :class="[
            'text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full font-medium flex items-center',
            getPriorityClass(card.priority)
          ]"
        >
          <svg class="w-2.5 h-2.5 sm:w-3 sm:h-3 ml-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clip-rule="evenodd"/>
          </svg>
          <span class="hidden sm:inline">{{ getPriorityText(card.priority) }}</span>
        </span>
      </div>
      
      <!-- Due date indicator -->
      <div v-if="card.due_date" class="flex items-center flex-shrink-0">
        <span 
          :class="[
            'text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded flex items-center',
            isOverdue ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
          ]"
        >
          <svg class="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
          </svg>
          <span class="hidden sm:inline">{{ formatDueDate(card.due_date) }}</span>
          <span class="sm:hidden">{{ formatDueDateShort(card.due_date) }}</span>
          <span v-if="isOverdue" class="mr-1">⚠️</span>
        </span>
      </div>
    </div>
    
    <!-- Assigned users circles -->
    <div v-if="card.assigned_users && card.assigned_users.length > 0" class="flex items-center space-x-1 rtl:space-x-reverse">
      <UserAvatar
        v-for="user in card.assigned_users.slice(0, 3)"
        :key="user.id"
        :user="user"
        size="sm"
        @click="handleUserClick(user)"
      />
      <div 
        v-if="card.assigned_users.length > 3"
        class="w-8 h-8 rounded-full bg-gray-400 text-white flex items-center justify-center text-xs font-semibold border-2 border-white shadow-sm"
        :title="`${card.assigned_users.length - 3} نفر دیگر`"
      >
        +{{ card.assigned_users.length - 3 }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTasksStore } from '../stores/tasks';
import UserAvatar from './UserAvatar.vue';

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['userClick']);

const tasksStore = useTasksStore();

function goDetail() {
  tasksStore.openTask(props.card.id);
}

async function toggle() {
  await tasksStore.toggleComplete(props.card.id);
}

function handleUserClick(user) {
  emit('userClick', { user, task: props.card });
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

// Format due date for mobile (shorter version)
function formatDueDateShort(dateString) {
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
  } else if (diffDays > 0 && diffDays <= 7) {
    return `${diffDays}روز`;
  } else if (diffDays < 0 && diffDays >= -7) {
    return `${Math.abs(diffDays)}روز پیش`;
  } else {
    // Format as short Persian date
    return date.toLocaleDateString('fa-IR', {
      month: 'numeric',
      day: 'numeric'
    });
  }
}

// Get priority class for styling
function getPriorityClass(priority) {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

// Get priority text in Persian
function getPriorityText(priority) {
  switch (priority) {
    case 'urgent':
      return 'فوری';
    case 'high':
      return 'بالا';
    case 'medium':
      return 'متوسط';
    case 'low':
      return 'پایین';
    default:
      return 'نامشخص';
  }
}
</script>
