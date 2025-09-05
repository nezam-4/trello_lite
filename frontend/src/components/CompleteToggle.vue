<template>
  <button
    @click.stop="toggle"
    :class="[
      'w-5 h-5 border rounded flex items-center justify-center',
      isCompleted ? 'bg-green-500 text-white' : 'bg-white'
    ]"
    title="Toggle complete"
  >
    <span v-if="isCompleted">✓</span>
  </button>
</template>

<script setup>
import { computed } from 'vue';
import { useTasksStore } from '../stores/tasks';

const props = defineProps({
  taskId: {
    type: [Number, String],
    required: true,
  },
  modelValue: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

const tasksStore = useTasksStore();

const isCompleted = computed(() => props.modelValue);

async function toggle() {
  const updated = await tasksStore.toggleComplete(props.taskId);
  // emit to parent for local state update if needed
  emit('update:modelValue', updated.is_completed);
}
</script>
