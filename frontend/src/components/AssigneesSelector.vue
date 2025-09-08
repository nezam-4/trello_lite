<template>
  <div class="flex items-center space-x-1 rtl:space-x-reverse">
    <!-- Assigned users circles -->
    <div
      v-for="user in assignedDetails"
      :key="user.id"
      class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-semibold cursor-pointer hover:bg-blue-700 transition-colors"
      :title="user.full_name || user.username"
      @click="handleUserClick(user)"
    >
      <span :title="(user.full_name || user.username)">
        {{ user.initials }}
      </span>
    </div>

    <!-- Plus button -->
    <button
      class="w-8 h-8 rounded-full bg-gray-300 hover:bg-gray-400 flex items-center justify-center text-lg"
      @click="open"
      title="Assign members"
    >
      +
    </button>

    <!-- Dialog -->
    <teleport to="body">
      <div v-if="dialogOpen" class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-40" @click.self="close">
        <div class="bg-white rounded-lg w-80 max-h-[75vh] overflow-y-auto p-4" @click.stop>
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-bold text-lg">انتخاب اعضا</h3>
            <button @click="close">✕</button>
          </div>
          <ul>
            <li
              v-for="member in members"
              :key="member.user_id ?? member.id"
              class="flex items-center justify-between py-2 border-b text-sm"
            >
              <div class="flex items-center space-x-2 rtl:space-x-reverse">
                <div class="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs">
                  {{ getInitials(member) }}
                </div>
                <div class="flex flex-col leading-tight">
                  <span class="font-medium">{{ member.full_name || member.username }}</span>
                  <span class="text-gray-500 text-xs">@{{ member.username }}</span>
                </div>
              </div>
              <input type="checkbox" v-model="selectedIds" :value="member.user_id ?? member.id" />
            </li>
          </ul>
          <div class="flex justify-end mt-4 space-x-2 rtl:space-x-reverse">
            <button @click="save" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded">ذخیره</button>
            <button @click="close" class="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">انصراف</button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useBoardsStore } from '../stores/boards';
import { useTasksStore } from '../stores/tasks';

const props = defineProps({
  task: { type: Object, required: true },
});
const emit = defineEmits(['updated', 'userClick']);

const boardsStore = useBoardsStore();
const tasksStore = useTasksStore();

const dialogOpen = ref(false);
const members = ref([]);
const selectedIds = ref([]);

const assignedDetails = computed(() => {
  if (members.value.length) {
    return members.value.filter((m) => props.task.assigned_to.includes((m.user_id ?? m.id))).map((m) => ({
      ...m,
      id: m.user_id ?? m.id,
      initials: getInitials(m),
      username: m.username || m.user_username,
      full_name: m.full_name,
      email: m.email || '',
      role: m.role || 'member'
    }));
  } else {
    // Fallback when members data is not loaded yet
    return props.task.assigned_to_usernames.map((username, idx) => ({
      id: props.task.assigned_to[idx] || idx,
      username,
      full_name: '',
      email: '',
      role: 'member',
      initials: username.slice(0, 2).toUpperCase(),
    }));
  }
});

function getInitials(user) {
  if (user.full_name) {
    return user.full_name
      .split(' ')
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  }
  if (user.username || user.user_username) {
    const uname = user.username || user.user_username;
    return uname.slice(0, 2).toUpperCase();
  }
  return "??";
}

async function open() {
  try {
    await fetchMembers();
    selectedIds.value = [...props.task.assigned_to];
    dialogOpen.value = true;
  } catch (e) {
    console.error('Failed to open assignees selector', e);
    // Optionally toast error
  }
}

function close() {
  dialogOpen.value = false;
}

async function fetchMembers() {
  const list = await boardsStore.fetchMembers(props.task.board);
  members.value = list;
}

function handleUserClick(user) {
  console.log('User clicked:', user);
  emit('userClick', user);
}

async function save() {
  try {
    await tasksStore.updateTask(props.task.id, { assigned_to: selectedIds.value });
    await tasksStore.fetchTask(props.task.id);
    emit('updated');
    close();
  } catch (e) {
    console.error('Failed to save assignees', e);
  }
}
</script>

<style scoped>
</style>
