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
      <div class="container mx-auto px-6 py-4" v-if="board">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4 space-x-reverse">
            <div 
              class="w-12 h-12 rounded-xl flex items-center justify-center shadow-sm"
              :style="{ background: board.color ? `linear-gradient(135deg, ${board.color}, ${adjustColor(board.color, -20)})` : 'linear-gradient(135deg, #3b82f6, #1d4ed8)' }"
            >
              <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ board.title }}</h1>
              <p class="text-sm text-gray-600">{{ lists.length }} لیست • {{ totalTasks }} تسک</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-3 space-x-reverse">
            <!-- Board Members -->
            <div class="flex -space-x-2 space-x-reverse">
              <div 
                v-for="(member, index) in boardMembers.slice(0, 4)" 
                :key="member.id"
                class="w-8 h-8 rounded-full border-2 border-white bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-medium"
                :title="member.name"
              >
                {{ member.name ? member.name[0].toUpperCase() : 'U' }}
              </div>
              <div 
                v-if="boardMembers.length > 4"
                class="w-8 h-8 rounded-full border-2 border-white bg-gray-400 flex items-center justify-center text-white text-xs font-medium"
              >
                +{{ boardMembers.length - 4 }}
              </div>
            </div>
            
            <!-- Add List Button -->
            <button 
              @click="showAddListDialog = true"
              class="flex items-center space-x-2 space-x-reverse bg-white hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg border border-gray-200 font-medium transition-all duration-200 shadow-sm hover:shadow-md"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>افزودن لیست</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Board Content -->
    <div class="container mx-auto px-4 md:px-6 py-4 md:py-6" v-if="board">
      <div class="flex space-x-4 md:space-x-6 space-x-reverse overflow-x-auto pb-6" style="min-height: calc(100vh - 200px);">
        <ListColumn 
          v-for="list in lists" 
          :key="list.id" 
          :list="list" 
          class="flex-shrink-0"
        />
        
        <!-- Add List Column -->
        <div class="flex-shrink-0 w-80">
          <div 
            v-if="!showAddListDialog"
            @click="showAddListDialog = true"
            class="bg-white/60 hover:bg-white/80 border-2 border-dashed border-gray-300 hover:border-blue-400 rounded-2xl p-6 cursor-pointer transition-all duration-200 h-32 flex items-center justify-center group"
          >
            <div class="text-center">
              <svg class="w-8 h-8 text-gray-400 group-hover:text-blue-500 mx-auto mb-2 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <p class="text-gray-600 group-hover:text-blue-600 font-medium transition-colors">افزودن لیست جدید</p>
            </div>
          </div>
          
          <!-- Add List Form -->
          <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <input 
              v-model="newListTitle"
              @keyup.enter="createList"
              @keyup.escape="cancelAddList"
              ref="listTitleInput"
              type="text" 
              placeholder="عنوان لیست را وارد کنید..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
            <div class="flex space-x-2 space-x-reverse mt-3">
              <button 
                @click="createList"
                :disabled="!newListTitle.trim()"
                class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                افزودن
              </button>
              <button 
                @click="cancelAddList"
                class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
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
  </div>
</template>

<script setup>
import { onMounted, computed, ref, nextTick, watch } from 'vue';
import { useTasksStore } from '../stores/tasks';
import TaskModal from '../components/TaskModal.vue';
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

onMounted(async () => {
  const boardId = route.params.id;
  await boardsStore.fetchBoard(boardId);
  await listsStore.fetchLists(boardId);
});

const board = computed(() => boardsStore.currentBoard);
const lists = computed(() => listsStore.lists);

// Computed properties for board stats
const totalTasks = computed(() => {
  return lists.value.reduce((total, list) => total + (list.tasks_count || 0), 0);
});

const boardMembers = computed(() => {
  // Mock data - replace with actual board members from store
  return [
    { id: 1, name: 'احمد محمدی' },
    { id: 2, name: 'فاطمه احمدی' },
    { id: 3, name: 'علی رضایی' }
  ];
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
</script>
