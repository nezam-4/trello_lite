<template>
  <div class="p-6" dir="rtl">
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
        <!-- dropdown menu -->
        <div
          v-if="openMenuId === board.id"
          class="absolute left-2 top-8 bg-white border shadow rounded z-10 text-sm w-32 board-menu"
        >
                    <button @click="openInvite(board.id, 'user')" class="block w-full text-left px-2 py-1 hover:bg-gray-100">دعوت کاربر</button>
          <button @click="openInvite(board.id, 'email')" class="block w-full text-left px-2 py-1 hover:bg-gray-100">دعوت کاربر جدید</button>
          <button @click="openEditDialog(board)" class="block w-full text-left px-2 py-1 hover:bg-gray-100">ویرایش</button>
          <button @click="prepareDelete(board.id)" class="block w-full text-left px-2 py-1 hover:bg-gray-100 text-red-600">حذف</button>
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
    <DeleteConfirmDialog
      :visible="showDeleteDialog"
      message="آیا از حذف این برد مطمئن هستید؟"
      @cancel="showDeleteDialog=false"
      @confirm="confirmDelete"
    />
  </div>
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
import { useRouter } from 'vue-router';

const boardsStore = useBoardsStore();
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

const goToBoard = (id) => {
  router.push(`/boards/${id}`);
};
</script>
