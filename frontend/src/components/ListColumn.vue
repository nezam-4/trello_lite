<template>
  <div class="bg-gray-200 rounded p-4 w-64 mr-4 flex-shrink-0">
    <h2 class="font-bold mb-2">{{ list.title }}</h2>
    <CardItem v-for="task in tasks" :key="task.id" :card="task" />

    <!-- Add Task Section -->
    <div v-if="adding" class="mt-2">
      <input
        v-model="newTitle"
        @keyup.enter="submit"
        @blur="cancel"
        class="w-full p-2 border rounded"
        placeholder="عنوان تسک..."
        autofocus
      />
    </div>
    <button
      v-else
      @click="adding = true"
      class="mt-2 w-full bg-gray-300 hover:bg-gray-400 text-sm py-1 rounded"
    >
      + Add Task
    </button>
  </div>
</template>

<script setup>
import { onMounted, computed, watch, ref } from 'vue';
import { useTasksStore } from '../stores/tasks';
import CardItem from './CardItem.vue';

const props = defineProps({
  list: {
    type: Object,
    required: true,
  },
});

const tasksStore = useTasksStore();

// Fetch tasks when component mounts and when list id changes
const fetch = () => tasksStore.fetchTasks(props.list.id);

onMounted(fetch);
watch(() => props.list.id, fetch);

const tasks = computed(() => tasksStore.tasks(props.list.id));

// add task state
const adding = ref(false);
const newTitle = ref('');

async function submit() {
  if (!newTitle.value.trim()) {
    cancel();
    return;
  }
  await tasksStore.createTask(props.list.id, newTitle.value.trim());
  newTitle.value = '';
  adding.value = false;
}
function cancel() {
  adding.value = false;
  newTitle.value = '';
}
</script>
