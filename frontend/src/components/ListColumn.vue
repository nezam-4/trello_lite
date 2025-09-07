<template>
  <div :class="listBackgroundClass" class="rounded p-4 w-64 mr-4 flex-shrink-0">
    <div class="flex items-center justify-between mb-2">
      <h2 
        v-if="!editing" 
        @click="startEdit"
        class="font-bold cursor-pointer hover:bg-gray-300 px-2 py-1 rounded transition-colors"
      >
        {{ list.title }}
      </h2>
      <input 
        v-else
        ref="editInput"
        v-model="editTitle"
        @keyup.enter="saveEdit"
        @blur="saveEdit"
        @keyup.escape="cancelEdit"
        class="font-bold bg-white border border-blue-500 px-2 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <div class="relative">
        <button 
          @click="toggleMenu"
          class="p-1 hover:bg-gray-300 rounded transition-colors"
          :class="{ 'bg-gray-300': showMenu }"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
          </svg>
        </button>
        
        <!-- Dropdown Menu -->
        <div 
          v-if="showMenu" 
          class="absolute left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border z-10"
          @click.stop
        >
          <div class="py-1">
            <button 
              @click="refreshList"
              class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              بروزرسانی لیست
            </button>
            <button 
              @click="startEditFromMenu"
              class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              ویرایش نام
            </button>
            <button 
              @click="toggleColorPicker"
              class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM7 3H5a2 2 0 00-2 2v12a4 4 0 004 4h2a2 2 0 002-2V5a2 2 0 00-2-2z"/>
              </svg>
              تغییر رنگ
            </button>
            <hr class="my-1">
            <button 
              @click="deleteList"
              class="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              حذف لیست
            </button>
          </div>
        </div>
        
        <!-- Color Picker Modal -->
        <div 
          v-if="showColorPicker" 
          class="absolute left-0 mt-1 w-56 bg-white rounded-lg shadow-lg border z-20"
          @click.stop
        >
          <div class="p-4">
            <h3 class="text-sm font-medium mb-3">انتخاب رنگ پس‌زمینه</h3>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="color in availableColors"
                :key="color.value"
                @click="changeColor(color.value)"
                :class="[
                  'w-10 h-10 rounded-lg border-2 transition-all duration-200 hover:scale-110',
                  list.color === color.value ? 'border-gray-800 ring-2 ring-blue-500' : 'border-gray-300'
                ]"
                :style="{ backgroundColor: color.bg }"
                :title="color.name"
              >
                <span v-if="list.color === color.value" class="text-white text-xs">✓</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
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
import { onMounted, computed, watch, ref, nextTick, onUnmounted } from 'vue';
import { useTasksStore } from '../stores/tasks';
import { useListsStore } from '../stores/lists';
import CardItem from './CardItem.vue';

const props = defineProps({
  list: {
    type: Object,
    required: true,
  },
});

const tasksStore = useTasksStore();
const listsStore = useListsStore();
const taskContainer = ref();
const showMenu = ref(false);
const showColorPicker = ref(false);
const editing = ref(false);
const editTitle = ref('');
const editInput = ref();

// Available colors for list backgrounds
const availableColors = [
  { value: 'blue', name: 'آبی', bg: '#dbeafe' },
  { value: 'green', name: 'سبز', bg: '#dcfce7' },
  { value: 'yellow', name: 'زرد', bg: '#fef3c7' },
  { value: 'red', name: 'قرمز', bg: '#fee2e2' },
  { value: 'purple', name: 'بنفش', bg: '#e9d5ff' },
  { value: 'pink', name: 'صورتی', bg: '#fce7f3' },
  { value: 'indigo', name: 'نیلی', bg: '#e0e7ff' },
  { value: 'gray', name: 'خاکستری', bg: '#f3f4f6' },
  { value: 'orange', name: 'نارنجی', bg: '#fed7aa' },
  { value: 'teal', name: 'سبز آبی', bg: '#ccfbf1' },
  { value: 'cyan', name: 'فیروزه‌ای', bg: '#cffafe' },
  { value: 'lime', name: 'لیمویی', bg: '#ecfccb' }
];

// Computed property for list background class
const listBackgroundClass = computed(() => {
  const colorMap = {
    blue: 'bg-blue-100',
    green: 'bg-green-100', 
    yellow: 'bg-yellow-100',
    red: 'bg-red-100',
    purple: 'bg-purple-100',
    pink: 'bg-pink-100',
    indigo: 'bg-indigo-100',
    gray: 'bg-gray-200',
    orange: 'bg-orange-100',
    teal: 'bg-teal-100',
    cyan: 'bg-cyan-100',
    lime: 'bg-lime-100'
  };
  
  return colorMap[props.list.color] || 'bg-gray-200';
});

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

// Menu functionality
function toggleMenu() {
  showMenu.value = !showMenu.value;
}

function closeMenu() {
  showMenu.value = false;
  showColorPicker.value = false;
}

// Menu actions
async function refreshList() {
  closeMenu();
  await fetch();
}

// Color picker functionality
function toggleColorPicker() {
  showMenu.value = false;
  showColorPicker.value = !showColorPicker.value;
}

async function changeColor(colorValue) {
  try {
    await listsStore.updateList(props.list.id, { color: colorValue });
    showColorPicker.value = false;
  } catch (error) {
    console.error('Failed to update list color:', error);
  }
}

// List editing functionality
function startEdit() {
  editing.value = true;
  editTitle.value = props.list.title;
  nextTick(() => {
    if (editInput.value) {
      editInput.value.focus();
      editInput.value.select();
    }
  });
}

function startEditFromMenu() {
  closeMenu();
  startEdit();
}

async function saveEdit() {
  if (!editTitle.value.trim()) {
    cancelEdit();
    return;
  }
  
  if (editTitle.value.trim() === props.list.title) {
    cancelEdit();
    return;
  }
  
  try {
    await listsStore.updateList(props.list.id, { title: editTitle.value.trim() });
    editing.value = false;
  } catch (error) {
    console.error('Failed to update list title:', error);
    // Optionally show error message to user
    cancelEdit();
  }
}

function cancelEdit() {
  editing.value = false;
  editTitle.value = '';
}

async function deleteList() {
  closeMenu();
  if (confirm(`آیا مطمئن هستید که می‌خواهید لیست "${props.list.title}" را حذف کنید؟`)) {
    try {
      await listsStore.deleteList(props.list.id);
    } catch (error) {
      console.error('Failed to delete list:', error);
      // Optionally show error message to user
    }
  }
}

// Close menu when clicking outside
function handleClickOutside(event) {
  if ((showMenu.value || showColorPicker.value) && !event.target.closest('.relative')) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
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
