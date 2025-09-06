<template>
  <div class="p-6 flex flex-col md:flex-row gap-4" dir="rtl">
    <!-- Left section -->
    <div class="flex-[0.7] bg-gray-100 dark:bg-gray-600 p-4 rounded">
    <div class="flex items-center justify-between mb-2">
      <h1 class="text-2xl font-bold text-right">بردها</h1>
      <button @click="showCreateDialog=true" class="bg-sky-600 text-white px-4 py-2 rounded hover:bg-sky-700">ایجاد برد جدید</button>
    </div>
    <p v-if="errorMessage" class="text-red-600 mb-4">{{ errorMessage }}</p>
    <div class="grid gap-4 grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
      <div
        v-for="board in boardsStore.boards"
        :key="board.id"
        class="bg-white p-4 shadow rounded hover:bg-gray-100 relative"
      >
        <div class="flex justify-between items-start cursor-pointer" @click="goToBoard(board.id)">
          <span class="font-medium">{{ board.title }}</span>
          <button @click.stop="toggleMenu(board.id)" class="text-gray-500 hover:text-gray-700 board-menu">
            ⋮
          </button>
        </div>
        <p class="text-sm text-gray-600 mt-2">اعضا: {{ board.members_count }}</p>
        <span v-if="board.current_user_role" class="inline-block mt-2 px-2 py-1 rounded-full text-xs font-semibold"
              :class="{
                'bg-emerald-100 text-emerald-700': board.current_user_role==='owner',
                'bg-indigo-100 text-indigo-700': board.current_user_role==='admin',
                'bg-gray-100 text-gray-700': board.current_user_role==='member'
              }">
          {{ board.current_user_role }}
        </span>
        <!-- dropdown menu -->
        <div
          v-if="openMenuId === board.id"
          class="absolute left-2 top-8 bg-white border shadow rounded z-10 text-sm w-36 board-menu"
        >
          <!-- invite/edit for owner or admin -->
          <template v-if="['owner','admin'].includes(board.current_user_role)">
            <button @click="openInvite(board.id, 'user')" class="block w-full text-left px-2 py-1 hover:bg-gray-100">دعوت کاربر</button>
            <button @click="openInvite(board.id, 'email')" class="block w-full text-left px-2 py-1 hover:bg-gray-100">دعوت کاربر جدید</button>
            <button @click="openEditDialog(board)" class="block w-full text-left px-2 py-1 hover:bg-gray-100">ویرایش</button>
          </template>
          <!-- destructive option -->
          <template v-if="board.current_user_role === 'owner'">
            <button @click="prepareDelete(board.id)" class="block w-full text-left px-2 py-1 hover:bg-gray-100 text-red-600">حذف برد</button>
          </template>
          <template v-else>
            <button @click="leaveBoard(board.id)" class="block w-full text-left px-2 py-1 hover:bg-gray-100 text-red-600">ترک برد</button>
          </template>
        </div>
      </div>
    </div>
    <BoardEditDialog
      :visible="showDialog"
      :board="selectedBoard"
      :error="dialogError"
      @cancel="showDialog=false"
      @save="handleDialogSave"
    />
    <CreateBoardDialog
      :visible="showCreateDialog"
      :error="createError"
      @cancel="showCreateDialog=false"
      @save="handleCreateSave"
    />
    </div> <!-- end left section -->
    <!-- Right section -->
    <div class="flex-[0.3] bg-gray-50 dark:bg-gray-500 p-4 rounded overflow-y-auto max-h-screen">
      <h2 class="text-xl font-bold mb-4 text-right">دعوت‌ها</h2>
      <p v-if="invitationsStore.invitations.length === 0" class="text-gray-600 dark:text-gray-300 text-right">هیچ دعوتی وجود ندارد.</p>
      <div v-for="inv in invitationsStore.invitations" :key="inv.id" class="bg-white dark:bg-gray-700 shadow rounded p-3 mb-3 flex flex-col gap-2">
        <div class="flex justify-between items-center">
          <h3 class="font-semibold">{{ inv.board_title }}</h3>
          <span class="text-sm" :class="{'text-green-600': inv.role==='admin', 'text-gray-600': inv.role!=='admin'}">{{ inv.role === 'admin' ? 'ادمین' : 'عضو' }}</span>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-300">دعوت‌کننده: {{ inv.invited_by_username || 'سیستم' }}</p>
        <div class="flex gap-2 self-end">
          <button @click="respondInvitation(inv.id, 'accept')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-sm">پذیرش</button>
          <button @click="respondInvitation(inv.id, 'reject')" class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm">رد</button>
        </div>
      </div>
    </div>
  </div> <!-- end root flex container -->

  <!-- Delete confirm dialog -->
  <DeleteConfirmDialog
      :visible="showDeleteDialog"
      message="آیا از حذف این برد مطمئن هستید؟"
      @cancel="showDeleteDialog=false"
      @confirm="confirmDelete"
  />
  <!-- Invite dialog -->
    <InviteDialog
      :visible="showInviteDialog"
      :type="inviteType"
      :error="inviteError"
      :success="inviteSuccess"
      @cancel="showInviteDialog=false"
      @submit="handleInviteSubmit"
    />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import InviteDialog from '../components/InviteDialog.vue';
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
const openMenuId = ref(null);
const showDialog = ref(false);
const selectedBoard = ref(null);
const dialogError = ref('');
const showCreateDialog = ref(false);
const createError = ref('');
const showDeleteDialog = ref(false);
const showInviteDialog = ref(false);
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

function handleOutsideClick(e) {
  // If the click is not inside a dropdown menu button area, close
  if (!e.target.closest('.board-menu')) {
    openMenuId.value = null;
  }
}

onMounted(() => {
  invitationsStore.fetchInvitations();
  boardsStore.fetchBoards();
  window.addEventListener('click', handleOutsideClick);
});

onBeforeUnmount(() => {
  window.removeEventListener('click', handleOutsideClick);
});

const toggleMenu = (id) => {
  openMenuId.value = openMenuId.value === id ? null : id;
};

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
</script>
