<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-2 sm:p-4"
    @click.self="close"
  >
    <div
      class="bg-white relative rounded-2xl w-full max-w-4xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden shadow-2xl"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 sm:px-8 py-4 sm:py-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <div class="flex items-center space-x-4 space-x-reverse">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-900">جزئیات تسک</h2>
            <p class="text-sm text-gray-600">ویرایش و مدیریت اطلاعات تسک</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3 space-x-reverse">
          <!-- Complete Toggle -->
          <button
            @click.stop="toggle"
            :class="[
              'flex items-center space-x-2 space-x-reverse px-4 py-2 rounded-lg font-medium transition-all duration-200',
              task.is_completed 
                ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            <div :class="[
              'w-5 h-5 border-2 rounded flex items-center justify-center transition-all duration-200',
              task.is_completed ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-green-400'
            ]">
              <svg v-if="task.is_completed" class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span>{{ task.is_completed ? 'تکمیل شده' : 'تکمیل کردن' }}</span>
          </button>
          
          <!-- Close Button -->
          <button
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500 hover:text-gray-700"
            @click="close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex flex-col lg:flex-row max-h-[calc(95vh-120px)] sm:max-h-[calc(90vh-120px)] overflow-hidden">
        <!-- Left column -->
        <div class="flex-1 p-4 sm:p-8 overflow-y-auto">
          <!-- Title Section -->
          <div class="mb-8">
            <label class="block text-sm font-semibold text-gray-700 mb-3">عنوان تسک</label>
            <input 
              v-model="form.title" 
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-medium transition-all duration-200" 
              placeholder="عنوان تسک را وارد کنید..."
            />
          </div>

          <!-- Assignees Section -->
          <div class="mb-8">
            <label class="block text-sm font-semibold text-gray-700 mb-3">اعضای مسئول</label>
            <div class="bg-gray-50 rounded-xl p-4">
              <AssigneesSelector :task="task" @updated="reloadTask" @userClick="showMemberProfile" />
            </div>
          </div>

          <!-- Description Section -->
          <div class="mb-8">
            <label class="block text-sm font-semibold text-gray-700 mb-3">توضیحات</label>
            <textarea
              v-model="form.description"
              rows="5"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
              placeholder="توضیحات تسک را وارد کنید..."
            ></textarea>
          </div>

          <!-- Priority Section -->
          <div class="mb-8">
            <label class="block text-sm font-semibold text-gray-700 mb-3">اولویت</label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <button
                v-for="priority in priorityOptions"
                :key="priority.value"
                @click="form.priority = priority.value"
                :class="[
                  'flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md',
                  form.priority === priority.value 
                    ? `border-${priority.color}-500 bg-${priority.color}-50 text-${priority.color}-700` 
                    : 'border-gray-200 hover:border-gray-300 text-gray-600'
                ]"
              >
                <div :class="[
                  'w-8 h-8 rounded-lg flex items-center justify-center mb-2',
                  form.priority === priority.value ? `bg-${priority.color}-500` : 'bg-gray-300'
                ]">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path :d="priority.icon"/>
                  </svg>
                </div>
                <span class="text-sm font-medium">{{ priority.label }}</span>
              </button>
            </div>
          </div>

          <!-- Due Date Section -->
          <div class="mb-8">
            <label class="block text-sm font-semibold text-gray-700 mb-3">تاریخ سررسید</label>
            
            <!-- Due Date Display -->
            <div 
              @click="openDatePicker"
              :class="[
                'flex items-center justify-between px-6 py-4 rounded-xl border-2 cursor-pointer transition-all duration-200 hover:shadow-md group',
                task.due_date 
                  ? (isOverdue ? 'bg-red-50 border-red-200 hover:border-red-300' : 'bg-blue-50 border-blue-200 hover:border-blue-300')
                  : 'bg-gray-50 border-gray-200 hover:border-blue-300'
              ]"
            >
              <div class="flex items-center space-x-4 space-x-reverse">
                <div :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center',
                  task.due_date 
                    ? (isOverdue ? 'bg-red-100' : 'bg-blue-100')
                    : 'bg-gray-100 group-hover:bg-blue-100'
                ]">
                  <svg :class="[
                    'w-6 h-6',
                    task.due_date 
                      ? (isOverdue ? 'text-red-600' : 'text-blue-600')
                      : 'text-gray-500 group-hover:text-blue-600'
                  ]" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <div v-if="task.due_date" :class="isOverdue ? 'text-red-700 font-semibold text-lg' : 'text-blue-700 font-semibold text-lg'">
                    {{ formatDueDateDisplay(task.due_date) }}
                  </div>
                  <div v-else class="text-gray-600 font-medium">
                    انتخاب تاریخ سررسید
                  </div>
                  <div v-if="isOverdue" class="flex items-center text-red-500 text-sm mt-1">
                    <svg class="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                    گذشته از زمان مقرر
                  </div>
                  <div v-else-if="task.due_date" class="text-gray-500 text-sm mt-1">
                    کلیک کنید تا تغییر دهید
                  </div>
                  <div v-else class="text-gray-400 text-sm mt-1">
                    کلیک کنید تا تاریخ انتخاب کنید
                  </div>
                </div>
              </div>
              <div class="flex items-center">
                <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </div>
            </div>
          </div>
          
          <!-- Date Picker Modal -->
          <div v-if="showDatePicker" class="fixed inset-0 z-60 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="closeDatePicker">
            <div class="bg-white rounded-2xl p-8 w-96 shadow-2xl">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-xl font-bold text-gray-900">انتخاب تاریخ سررسید</h3>
                <button @click="closeDatePicker" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              
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

        </div>

        <!-- Right column: Activity and Operations -->
        <div class="flex">
          <!-- Activity -->
          <div class="w-1/3 border-l pl-4">
            <h3 class="font-semibold mb-2">Activity</h3>
            <p class="text-sm text-gray-500">(به‌زودی)</p>
          </div>
          <!-- Right Sidebar -->
          <div class="w-full lg:w-80 bg-gray-50 border-t lg:border-t-0 lg:border-l border-gray-200 p-4 sm:p-6 overflow-y-auto max-h-60 lg:max-h-none">
            <h3 class="font-bold text-gray-900 mb-6 flex items-center">
              <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              عملیات
            </h3>
            
            <div class="space-y-4">
              <!-- Save Button -->
              <button
                @click="save"
                class="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2 space-x-reverse"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <span>ذخیره تغییرات</span>
              </button>
              
              <!-- Delete Button -->
              <button
                @click="deleteTask"
                class="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2 space-x-reverse"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                <span>حذف تسک</span>
              </button>
              
              <!-- Task Info -->
              <div class="mt-8 p-4 bg-white rounded-xl border border-gray-200">
                <h4 class="font-semibold text-gray-900 mb-3">اطلاعات تسک</h4>
                <div class="space-y-3 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">وضعیت:</span>
                    <span :class="task.is_completed ? 'text-green-600 font-medium' : 'text-yellow-600 font-medium'">
                      {{ task.is_completed ? 'تکمیل شده' : 'در حال انجام' }}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">اولویت:</span>
                    <span :class="{
                      'text-gray-600': form.priority === 'low',
                      'text-yellow-600': form.priority === 'medium', 
                      'text-orange-600': form.priority === 'high',
                      'text-red-600': form.priority === 'urgent'
                    } + ' font-medium'">
                      {{ priorityOptions.find(p => p.value === form.priority)?.label || 'نامشخص' }}
                    </span>
                  </div>
                  <div v-if="task.due_date" class="flex justify-between">
                    <span class="text-gray-600">سررسید:</span>
                    <span :class="isOverdue ? 'text-red-600 font-medium' : 'text-blue-600 font-medium'">
                      {{ formatDueDateDisplay(task.due_date) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Member Profile Modal -->
    <MemberProfileModal 
      v-if="showMemberProfileModal && selectedMember"
      :member="selectedMember"
      @close="closeMemberProfile"
    />
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref, nextTick } from 'vue';
import AssigneesSelector from './AssigneesSelector.vue';
import MemberProfileModal from './MemberProfileModal.vue';
import { storeToRefs } from 'pinia';
import { useTasksStore } from '../stores/tasks';

const tasksStore = useTasksStore();
const task = computed(() => tasksStore.currentTask);
const form = reactive({
  title: '',
  description: '',
  priority: 'medium'
});
const showDatePicker = ref(false);
const showMemberProfileModal = ref(false);
const selectedMember = ref(null);

// Priority options with modern styling
const priorityOptions = [
  {
    value: 'low',
    label: 'کم',
    color: 'gray',
    icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    value: 'medium', 
    label: 'متوسط',
    color: 'yellow',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z'
  },
  {
    value: 'high',
    label: 'بالا', 
    color: 'orange',
    icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    value: 'urgent',
    label: 'فوری',
    color: 'red', 
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z'
  }
];

// Date picker state
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
  close();
}

function reloadTask() {
  tasksStore.fetchTask(task.value.id);
}

function showMemberProfile(user) {
  console.log('showMemberProfile called with:', user);
  // Transform user data to match MemberProfileModal expected format
  const memberData = {
    id: user.id,
    user_id: user.id,
    username: user.username,
    full_name: user.full_name,
    email: user.email || '',
    role: 'member', // Default role since AssigneesSelector doesn't have role info
    status: 'accepted'
  };
  console.log('Transformed member data:', memberData);
  selectedMember.value = memberData;
  showMemberProfileModal.value = true;
}

function closeMemberProfile() {
  showMemberProfileModal.value = false;
  selectedMember.value = null;
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
