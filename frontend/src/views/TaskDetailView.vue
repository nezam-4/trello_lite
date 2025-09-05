<template>
  <div class="p-4 max-w-lg mx-auto" v-if="task">
    <h2 class="text-xl font-bold mb-4">جزئیات تسک</h2>

    <label class="block text-sm">عنوان</label>
    <input v-model="form.title" class="w-full p-2 border rounded mb-4" />

    <label class="block text-sm">توضیحات</label>
    <textarea v-model="form.description" rows="4" class="w-full p-2 border rounded mb-4"></textarea>

    <label class="block text-sm">اولویت</label>
    <select v-model="form.priority" class="w-full p-2 border rounded mb-4">
      <option value="low">Low</option>
      <option value="medium">Medium</option>
      <option value="high">High</option>
      <option value="urgent">Urgent</option>
    </select>

    <div class="flex space-x-2">
      <button @click="save" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">ذخیره</button>
      <router-link :to="backUrl" class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400">بازگشت</router-link>
    </div>
  </div>
  <div v-else class="flex items-center justify-center h-screen">در حال بارگیری...</div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTasksStore } from '../stores/tasks';

const route = useRoute();
const router = useRouter();
const tasksStore = useTasksStore();
const id = route.params.id;

const task = ref(null);
const form = ref({ title: '', description: '', priority: 'medium' });

async function load() {
  const data = await tasksStore.fetchTask(id);
  task.value = data;
  form.value = {
    title: data.title,
    description: data.description || '',
    priority: data.priority,
  };
}

onMounted(load);
watch(() => route.params.id, load);

async function save() {
  await tasksStore.updateTask(id, { ...form.value });
  await load();
  // Optionally toast success
}

const backUrl = router.currentRoute.value.query.back || `/boards/${task.value?.board || ''}`;
</script>
