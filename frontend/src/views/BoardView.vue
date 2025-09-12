<template>
  <div 
    class="min-h-screen transition-all duration-500"
    :style="{ 
      background: board?.color 
        ? `linear-gradient(135deg, ${adjustColor(board.color, 40)}, ${adjustColor(board.color, -20)})` 
        : 'linear-gradient(135deg, #f8fafc, #e0f2fe)' 
    }"
  >
    <!-- Board Header -->
    <div class="bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-16 z-40">
      <div class="w-full max-w-none px-3 sm:px-4 lg:px-6 py-3 sm:py-4 lg:py-5" v-if="board">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 lg:gap-4">
          <div class="flex items-center gap-3 sm:gap-4 lg:gap-5 min-w-0 flex-1">
            <div 
              class="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 rounded-xl flex items-center justify-center shadow-sm flex-shrink-0"
              :style="{ background: board.color ? `linear-gradient(135deg, ${board.color}, ${adjustColor(board.color, -20)})` : 'linear-gradient(135deg, #3b82f6, #1d4ed8)' }"
            >
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <h1 class="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-bold text-gray-900 truncate">{{ board.title }}</h1>
              <div class="flex items-center gap-2 sm:gap-3 mt-1 sm:mt-2">
                <div class="flex items-center gap-1">
                  <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                  </svg>
                  <p class="text-sm sm:text-base text-gray-600">{{ lists.length }} لیست</p>
                </div>
                <span class="text-gray-400">•</span>
                <div class="flex items-center gap-1">
                  <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  <p class="text-sm sm:text-base text-gray-600">{{ totalTasks }} تسک</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-3 sm:gap-4 lg:gap-5 w-full lg:w-auto justify-between lg:justify-end flex-shrink-0">
            <!-- Board Members -->
            <div class="flex -space-x-1 sm:-space-x-2 space-x-reverse">
              <UserAvatar
                v-for="(member, index) in boardMembers.slice(0, 3)" 
                :key="member.id"
                :user="member"
                size="sm"
                @click="openMemberProfile(member)"
              />
              <div 
                v-if="boardMembers.length > 3"
                @click="showAllMembers = true"
                class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-full border-2 border-white bg-gray-400 flex items-center justify-center text-white text-xs sm:text-sm lg:text-base font-medium cursor-pointer hover:scale-110 transition-transform duration-200 flex-shrink-0"
                :title="`${boardMembers.length - 3} عضو دیگر`"
              >
                +{{ boardMembers.length - 3 }}
              </div>
            </div>
            
            <!-- Add List Button -->
            <button 
              @click="showAddListDialog = true"
              class="flex items-center gap-2 sm:gap-3 bg-white hover:bg-gray-50 text-gray-700 px-3 sm:px-4 lg:px-5 py-2 sm:py-3 rounded-lg border border-gray-200 font-medium transition-all duration-200 shadow-sm hover:shadow-md text-sm sm:text-base flex-shrink-0"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span class="hidden sm:inline">افزودن لیست</span>
              <span class="sm:hidden">افزودن</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Board Content -->
    <div class="w-full px-2 sm:px-4 lg:px-6 py-3 sm:py-4 lg:py-6" v-if="board">
      <div 
        ref="listsContainer"
        class="relative flex items-start gap-3 sm:gap-4 lg:gap-6 overflow-x-auto pb-4 sm:pb-6 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100"
        :class="{ 'dragging-scroll': isDragScrolling }"
        style="min-height: calc(100vh - 160px); direction: ltr;"
        @pointerdown.capture="handleContainerPointerDown"
        @pointermove="handleContainerPointerMove"
        @pointerup="handleContainerPointerUp"
        @pointerleave="handleContainerPointerUp"
        @pointercancel="handleContainerPointerUp"
      >
        <div
          v-for="list in lists" 
          :key="list.id"
          :data-list-id="list.id"
          class="flex-shrink-0 draggable-list min-w-0"
          style="direction: rtl;"
        >
          <ListColumn 
            :list="list" 
            @taskUserClick="handleTaskUserClick"
          />
        </div>
        
        <!-- Add List Column -->
        <div class="flex-shrink-0 w-72 sm:w-80 lg:w-96" style="direction: rtl;" data-add-list-column>
          <div 
            v-if="!showAddListDialog"
            @click="showAddListDialog = true"
            class="bg-white/60 hover:bg-white/80 border-2 border-dashed border-gray-300 hover:border-blue-400 rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 cursor-pointer transition-all duration-200 min-h-[120px] sm:min-h-[140px] lg:min-h-[160px] flex items-center justify-center group"
          >
            <div class="text-center">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-gray-400 group-hover:text-blue-500 mx-auto mb-2 sm:mb-3 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <p class="text-sm sm:text-base lg:text-lg text-gray-600 group-hover:text-blue-600 font-medium transition-colors">افزودن لیست جدید</p>
            </div>
          </div>
          
          <!-- Add List Form -->
          <div v-else class="bg-white rounded-xl lg:rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-5">
            <input 
              v-model="newListTitle"
              @keyup.enter="createList"
              @keyup.escape="cancelAddList"
              ref="listTitleInput"
              type="text" 
              placeholder="عنوان لیست را وارد کنید..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
            />
            <div class="flex gap-3 mt-4">
              <button 
                @click="createList"
                :disabled="!newListTitle.trim()"
                class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-3 rounded-lg text-sm sm:text-base font-medium transition-colors"
              >
                افزودن
              </button>
              <button 
                @click="cancelAddList"
                class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-3 rounded-lg text-sm sm:text-base font-medium transition-colors"
              >
                انصراف
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
    
    <!-- Loading State -->
    <div v-else class="flex items-center justify-center h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p class="text-gray-600">در حال بارگیری برد...</p>
      </div>
    </div>

    <TaskModal v-if="tasksStore.modalOpen" />
    <MemberProfileModal 
      v-if="memberProfileModal.isOpen && memberProfileModal.member"
      :member="memberProfileModal.member"
      :canManageMembers="canManageMembers"
      @close="closeMemberProfile"
      @sendMessage="handleSendMessage"
      @manageMember="handleManageMember"
      @removeMember="handleRemoveMember"
    />
    <TaskMemberProfileModal 
      v-if="taskMemberProfileModal.isOpen && taskMemberProfileModal.member"
      :member="taskMemberProfileModal.member"
      :task="taskMemberProfileModal.task"
      @close="closeTaskMemberProfile"
      @viewTask="handleViewTask"
    />
    
    <ConfirmationModal
      :isOpen="confirmationModal.isOpen"
      :memberInfo="confirmationModal.member"
      title="حذف عضو از برد"
      :message="`آیا مطمئن هستید که می‌خواهید ${confirmationModal.member?.name || confirmationModal.member?.username} را از برد حذف کنید؟`"
      confirmText="حذف عضو"
      @confirm="confirmRemoveMember"
      @cancel="cancelRemoveMember"
    />
    
    <!-- All Members Modal -->
    <div 
      v-if="showAllMembers" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="showAllMembers = false"
    >
      <div 
        class="bg-white rounded-xl sm:rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] sm:max-h-96 overflow-hidden"
        @click.stop
      >
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-4 sm:px-6 py-3 sm:py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg sm:text-xl font-bold text-white">اعضای برد</h3>
            <button 
              @click="showAllMembers = false"
              class="text-white hover:text-gray-200 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="p-4 sm:p-6 overflow-y-auto max-h-[70vh] sm:max-h-80">
          <div class="space-y-2 sm:space-y-3">
            <div 
              v-for="member in boardMembers" 
              :key="member.id"
              @click="openMemberProfile(member)"
              class="flex items-center space-x-2 sm:space-x-3 space-x-reverse p-2 sm:p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <UserAvatar
                :user="member"
                size="md"
                @click="openMemberProfile(member)"
              />
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 text-sm sm:text-base truncate">{{ member.name || member.username }}</h4>
                <p class="text-xs sm:text-sm text-gray-600 truncate">@{{ member.username }}</p>
              </div>
              <span 
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getRoleClass(member.role)"
              >
                {{ getRoleText(member.role) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, computed, ref, nextTick, watch, reactive } from 'vue';
import { useTasksStore } from '../stores/tasks';
import TaskModal from '../components/TaskModal.vue';
import MemberProfileModal from '../components/MemberProfileModal.vue';
import TaskMemberProfileModal from '../components/TaskMemberProfileModal.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';
import UserAvatar from '../components/UserAvatar.vue';
import { useRoute } from 'vue-router';
import { useBoardsStore } from '../stores/boards';
import { useListsStore } from '../stores/lists';
import ListColumn from '../components/ListColumn.vue';

const route = useRoute();
const boardsStore = useBoardsStore();
const listsStore = useListsStore();
const tasksStore = useTasksStore();

// Add list functionality
const showAddListDialog = ref(false);
const newListTitle = ref('');
const listTitleInput = ref(null);
const listsContainer = ref(null);

// Drag-to-scroll (desktop) state
const isDragScrolling = ref(false);
let dragStartX = 0;
let dragStartY = 0;
let dragStartScrollLeft = 0;
let listsSortable = null;
let hasMoved = false;
const DRAG_THRESHOLD = 6; // px
let isPointerDown = false;

function handleContainerPointerDown(e) {
  // Only left-click and mouse pointer (desktop behavior)
  if (e.button !== 0 || (e.pointerType && e.pointerType !== 'mouse')) return;

  const target = e.target;
  // Ignore if starting on a list column (to not conflict with SortableJS)
  if (target.closest('.draggable-list')) return;
  // Ignore interactive elements to preserve native interactions
  if (target.closest('input, textarea, button, select, a, [contenteditable="true"]')) return;

  // Prepare for potential drag-scroll (do NOT start yet)
  isDragScrolling.value = false;
  hasMoved = false;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragStartScrollLeft = listsContainer.value?.scrollLeft || 0;
  isPointerDown = true;
}

function handleContainerPointerMove(e) {
  if (!listsContainer.value) return;

  // If mouse button is not pressed, ensure we stop drag-scroll
  if (e.pointerType === 'mouse' && e.buttons === 0) {
    if (isDragScrolling.value) {
      handleContainerPointerUp(e);
    }
    return;
  }

  if (!isPointerDown) return;

  // If not yet started, check threshold
  if (!isDragScrolling.value) {
    const dx = Math.abs(e.clientX - dragStartX);
    const dy = Math.abs(e.clientY - dragStartY);
    if (dx > DRAG_THRESHOLD && dx > dy) {
      // Start drag-scroll now
      isDragScrolling.value = true;
      hasMoved = true;
      try {
        if (listsSortable && typeof listsSortable.option === 'function') {
          listsSortable.option('disabled', true);
        }
      } catch (_) {}
      // Visual feedback and prevent text selection
      listsContainer.value.style.cursor = 'grabbing';
      listsContainer.value.style.userSelect = 'none';
      try {
        e.currentTarget.setPointerCapture && e.currentTarget.setPointerCapture(e.pointerId);
      } catch (_) {}
    } else {
      return; // do nothing until threshold exceeded
    }
  }

  // Perform scrolling
  const dxMove = e.clientX - dragStartX;
  listsContainer.value.scrollLeft = dragStartScrollLeft - dxMove;
  e.preventDefault();
  e.stopPropagation();
}

function handleContainerPointerUp(e) {
  // Release pointer capture if any
  try {
    if (e && e.currentTarget && e.pointerId && e.currentTarget.hasPointerCapture && e.currentTarget.hasPointerCapture(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  } catch (_) {}

  if (isDragScrolling.value) {
    isDragScrolling.value = false;
    if (listsContainer.value) {
      listsContainer.value.style.cursor = '';
      listsContainer.value.style.userSelect = '';
    }
    // Re-enable Sortable
    try {
      if (listsSortable && typeof listsSortable.option === 'function') {
        listsSortable.option('disabled', false);
      }
    } catch (_) {}
    // Prevent click after drag
    e.preventDefault();
    e.stopPropagation();
  }
  isPointerDown = false;
}

function handleGlobalPointerUp() {
  if (!isPointerDown && !isDragScrolling.value) return;
  isPointerDown = false;
  if (isDragScrolling.value) {
    isDragScrolling.value = false;
    if (listsContainer.value) {
      listsContainer.value.style.cursor = '';
      listsContainer.value.style.userSelect = '';
    }
    try {
      if (listsSortable && typeof listsSortable.option === 'function') {
        listsSortable.option('disabled', false);
      }
    } catch (_) {}
  }
}

// Member profile modal
const memberProfileModal = reactive({
  isOpen: false,
  member: null
});
const showAllMembers = ref(false);

// Task member profile modal
const taskMemberProfileModal = reactive({
  isOpen: false,
  member: null,
  task: null
});

// Confirmation modal
const confirmationModal = ref({
  isOpen: false,
  member: null
});

onMounted(async () => {
  const boardId = route.params.id;
  await boardsStore.fetchBoard(boardId);
  await listsStore.fetchLists(boardId);
  await nextTick();
  initializeListSortable();
  // Global listeners to guarantee end of drag-scroll
  window.addEventListener('pointerup', handleGlobalPointerUp, true);
  window.addEventListener('pointercancel', handleGlobalPointerUp, true);
  window.addEventListener('blur', handleGlobalPointerUp, true);
});

onBeforeUnmount(() => {
  // Ensure cleanup of styles if user navigates mid-drag
  handleContainerPointerUp();
  try {
    if (listsSortable && typeof listsSortable.destroy === 'function') {
      listsSortable.destroy();
      listsSortable = null;
    }
  } catch (_) {}
  window.removeEventListener('pointerup', handleGlobalPointerUp, true);
  window.removeEventListener('pointercancel', handleGlobalPointerUp, true);
  window.removeEventListener('blur', handleGlobalPointerUp, true);
});

const board = computed(() => boardsStore.currentBoard);
const lists = computed(() => listsStore.lists);

// Computed properties for board stats
const totalTasks = computed(() => {
  return lists.value.reduce((total, list) => total + (list.tasks_count || 0), 0);
});

const boardMembers = computed(() => {
  if (!board.value?.members) return [];
  
  return board.value.members.map(membership => ({
    id: membership.user_id,
    user_id: membership.user_id,
    name: membership.full_name || membership.username,
    username: membership.username,
    full_name: membership.full_name,
    email: membership.email,
    profile: membership.profile,
    role: membership.role,
    status: membership.status
  }));
});

const canManageMembers = computed(() => {
  // Check if current user is owner or admin
  const currentUser = board.value?.owner;
  return board.value && (board.value.owner === currentUser || 
    boardMembers.value.some(member => member.role === 'admin'));
});

// Helper functions
const adjustColor = (color, amount) => {
  if (!color) return '#3b82f6';
  
  // Convert hex to RGB
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Adjust brightness
  const newR = Math.max(0, Math.min(255, r + amount));
  const newG = Math.max(0, Math.min(255, g + amount));
  const newB = Math.max(0, Math.min(255, b + amount));
  
  // Convert back to hex
  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
};

// List management functions
const createList = async () => {
  if (!newListTitle.value.trim()) return;
  
  try {
    await listsStore.createList({
      title: newListTitle.value.trim(),
      board: route.params.id
    });
    newListTitle.value = '';
    showAddListDialog.value = false;
  } catch (error) {
    console.error('Error creating list:', error);
  }
};

const cancelAddList = () => {
  newListTitle.value = '';
  showAddListDialog.value = false;
};

// Watch for showAddListDialog changes to focus input
const watchAddListDialog = async (newVal) => {
  if (newVal) {
    await nextTick();
    listTitleInput.value?.focus();
  }
};

// Watch showAddListDialog
watch(() => showAddListDialog.value, watchAddListDialog);

// Initialize sortable functionality for lists
function initializeListSortable() {
  if (!listsContainer.value) return;
  
  // Destroy previous instance if exists
  try {
    if (listsSortable && typeof listsSortable.destroy === 'function') {
      listsSortable.destroy();
      listsSortable = null;
    }
  } catch (_) {}

  import('sortablejs').then(({ default: Sortable }) => {
    listsSortable = new Sortable(listsContainer.value, {
      animation: 200,
      ghostClass: 'ghost-list',
      chosenClass: 'chosen-list',
      dragClass: 'drag-list',
      draggable: '.draggable-list', // Only list columns are draggable
      handle: '.draggable-list', // Drag by the list container
      onUpdate: async (evt) => {
        try {
          const listId = evt.item.getAttribute('data-list-id');
          const newIndex = evt.newIndex;
          console.log('Moving list', listId, 'to position', newIndex + 1);
          
          // Move the list to new position
          await listsStore.moveList(parseInt(listId), newIndex + 1);
          
          // Refresh lists to ensure correct order
          await listsStore.fetchLists(route.params.id);
        } catch (error) {
          console.error('Failed to move list:', error);
          // Refresh lists on error to restore correct order
          await listsStore.fetchLists(route.params.id);
        }
      }
    });
  });
}

// Watch for list changes to reinitialize sortable
watch(() => lists.value.length, async () => {
  await nextTick();
  initializeListSortable();
});

// Member profile functions
const openMemberProfile = (member) => {
  console.log('openMemberProfile called with:', member);
  if (!member) {
    console.warn('openMemberProfile called with null/undefined member');
    return;
  }
  
  console.log('Setting modal state...');
  memberProfileModal.isOpen = true;
  memberProfileModal.member = member;
  showAllMembers.value = false;
  console.log('Modal state after setting:', memberProfileModal);
  console.log('Modal isOpen:', memberProfileModal.isOpen);
  console.log('Modal member:', memberProfileModal.member);
};

const closeMemberProfile = () => {
  memberProfileModal.isOpen = false;
  memberProfileModal.member = null;
};

const handleSendMessage = (member) => {
  // TODO: Implement messaging functionality
  console.log('Send message to:', member);
};

const handleManageMember = (member) => {
  // TODO: Implement member management functionality
  console.log('Manage member:', member);
};

const handleRemoveMember = (member) => {
  confirmationModal.value = {
    isOpen: true,
    member: member
  };
};

// Task member profile functions
function handleTaskUserClick(data) {
  console.log('Task user clicked:', data);
  console.log('Opening modal with member:', data.user);
  console.log('Modal state before:', taskMemberProfileModal.isOpen);
  taskMemberProfileModal.isOpen = true;
  taskMemberProfileModal.member = data.user;
  taskMemberProfileModal.task = data.task;
  console.log('Modal state after:', taskMemberProfileModal.isOpen);
}

function closeTaskMemberProfile() {
  taskMemberProfileModal.isOpen = false;
  taskMemberProfileModal.member = null;
  taskMemberProfileModal.task = null;
}

function handleViewTask(task) {
  tasksStore.openTask(task.id);
}

function handleSendMessageToTaskMember(member) {
  // TODO: Implement messaging functionality
  console.log('Send message to task member:', member);
}

const confirmRemoveMember = async () => {
  const member = confirmationModal.value.member;
  confirmationModal.value.isOpen = false;
  
  try {
    await boardsStore.removeMember(route.params.id, member.id);
    console.log('Member removed successfully');
  } catch (error) {
    console.error('Failed to remove member:', error);
    alert('خطا در حذف عضو: ' + (error.error || 'خطای نامشخص'));
  }
};

const cancelRemoveMember = () => {
  confirmationModal.value = {
    isOpen: false,
    member: null
  };
};

const getRoleClass = (role) => {
  switch (role) {
    case 'owner':
      return 'bg-purple-100 text-purple-800';
    case 'admin':
      return 'bg-blue-100 text-blue-800';
    case 'member':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getRoleText = (role) => {
  switch (role) {
    case 'owner':
      return 'مالک';
    case 'admin':
      return 'مدیر';
    case 'member':
      return 'عضو';
    default:
      return 'نامشخص';
  }
};
</script>

<style scoped>
/* Drag and drop visual feedback for lists */
.ghost-list {
  opacity: 0.5;
  background: rgba(59, 130, 246, 0.1);
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 16px;
}

.chosen-list {
  cursor: grabbing !important;
  transform: rotate(2deg);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.drag-list {
  opacity: 0.9;
  transform: rotate(2deg);
}

/* Draggable list styling */
.draggable-list {
  cursor: grab;
  transition: all 0.2s ease;
}

.draggable-list:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.draggable-list:active {
  cursor: grabbing;
}

/* Cursor feedback while drag-scrolling on empty area */
.dragging-scroll {
  cursor: grabbing;
}

/* Custom scrollbar styles */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: #d1d5db #f3f4f6;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 4px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.scrollbar-thin::-webkit-scrollbar-corner {
  background: #f3f4f6;
}

/* Responsive improvements */
@media (max-width: 640px) {
  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
}

@media (min-width: 1024px) {
  .scrollbar-thin::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
}
</style>
