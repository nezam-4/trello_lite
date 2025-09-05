<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="close"
  >
    <div
      class="bg-white relative p-6 rounded w-full max-w-5xl max-h-[90vh] overflow-y-auto"
    >
      <button
        class="absolute top-4 right-4 text-gray-500 hover:text-black"
        @click="close"
      >
        ✕
      </button>

      <div class="flex gap-6">
        <!-- Left column -->
        <div class="flex-1">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2 rtl:space-x-reverse">
            <h2 class="text-xl font-bold">جزئیات تسک</h2>
            </div>
            <button
                            @click.stop="toggle"
              :class="[
                'w-5 h-5 border rounded flex-shrink-0 flex items-center justify-center',
                task.is_completed ? 'bg-green-500 text-white' : 'bg-white'
              ]"
            >
              <span v-if="task.is_completed">✓</span>
            </button>
          </div>

          <label class="block text-sm">عنوان</label>
          <input v-model="form.title" class="w-full p-2 border rounded mb-4" />

          <label class="block text-sm">توضیحات</label>
          <textarea
            v-model="form.description"
            rows="4"
            class="w-full p-2 border rounded mb-4"
          ></textarea>

          <label class="block text-sm">اولویت</label>
          <select v-model="form.priority" class="w-full p-2 border rounded mb-4">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>

          <div class="flex space-x-2 my-4">
            <button
              @click="save"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              ذخیره
            </button>
          </div>
        </div>

        <!-- Right column: Activity -->
        <div class="w-1/3 border-l pl-4">
          <h3 class="font-semibold mb-2">Activity</h3>
          <p class="text-sm text-gray-500">(به‌زودی)</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useTasksStore } from '../stores/tasks';

const tasksStore = useTasksStore();

const { currentTask: task } = storeToRefs(tasksStore);
const form = reactive({ title: '', description: '', priority: 'medium' });

watch(task, (t) => {
  if (t) {
    form.title = t.title;
    form.description = t.description || '';
    form.priority = t.priority;
  }
}, { immediate: true });

async function save() {
  await tasksStore.updateTask(task.value.id, { ...form });
}

function close() {
  tasksStore.closeTask();
}
// Old toggle function kept for compatibility (not used anymore)
async function toggle() {
  if (!task.value) return;
  const updated = await tasksStore.toggleComplete(task.value.id);
  Object.assign(task.value, updated);
}

</script>
