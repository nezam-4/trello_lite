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

          <!-- Assignees -->
          <div class="mb-4">
            <label class="block text-sm mb-1">اعضا</label>
            <AssigneesSelector :task="task" @updated="reloadTask" />
          </div>

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

          <!-- Due Date Section -->
          <div class="mb-4">
            <label class="block text-sm mb-2">تاریخ سررسید</label>
            
            <!-- Due Date Display -->
            <div 
              @click="openDatePicker"
              :class="[
                'flex items-center justify-between px-4 py-3 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md',
                task.due_date 
                  ? (isOverdue ? 'bg-red-50 border-red-200 hover:border-red-300' : 'bg-blue-50 border-blue-200 hover:border-blue-300')
                  : 'bg-gray-50 border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="flex items-center">
                <svg class="w-5 h-5 ml-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                </svg>
                <div>
                  <div v-if="task.due_date" :class="isOverdue ? 'text-red-700 font-medium' : 'text-blue-700 font-medium'">
                    {{ formatDueDateDisplay(task.due_date) }}
                  </div>
                  <div v-else class="text-gray-600">
                    انتخاب تاریخ سررسید
                  </div>
                  <div v-if="isOverdue" class="text-red-500 text-xs mt-1">
                    ⚠️ گذشته از زمان مقرر
                  </div>
                </div>
              </div>
              <div class="flex items-center">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </div>
            </div>
          </div>
          
          <!-- Date Picker Modal -->
          <div v-if="showDatePicker" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="closeDatePicker">
            <div class="bg-white rounded-lg p-6 w-80 shadow-xl">
              <h3 class="text-lg font-semibold mb-4 text-center">انتخاب تاریخ</h3>
              
              <input 
                ref="datePickerInput"
                v-model="selectedDate"
                type="date" 
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none mb-4"
              />
              
              <div class="flex space-x-3 rtl:space-x-reverse">
                <button 
                  @click="saveDateSelection"
                  class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  تایید
                </button>
                <button 
                  v-if="task.due_date"
                  @click="removeDueDate"
                  class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  حذف
                </button>
                <button 
                  @click="closeDatePicker"
                  class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  لغو
                </button>
              </div>
            </div>
          </div>

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
import { reactive, watch, computed, ref, nextTick } from 'vue';
import AssigneesSelector from './AssigneesSelector.vue';
import { storeToRefs } from 'pinia';
import { useTasksStore } from '../stores/tasks';

const tasksStore = useTasksStore();

const { currentTask: task } = storeToRefs(tasksStore);
const form = reactive({ title: '', description: '', priority: 'medium', due_date: '' });

// Date picker state
const showDatePicker = ref(false);
const selectedDate = ref('');
const datePickerInput = ref(null);

// --- members selection handled by AssigneesSelector component ---

watch(task, (t) => {
  if (t) {
    form.title = t.title;
    form.description = t.description || '';
    form.priority = t.priority;
    form.due_date = t.due_date ? formatDateForInput(t.due_date) : '';
  }
}, { immediate: true });

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

// Format date for display (date only)
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

// Date picker functions
async function openDatePicker() {
  showDatePicker.value = true;
  selectedDate.value = task.value.due_date ? formatDateForInput(task.value.due_date) : '';
  await nextTick();
  if (datePickerInput.value) {
    datePickerInput.value.focus();
  }
}

function closeDatePicker() {
  showDatePicker.value = false;
  selectedDate.value = '';
}

async function saveDateSelection() {
  if (!selectedDate.value) {
    closeDatePicker();
    return;
  }
  
  const updateData = {
    due_date: selectedDate.value // Keep date format as YYYY-MM-DD
  };
  
  await tasksStore.updateTask(task.value.id, updateData);
  closeDatePicker();
}

async function removeDueDate() {
  const updateData = { due_date: null };
  await tasksStore.updateTask(task.value.id, updateData);
  closeDatePicker();
}

async function save() {
  const updateData = { ...form };
  // Don't include due_date in form save since it's handled separately
  delete updateData.due_date;
  await tasksStore.updateTask(task.value.id, updateData);
}

function reloadTask() {
  tasksStore.fetchTask(task.value.id);
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
