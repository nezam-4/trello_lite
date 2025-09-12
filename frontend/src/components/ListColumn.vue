<template>
  <div class="w-72 sm:w-80 lg:w-96 flex-shrink-0 min-w-0">
    <div :class="['bg-white rounded-xl lg:rounded-2xl shadow-sm border border-gray-200/50 overflow-visible border-l-4', listAccentColor]">
      <!-- List Header -->
      <div class="px-4 sm:px-5 lg:px-6 py-3 sm:py-4 lg:py-5 border-b border-gray-100">
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <h2 
              v-if="!editing" 
              @click="startEdit"
              class="font-bold text-gray-900 cursor-pointer hover:bg-gray-100 px-2 py-1 -mx-2 rounded-lg transition-all duration-200 text-base sm:text-lg lg:text-xl truncate"
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
              class="font-bold text-base sm:text-lg lg:text-xl bg-white border-2 border-blue-500 px-2 py-1 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 w-full"
            />
            <div class="flex items-center space-x-1 space-x-reverse mt-1 sm:mt-2">
              <svg class="w-3 h-3 sm:w-4 sm:h-4 lg:w-5 lg:h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              <p class="text-xs sm:text-sm lg:text-base text-gray-500">{{ tasks.length }} تسک</p>
            </div>
          </div>
          
          <div ref="menuWrapper" class="relative flex-shrink-0">
            <button 
              ref="menuButton"
              @click="toggleMenu"
              class="p-2 sm:p-2.5 lg:p-3 hover:bg-gray-100 rounded-lg transition-all duration-200 text-gray-500 hover:text-gray-700"
              :class="{ 'bg-gray-100 text-gray-700': showMenu }"
            >
              <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
              </svg>
            </button>
        
            <!-- Dropdown Menu -->
            <div 
              v-if="showMenu" 
              ref="menuEl"
              :class="[
                'absolute z-[9999] w-52 sm:w-56 lg:w-60 bg-white rounded-xl shadow-lg border border-gray-200/50 py-2',
                menuAlignLeft ? 'left-0' : 'right-0',
                menuDropUp ? 'bottom-full mb-2' : 'top-full mt-2'
              ]"
              @click.stop
            >
              <button 
                @click="startEditFromMenu"
                class="flex items-center space-x-3 space-x-reverse w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
                <span>ویرایش لیست</span>
              </button>
              
              <button 
                @click="toggleColorPicker"
                class="flex items-center space-x-3 space-x-reverse w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM7 3H5a2 2 0 00-2 2v12a4 4 0 004 4h2a2 2 0 002-2V5a2 2 0 00-2-2z"/>
                </svg>
                <span>تغییر رنگ پس‌زمینه</span>
              </button>
              
              <hr class="my-2">
              
              <button 
                @click="deleteList"
                class="flex items-center space-x-3 space-x-reverse w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                <span>حذف لیست</span>
              </button>
            </div>
        
            <!-- Color Picker Modal -->
            <div 
              v-if="showColorPicker" 
              ref="colorPickerEl"
              :class="[
                'absolute z-[9999] w-64 sm:w-72 lg:w-80 bg-white rounded-xl shadow-lg border border-gray-200/50',
                colorPickerAlignLeft ? 'left-0' : 'right-0',
                colorPickerDropUp ? 'bottom-full mb-2' : 'top-full mt-2'
              ]"
              @click.stop
            >
              <div class="p-6">
                <h3 class="text-sm font-semibold text-gray-900 mb-4">انتخاب رنگ پس‌زمینه</h3>
                <div class="grid grid-cols-4 gap-3">
                  <button
                    v-for="color in availableColors"
                    :key="color.value"
                    @click="changeColor(color.value)"
                    :class="[
                      'w-12 h-12 rounded-xl border-2 transition-all duration-200 hover:scale-105 hover:shadow-md relative group',
                      list.color === color.value ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                    ]"
                    :style="{ backgroundColor: color.bg }"
                    :title="color.name"
                  >
                    <span v-if="list.color === color.value" class="absolute inset-0 flex items-center justify-center">
                      <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                      </svg>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    
      
      <!-- Tasks Container -->
      <div class="px-4 sm:px-5 lg:px-6 py-3 sm:py-4 lg:py-5 max-h-80 sm:max-h-96 lg:max-h-[28rem] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        <div 
          ref="taskContainer"
          class="space-y-2 sm:space-y-3 lg:space-y-4 min-h-[60px] transition-all duration-200"
        >
          <CardItem 
            v-for="task in tasks" 
            :key="task.id" 
            :card="task" 
            @userClick="handleTaskUserClick"
            class="draggable-task"
          />
        </div>
      </div>

      <!-- Add Task Section -->
      <div class="px-4 sm:px-5 lg:px-6 py-3 sm:py-4 lg:py-5 border-t border-gray-100">
        <div v-if="adding" class="space-y-3 sm:space-y-4">
          <input
            v-model="newTitle"
            @keyup.enter="addTask"
            @keyup.escape="cancel"
            ref="newTaskInput"
            class="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base placeholder-gray-500"
            placeholder="عنوان تسک را وارد کنید..."
            autofocus
          />
          <div class="flex gap-3">
            <button
              @click="addTask"
              :disabled="!newTitle.trim()"
              class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-sm sm:text-base font-medium transition-colors"
            >
              افزودن
            </button>
            <button
              @click="cancel"
              class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-sm sm:text-base font-medium transition-colors"
            >
              انصراف
            </button>
          </div>
        </div>
        <button
          v-else
          @click="adding = true"
          class="w-full bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-gray-800 py-3 sm:py-4 rounded-lg text-sm sm:text-base font-medium transition-all duration-200 border-2 border-dashed border-gray-200 hover:border-gray-300 flex items-center justify-center gap-2 sm:gap-3 group"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span>افزودن تسک جدید</span>
        </button>
      </div>
    </div>

    <!-- Edit List Modal -->
    <div 
      v-if="showEditModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[10000]"
      @click="closeEditModal"
    >
      <div 
        class="bg-white rounded-2xl shadow-2xl w-96 max-w-[90vw] max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-gray-900">ویرایش لیست</h3>
            <button 
              @click="closeEditModal"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveListChanges" class="space-y-6">
            <!-- List Title -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">نام لیست</label>
              <input
                v-model="modalEditTitle"
                ref="modalTitleInput"
                type="text"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="نام لیست را وارد کنید..."
                required
              />
            </div>

            <!-- List Color -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">رنگ پس‌زمینه</label>
              <div class="grid grid-cols-6 gap-3">
                <button
                  v-for="color in availableColors"
                  :key="color.value"
                  type="button"
                  @click="modalSelectedColor = color.value"
                  :class="[
                    'w-12 h-12 rounded-xl border-2 transition-all duration-200 hover:scale-105 hover:shadow-md relative group',
                    modalSelectedColor === color.value ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                  ]"
                  :style="{ backgroundColor: color.bg }"
                  :title="color.name"
                >
                  <span v-if="modalSelectedColor === color.value" class="absolute inset-0 flex items-center justify-center">
                    <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                  </span>
                </button>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex space-x-3 space-x-reverse pt-4">
              <button
                type="submit"
                :disabled="!modalEditTitle.trim() || isUpdating"
                class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                <span v-if="isUpdating">در حال ذخیره...</span>
                <span v-else>ذخیره تغییرات</span>
              </button>
              <button
                type="button"
                @click="closeEditModal"
                class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-3 rounded-lg font-medium transition-colors"
              >
                انصراف
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Dialog -->
    <DeleteConfirmDialog
      :visible="showDeleteDialog"
      :message="`آیا از حذف لیست «${list.title}» مطمئن هستید؟`"
      @cancel="cancelDeleteList"
      @confirm="confirmDeleteList"
    />
  </div>
</template>

<script setup>
import { onMounted, computed, watch, ref, nextTick, onUnmounted } from 'vue';
import { useTasksStore } from '../stores/tasks';
import { useListsStore } from '../stores/lists';
import CardItem from './CardItem.vue';
import DeleteConfirmDialog from './DeleteConfirmDialog.vue';

const props = defineProps({
  list: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['taskUserClick']);

const tasksStore = useTasksStore();
const listsStore = useListsStore();
const taskContainer = ref();
const showMenu = ref(false);
const showColorPicker = ref(false);
const editing = ref(false);
const editTitle = ref('');
const editInput = ref();
const showDeleteDialog = ref(false);

// Refs and placement state for dropdowns
const menuWrapper = ref();
const menuButton = ref();
const menuEl = ref();
const colorPickerEl = ref();
const menuAlignLeft = ref(false);
const menuDropUp = ref(false);
const colorPickerAlignLeft = ref(false);
const colorPickerDropUp = ref(false);

// Modal editing state
const showEditModal = ref(false);
const modalEditTitle = ref('');
const modalSelectedColor = ref('');
const modalTitleInput = ref();
const isUpdating = ref(false);

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

// Computed property for list header accent color
const listAccentColor = computed(() => {
  const colorMap = {
    blue: 'border-l-blue-400',
    green: 'border-l-green-400', 
    yellow: 'border-l-yellow-400',
    red: 'border-l-red-400',
    purple: 'border-l-purple-400',
    pink: 'border-l-pink-400',
    indigo: 'border-l-indigo-400',
    gray: 'border-l-gray-400',
    orange: 'border-l-orange-400',
    teal: 'border-l-teal-400',
    cyan: 'border-l-cyan-400',
    lime: 'border-l-lime-400'
  };
  
  return colorMap[props.list.color] || 'border-l-gray-400';
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
          
          // Refresh the cache first to get accurate positions
          await fetch();
          await tasksStore.moveTask(parseInt(taskId), props.list.id, newIndex + 1);
          await fetch(); // Refresh again after move
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
          await fetch(); // Refresh after move
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
const newTaskInput = ref();

async function addTask() {
  if (!newTitle.value.trim()) return;
  
  try {
    await tasksStore.createTask(props.list.id, newTitle.value);
    newTitle.value = '';
    adding.value = false;
    await fetch(); // Refresh tasks to show the new task
  } catch (error) {
    console.error('Failed to create task:', error);
  }
}

function handleTaskUserClick(data) {
  emit('taskUserClick', data);
}

// Focus input when adding starts
watch(adding, async (newVal) => {
  if (newVal) {
    await nextTick();
    newTaskInput.value?.focus();
  }
});

// Menu functionality
function toggleMenu() {
  showColorPicker.value = false;
  showMenu.value = !showMenu.value;
  if (showMenu.value) {
    nextTick(() => {
      positionMenu();
    });
  }
}

function closeMenu() {
  showMenu.value = false;
  showColorPicker.value = false;
}

// Calculate dropdown placement to keep it within viewport
function positionMenu() {
  try {
    const btn = menuButton.value;
    const el = menuEl.value;
    if (!btn || !el) return;
    // Defaults
    menuAlignLeft.value = false;
    menuDropUp.value = false;
    const btnRect = btn.getBoundingClientRect();
    const menuRect = el.getBoundingClientRect();
    const vw = window.innerWidth || document.documentElement.clientWidth;
    const vh = window.innerHeight || document.documentElement.clientHeight;
    // Horizontal: if not enough space on the left, open to the right
    const overflowLeft = (btnRect.left - menuRect.width) < 8;
    const hasRoomRight = (btnRect.right + menuRect.width) <= (vw - 8);
    menuAlignLeft.value = overflowLeft && hasRoomRight;
    // Vertical: if not enough space below, open upwards
    const overflowBottom = (btnRect.bottom + menuRect.height + 12) > vh;
    const hasRoomAbove = btnRect.top >= (menuRect.height + 12);
    menuDropUp.value = overflowBottom && hasRoomAbove;
  } catch (_) {}
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
  if (showColorPicker.value) {
    nextTick(() => {
      positionColorPicker();
    });
  }
}

function positionColorPicker() {
  try {
    const btn = menuButton.value;
    const el = colorPickerEl.value;
    if (!btn || !el) return;
    colorPickerAlignLeft.value = false;
    colorPickerDropUp.value = false;
    const btnRect = btn.getBoundingClientRect();
    const pickerRect = el.getBoundingClientRect();
    const vw = window.innerWidth || document.documentElement.clientWidth;
    const vh = window.innerHeight || document.documentElement.clientHeight;
    const overflowLeft = (btnRect.left - pickerRect.width) < 8;
    const hasRoomRight = (btnRect.right + pickerRect.width) <= (vw - 8);
    colorPickerAlignLeft.value = overflowLeft && hasRoomRight;
    const overflowBottom = (btnRect.bottom + pickerRect.height + 12) > vh;
    const hasRoomAbove = btnRect.top >= (pickerRect.height + 12);
    colorPickerDropUp.value = overflowBottom && hasRoomAbove;
  } catch (_) {}
}

function handleWindowResize() {
  if (showMenu.value) nextTick(() => positionMenu());
  if (showColorPicker.value) nextTick(() => positionColorPicker());
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
  openEditModal();
}

// Modal functions
function openEditModal() {
  showEditModal.value = true;
  modalEditTitle.value = props.list.title;
  modalSelectedColor.value = props.list.color || 'blue';
  nextTick(() => {
    if (modalTitleInput.value) {
      modalTitleInput.value.focus();
      modalTitleInput.value.select();
    }
  });
}

function closeEditModal() {
  showEditModal.value = false;
  modalEditTitle.value = '';
  modalSelectedColor.value = '';
  isUpdating.value = false;
}

async function saveListChanges() {
  if (!modalEditTitle.value.trim()) {
    return;
  }
  
  isUpdating.value = true;
  
  try {
    const updates = {};
    
    // Check if title changed
    if (modalEditTitle.value.trim() !== props.list.title) {
      updates.title = modalEditTitle.value.trim();
    }
    
    // Check if color changed
    if (modalSelectedColor.value !== (props.list.color || 'blue')) {
      updates.color = modalSelectedColor.value;
    }
    
    // Only update if there are changes
    if (Object.keys(updates).length > 0) {
      await listsStore.updateList(props.list.id, updates);
    }
    
    closeEditModal();
  } catch (error) {
    console.error('Failed to update list:', error);
    isUpdating.value = false;
  }
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
    cancel();
  }
}

function cancelEdit() {
  editing.value = false;
  editTitle.value = '';
}

function cancel() {
  adding.value = false;
  newTitle.value = '';
}

function deleteList() {
  closeMenu();
  showDeleteDialog.value = true;
}

async function confirmDeleteList() {
  try {
    await listsStore.deleteList(props.list.id);
  } catch (error) {
    console.error('Failed to delete list:', error);
  } finally {
    showDeleteDialog.value = false;
  }
}

function cancelDeleteList() {
  showDeleteDialog.value = false;
}

// Close menu when clicking outside (scoped to this component only)
function handleClickOutside(event) {
  if (!(showMenu.value || showColorPicker.value)) return;
  const wrapper = menuWrapper.value;
  if (!wrapper) {
    closeMenu();
    return;
  }
  if (!wrapper.contains(event.target)) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('resize', handleWindowResize);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('resize', handleWindowResize);
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
