<template>
  <div class="p-3 sm:p-4 lg:p-6 max-w-lg mx-auto" v-if="task">
    <h2 class="text-lg sm:text-xl lg:text-2xl font-bold mb-3 sm:mb-4">جزئیات تسک</h2>

    <label class="block text-xs sm:text-sm font-medium mb-1">عنوان</label>
    <input v-model="form.title" class="w-full p-2 sm:p-3 border rounded-lg mb-3 sm:mb-4 text-sm sm:text-base" />

    <label class="block text-xs sm:text-sm font-medium mb-1">توضیحات</label>
    <textarea v-model="form.description" rows="4" class="w-full p-2 sm:p-3 border rounded-lg mb-3 sm:mb-4 text-sm sm:text-base"></textarea>

    <label class="block text-xs sm:text-sm font-medium mb-1">اولویت</label>
    <select v-model="form.priority" class="w-full p-2 sm:p-3 border rounded-lg mb-3 sm:mb-4 text-sm sm:text-base">
      <option value="low">کم</option>
      <option value="medium">متوسط</option>
      <option value="high">زیاد</option>
      <option value="urgent">فوری</option>
    </select>

    <label class="block text-xs sm:text-sm font-medium mb-1">تاریخ سررسید</label>
    <input 
      v-model="form.due_date" 
      type="date" 
      class="w-full p-2 sm:p-3 border rounded-lg mb-2 text-sm sm:text-base"
      :class="{ 'border-red-500 bg-red-50': isOverdue }"
    />
    <div v-if="task.due_date" class="text-xs sm:text-sm text-gray-600 mb-2">
      {{ formatDueDateDisplay(task.due_date) }}
    </div>
    <div v-if="isOverdue" class="text-red-500 text-xs sm:text-sm mb-3 sm:mb-4 flex items-center">
      <span class="mr-1">⚠️</span>
      این تسک از تاریخ سررسید گذشته است
    </div>

    <div class="flex space-x-2 space-x-reverse">
      <button @click="save" class="px-3 sm:px-4 py-2 sm:py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm sm:text-base">ذخیره</button>
      <router-link :to="backUrl" class="px-3 sm:px-4 py-2 sm:py-2.5 bg-gray-300 rounded-lg hover:bg-gray-400 text-sm sm:text-base">بازگشت</router-link>
    </div>
  </div>
  <div v-else class="flex items-center justify-center h-screen">در حال بارگیری...</div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTasksStore } from '../stores/tasks';

const route = useRoute();
const router = useRouter();
const tasksStore = useTasksStore();
const id = route.params.id;

const task = ref(null);
const form = ref({ title: '', description: '', priority: 'medium', due_date: '' });

async function load() {
  const data = await tasksStore.fetchTask(id);
  task.value = data;
  form.value = {
    title: data.title,
    description: data.description || '',
    priority: data.priority,
    due_date: data.due_date ? formatDateForInput(data.due_date) : '',
  };
}

onMounted(load);
watch(() => route.params.id, load);

// Check if task is overdue
const isOverdue = computed(() => {
  if (!task.value?.due_date || task.value?.is_completed) return false;
  return new Date(task.value.due_date) < new Date();
});

// Format date for date input
function formatDateForInput(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  // Format for date input (YYYY-MM-DD)
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Format due date for display in Persian (date only)
function formatDueDateDisplay(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  
  const diffTime = taskDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return `امروز`;
  } else if (diffDays === 1) {
    return `فردا`;
  } else if (diffDays === -1) {
    return `دیروز`;
  } else if (diffDays > 0) {
    return `${diffDays} روز دیگر - ${date.toLocaleDateString('fa-IR')}`;
  } else {
    return `${Math.abs(diffDays)} روز پیش - ${date.toLocaleDateString('fa-IR')}`;
  }
}

async function save() {
  const updateData = { ...form.value };
  // Keep date format as YYYY-MM-DD for API
  if (updateData.due_date) {
    updateData.due_date = updateData.due_date; // Already in YYYY-MM-DD format
  } else {
    updateData.due_date = null;
  }
  await tasksStore.updateTask(id, updateData);
  await load();
  // Optionally toast success
}

// Compute backUrl safely after task is loaded
const backUrl = computed(() => {
  return router.currentRoute.value.query.back || `/boards/${task.value?.board || ''}`;
});
</script>
