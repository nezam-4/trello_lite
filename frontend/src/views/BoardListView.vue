<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-100 to-blue-100 p-2 sm:p-4 md:p-6" dir="rtl">
    <div class="max-w-7xl mx-auto">
      <!-- Header Section -->
      <div class="px-2 sm:px-4 md:px-6 py-4 sm:py-6 md:py-8">
        <div class="mb-4 sm:mb-6 md:mb-8">
          <h1 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-2">بردهای من - MODAL UPDATED</h1>
          <p class="text-sm sm:text-base text-gray-600">مدیریت و سازماندهی پروژه‌های خود</p>
        </div>
        <button 
          @click="showCreateDialog=true" 
          class="flex items-center space-x-2 space-x-reverse bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 sm:px-6 py-2.5 sm:py-3 rounded-lg sm:rounded-xl hover:from-blue-600 hover:to-purple-700 font-medium shadow-lg hover:shadow-xl transition-all duration-200 text-sm sm:text-base"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span class="hidden sm:inline">ایجاد برد جدید</span>
          <span class="sm:hidden">ایجاد برد</span>
        </button>
      </div>

      <div class="flex flex-col xl:flex-row gap-4 sm:gap-6 lg:gap-8">
        <!-- Boards Section -->
        <div class="flex-1">
          <p v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg mb-4 sm:mb-6 text-sm sm:text-base">{{ errorMessage }}</p>
          <!-- Boards Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-3 sm:gap-4 md:gap-6">
            <div
              v-for="board in boardsStore.boards"
              :key="board.id"
              :data-board-id="board.id"
              class="group relative bg-white rounded-xl sm:rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-visible cursor-pointer"
              @click="goToBoard(board.id)"
            >
              <!-- Board Color Header -->
              <div 
                class="h-16 sm:h-20 md:h-24 relative"
                :style="{ background: board.color ? `linear-gradient(135deg, ${board.color}, ${adjustColor(board.color, -20)})` : 'linear-gradient(135deg, #3b82f6, #1d4ed8)' }"
              >
                <div class="absolute inset-0 bg-black/10"></div>
                <button 
                  @click.stop="toggleMenu(board.id)" 
                  class="absolute top-2 sm:top-3 left-2 sm:left-3 w-6 h-6 sm:w-8 sm:h-8 bg-white/20 hover:bg-white/30 rounded-md sm:rounded-lg flex items-center justify-center text-white transition-all duration-200 board-menu-button opacity-0 group-hover:opacity-100"
                >
                  <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                  </svg>
                </button>
              </div>

              <!-- Board Content -->
              <div class="p-3 sm:p-4 md:p-6">
                <h3 class="font-bold text-sm sm:text-base md:text-lg text-gray-900 mb-2 line-clamp-2">{{ board.title }}</h3>
                
                <div class="flex items-center justify-between mb-2 sm:mb-4">
                  <div class="flex items-center space-x-1 sm:space-x-2 space-x-reverse text-xs sm:text-sm text-gray-600">
                    <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
                    </svg>
                    <span>{{ board.members_count }} عضو</span>
                  </div>
                  
                  <span 
                    v-if="board.current_user_role" 
                    class="inline-flex items-center px-1.5 sm:px-2.5 py-0.5 sm:py-1 rounded-full text-xs font-medium"
                    :class="{
                      'bg-emerald-100 text-emerald-700': board.current_user_role==='owner',
                      'bg-blue-100 text-blue-700': board.current_user_role==='admin',
                      'bg-gray-100 text-gray-700': board.current_user_role==='member'
                    }"
                  >
                    {{ getRoleText(board.current_user_role) }}
                  </span>
                </div>
              </div>

            </div>
          </div>
        </div>
        <!-- Invitations Sidebar -->
        <div class="w-full xl:w-80 bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-200/50 p-3 sm:p-4 md:p-6">
          <div class="flex items-center space-x-2 space-x-reverse mb-4 sm:mb-6">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <h2 class="text-base sm:text-lg font-bold text-gray-900">دعوت‌ها</h2>
          </div>
          
          <div v-if="invitationsStore.invitations.length === 0" class="text-center py-6 sm:py-8">
            <svg class="w-8 h-8 sm:w-12 sm:h-12 text-gray-300 mx-auto mb-3 sm:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2 2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <p class="text-gray-500 text-xs sm:text-sm">هیچ دعوتی وجود ندارد</p>
          </div>
          
          <div class="space-y-3 sm:space-y-4 max-h-80 sm:max-h-96 overflow-y-auto">
            <div 
              v-for="inv in invitationsStore.invitations" 
              :key="inv.id" 
              class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100 rounded-lg sm:rounded-xl p-3 sm:p-4 transition-all duration-200 hover:shadow-md"
            >
              <div class="flex items-start justify-between mb-2 sm:mb-3">
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-sm sm:text-base text-gray-900 mb-1 truncate">{{ inv.board_title }}</h3>
                  <p class="text-xs text-gray-600 truncate">دعوت‌کننده: {{ inv.invited_by_username || 'سیستم' }}</p>
                </div>
                <span 
                  class="inline-flex items-center px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs font-medium flex-shrink-0 ml-2"
                  :class="{'bg-emerald-100 text-emerald-700': inv.role==='admin', 'bg-blue-100 text-blue-700': inv.role!=='admin'}"
                >
                  {{ inv.role === 'admin' ? 'ادمین' : 'عضو' }}
                </span>
              </div>
              
              <div class="flex space-x-2 space-x-reverse">
                <button 
                  @click="respondInvitation(inv.id, 'accept')" 
                  class="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white text-xs sm:text-sm font-medium py-1.5 sm:py-2 px-2 sm:px-3 rounded-md sm:rounded-lg transition-colors"
                >
                  پذیرش
                </button>
                <button 
                  @click="respondInvitation(inv.id, 'reject')" 
                  class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs sm:text-sm font-medium py-1.5 sm:py-2 px-2 sm:px-3 rounded-md sm:rounded-lg transition-colors"
                >
                  رد
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete confirm dialog -->
  <DeleteConfirmDialog
      :visible="showDeleteDialog"
      message="آیا از حذف این برد مطمئن هستید؟"
      @cancel="showDeleteDialog=false"
      @confirm="confirmDelete"
  />
  <!-- Activity dialog -->
  <ActivityDialog
      :visible="showActivitiesDialog"
      :activities="activitiesList"
      @close="showActivitiesDialog=false"
  />
  <!-- Board members dialog -->
  <MembersDialog :visible="showMembersDialog" :members="membersList" @close="showMembersDialog=false" />
  <!-- Board invitations dialog -->
  <InvitationDialog :visible="showInvDialog" :invitations="invitationsList" @close="showInvDialog=false" />
  <!-- Invite dialog -->
    <InviteDialog
      :visible="showInviteDialog"
      :type="inviteType"
      :error="inviteError"
      :success="inviteSuccess"
      @cancel="showInviteDialog=false"
      @submit="handleInviteSubmit"
    />
  <!-- Create Board Dialog -->
  <CreateBoardDialog
    :visible="showCreateDialog"
    :error="createError"
    @cancel="showCreateDialog=false"
    @submit="handleCreateSave"
  />
  <!-- Board Edit Dialog -->
  <BoardEditDialog
    :visible="showDialog"
    :board="selectedBoard"
    :error="dialogError"
    @cancel="showDialog=false"
    @save="handleDialogSave"
  />
  <!-- Board Menu Modal v2024 -->
  <div v-if="showBoardMenuModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-end z-[99999]" @click="showBoardMenuModal=false">
    <div class="bg-white rounded-2xl shadow-2xl w-80 mr-4 max-h-[90vh] overflow-y-auto" @click.stop>
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">تنظیمات برد</h3>
          <button @click="showBoardMenuModal=false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <p class="text-sm text-gray-600 mt-1">{{ selectedBoardForMenu?.title }}</p>
      </div>

      <!-- Menu Options -->
      <div class="py-2">
        <button @click="handleMenuActivities(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>تاریخچه</span>
        </button>
        
        <button @click="handleMenuMembers(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
          </svg>
          <span>کاربران</span>
        </button>
        
        <button 
          v-if="['owner','admin'].includes(selectedBoardForMenu?.current_user_role)"
          @click="handleMenuInvitations(selectedBoardForMenu.id)" 
          class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          <span>دعوت‌ها</span>
        </button>
        
        <template v-if="['owner','admin'].includes(selectedBoardForMenu?.current_user_role)">
          <hr class="my-2">
          <button @click="handleMenuInviteUser(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
            <span>دعوت کاربر</span>
          </button>
          <button @click="handleMenuInviteEmail(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zM12 8v1.5a3.5 3.5 0 017 0V8a3.5 3.5 0 013.5 3.5z"/>
            </svg>
            <span>دعوت کاربر با ایمیل</span>
          </button>
          <button @click="handleMenuEdit(selectedBoardForMenu)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <span>ویرایش</span>
          </button>
        </template>
        
        <hr class="my-2">
        <template v-if="selectedBoardForMenu?.current_user_role === 'owner'">
          <button @click="handleMenuDelete(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            <span>حذف برد</span>
          </button>
        </template>
        <template v-else>
          <button @click="handleMenuLeave(selectedBoardForMenu.id)" class="flex items-center space-x-3 space-x-reverse w-full px-6 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            <span>ترک برد</span>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import InviteDialog from '../components/InviteDialog.vue';
import ActivityDialog from '../components/ActivityDialog.vue';
import InvitationDialog from '../components/InvitationDialog.vue';
import MembersDialog from '../components/MembersDialog.vue';
import BoardEditDialog from '../components/BoardEditDialog.vue';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog.vue';
import CreateBoardDialog from '../components/CreateBoardDialog.vue';
import { useBoardsStore } from '../stores/boards';
import { useInvitationsStore } from '../stores/invitations';
import { useRouter } from 'vue-router';

const boardsStore = useBoardsStore();
const invitationsStore = useInvitationsStore();
const router = useRouter(); // still used for board navigation

const errorMessage = ref('');
const showDialog = ref(false);
const selectedBoard = ref(null);
const dialogError = ref('');
const showCreateDialog = ref(false);
const createError = ref('');
const showDeleteDialog = ref(false);
const showInviteDialog = ref(false);
const showActivitiesDialog = ref(false);
const showMembersDialog = ref(false);
const showInvDialog = ref(false);
const showBoardMenuModal = ref(false);
const selectedBoardForMenu = ref(null);
const membersList = ref([]);
const invitationsList = ref([]);
const activitiesList = ref([]);
const inviteType = ref('user');
const inviteError = ref('');
const inviteSuccess = ref('');
let inviteBoardId = null;
const deleteTargetId = ref(null);

const handleCreateSave = async (data) => {
  createError.value = '';
  try {
    const newBoard = await boardsStore.createBoard(data);
    showCreateDialog.value = false;
    // optionally navigate to board
    // router.push(`/boards/${newBoard.id}`);
  } catch (err) {
    createError.value = typeof err === 'string' ? err : (err.detail || JSON.stringify(err));
    // err may be string or object from backend
    errorMessage.value = typeof err === 'string' ? err : (err.detail || JSON.stringify(err));
  }
};

function toggleMenu(boardId) {
  // FORCE CACHE REFRESH - Find the board and show modal
  console.log('MODAL SHOULD OPEN NOW!', boardId);
  const board = boardsStore.boards.find(b => b.id === boardId);
  if (board) {
    selectedBoardForMenu.value = board;
    showBoardMenuModal.value = true;
    console.log('Modal state:', showBoardMenuModal.value, selectedBoardForMenu.value);
  }
}

// Modal event handlers
const handleMenuActivities = async (boardId) => {
  showBoardMenuModal.value = false;
  await openActivities(boardId);
};

const handleMenuMembers = async (boardId) => {
  showBoardMenuModal.value = false;
  await openMembers(boardId);
};

const handleMenuInvitations = async (boardId) => {
  showBoardMenuModal.value = false;
  await openInvitations(boardId);
};

const handleMenuInviteUser = (boardId) => {
  showBoardMenuModal.value = false;
  openInvite(boardId, 'user');
};

const handleMenuInviteEmail = (boardId) => {
  showBoardMenuModal.value = false;
  openInvite(boardId, 'email');
};

const handleMenuEdit = (board) => {
  showBoardMenuModal.value = false;
  openEditDialog(board);
};

const handleMenuDelete = (boardId) => {
  showBoardMenuModal.value = false;
  prepareDelete(boardId);
};

const handleMenuLeave = async (boardId) => {
  showBoardMenuModal.value = false;
  await leaveBoard(boardId);
};

onMounted(() => {
  invitationsStore.fetchInvitations();
  boardsStore.fetchBoards();
});

// Remove duplicate toggleMenu function - using the one defined above

const openEditDialog = (board) => {
  selectedBoard.value = { ...board };
  dialogError.value = '';
  showDialog.value = true;
};

const handleDialogSave = async (data) => {
  if (!selectedBoard.value) return;
  try {
    await boardsStore.updateBoard(selectedBoard.value.id, data);
    showDialog.value = false;
    selectedBoard.value = null;
  } catch (err) {
    dialogError.value = typeof err === 'string' ? err : (err.detail || JSON.stringify(err));
  }
};

const prepareDelete = (id) => {
  console.log('prepareDelete called', id);
  deleteTargetId.value = id;
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  if (!deleteTargetId.value) return;
  try {
    await boardsStore.deleteBoard(deleteTargetId.value);
    openMenuId.value = null;
    showDeleteDialog.value = false;
    deleteTargetId.value = null;
  } catch (err) {
    errorMessage.value = typeof err === 'string' ? err : (err.detail || JSON.stringify(err));
    showDeleteDialog.value = false;
  }
};

const openInvite = (boardId, type) => {
  inviteBoardId = boardId;
  inviteType.value = type;
  inviteError.value = '';
  inviteSuccess.value = '';
  showInviteDialog.value = true;
  // Close the board menu when opening invite dialog
  openMenuId.value = null;
};

const handleInviteSubmit = async ({ value, role }) => {
  inviteError.value = '';
  inviteSuccess.value = '';
  if (!value) return;
  try {
    if (inviteType.value === 'user') {
      await boardsStore.inviteMember(inviteBoardId, value, role);
    } else {
      await boardsStore.inviteEmail(inviteBoardId, value, role);
    }
    inviteSuccess.value = 'دعوت ارسال شد.';
  } catch (e) {
    inviteError.value = typeof e === 'string' ? e : (e.detail || JSON.stringify(e));
  }
};

const openActivities = async (id) => {
  try {
    activitiesList.value = await boardsStore.fetchActivities(id);
    showActivitiesDialog.value = true;
    openMenuId.value = null;
  } catch (e) { /* handled globally */ }
};

const openMembers = async (id) => {
  try {
    membersList.value = await boardsStore.fetchMembers(id);
    showMembersDialog.value = true;
    openMenuId.value = null;
  } catch (e) { /* ignore */ }
};

const openInvitations = async (id) => {
  try {
    invitationsList.value = await boardsStore.fetchInvitations(id);
    showInvDialog.value = true;
    openMenuId.value = null;
  } catch (e) { /* ignore */ }
};

const respondInvitation = async (id, action) => {
  await invitationsStore.respondInvitation(id, action);
  // Refresh boards list in case user joined a new board
  boardsStore.fetchBoards();
};

const leaveBoard = async (id) => {
  await boardsStore.leaveBoard(id);
};

const goToBoard = (id) => {
  router.push(`/boards/${id}`);
};

const getRoleText = (role) => {
  const roleMap = {
    'owner': 'مالک',
    'admin': 'ادمین',
    'member': 'عضو'
  };
  return roleMap[role] || role;
};

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
</script>
