<template>
  <div class="bg-gray-200 rounded p-4 w-64 mr-4 flex-shrink-0">
    <h2 class="font-bold mb-2">{{ list.title }}</h2>
    
    <!-- Draggable Tasks -->
    <div 
      ref="taskContainer"
      class="min-h-[20px] transition-all duration-200"
    >
      <CardItem 
        v-for="task in tasks" 
        :key="task.id" 
        :card="task" 
        class="draggable-task"
      />
    </div>

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
import { onMounted, computed, watch, ref, nextTick } from 'vue';
import { useTasksStore } from '../stores/tasks';
import CardItem from './CardItem.vue';

const props = defineProps({
  list: {
    type: Object,
    required: true,
  },
});

const tasksStore = useTasksStore();
const taskContainer = ref();

// Fetch tasks when component mounts and when list id changes
const fetch = () => tasksStore.fetchTasks(props.list.id);

onMounted(async () => {
  await fetch();
  await nextTick();
  initializeSortable();
});

watch(() => props.list.id, async () => {
  await fetch();
  await nextTick();
  initializeSortable();
});

const tasks = computed(() => tasksStore.tasks(props.list.id));

// Initialize sortable functionality
function initializeSortable() {
  if (!taskContainer.value) return;
  
  import('sortablejs').then(({ default: Sortable }) => {
    new Sortable(taskContainer.value, {
      group: 'tasks',
      animation: 200,
      ghostClass: 'ghost-task',
      chosenClass: 'chosen-task',
      dragClass: 'drag-task',
      onAdd: async (evt) => {
        try {
          const taskId = evt.item.getAttribute('data-task-id');
          const newIndex = evt.newIndex;
          console.log('Moving task', taskId, 'to list', props.list.id, 'at position', newIndex + 1);
          await tasksStore.moveTask(parseInt(taskId), props.list.id, newIndex + 1);
        } catch (error) {
          console.error('Failed to move task:', error);
          await fetch();
        }
      },
      onUpdate: async (evt) => {
        try {
          const taskId = evt.item.getAttribute('data-task-id');
          const newIndex = evt.newIndex;
          console.log('Reordering task', taskId, 'to position', newIndex + 1);
          await tasksStore.moveTask(parseInt(taskId), null, newIndex + 1);
        } catch (error) {
          console.error('Failed to move task:', error);
          await fetch();
        }
      }
    });
  });
}

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

<style scoped>
/* Drag and drop visual feedback */
.ghost-task {
  opacity: 0.5;
  background: #e2e8f0;
  border: 2px dashed #cbd5e0;
}

.chosen-task {
  cursor: grabbing !important;
  transform: rotate(5deg);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.drag-task {
  opacity: 0.8;
  transform: rotate(5deg);
}

/* Smooth transitions for task movements */
.draggable-item {
  transition: all 0.2s ease;
}

/* Drop zone highlighting */
.min-h-\[20px\]:empty {
  background: linear-gradient(45deg, transparent 40%, rgba(59, 130, 246, 0.1) 50%, transparent 60%);
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  min-height: 40px;
}

/* Draggable task styling */
.draggable-task {
  cursor: grab;
}

.draggable-task:active {
  cursor: grabbing;
}
</style>
