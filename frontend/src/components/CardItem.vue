<template>
  <div
    class="bg-white p-2 rounded shadow mb-2 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
    @click="goDetail"
  >
    <span class="truncate mr-2">{{ card.title }}</span>
    <button
      @click.stop="toggle"
      :class="['w-5 h-5 border rounded flex-shrink-0 flex items-center justify-center', card.is_completed ? 'bg-green-500 text-white' : 'bg-white']"
      title="Toggle complete"
    >
      <span v-if="card.is_completed">✓</span>
    </button>
  </div>
</template>

<script setup>
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
</script>
