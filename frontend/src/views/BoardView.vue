<template>
  <div>
    <div class="p-4 overflow-x-auto flex space-x-4" v-if="board">
      <ListColumn v-for="list in lists" :key="list.id" :list="list" />
    </div>
    <div v-else class="flex items-center justify-center h-screen">در حال بارگیری...</div>

    <TaskModal v-if="tasksStore.modalOpen" />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useTasksStore } from '../stores/tasks';
import TaskModal from '../components/TaskModal.vue';
import { useRoute } from 'vue-router';
import { useBoardsStore } from '../stores/boards';
import { useListsStore } from '../stores/lists';
import ListColumn from '../components/ListColumn.vue';

const route = useRoute();
const boardsStore = useBoardsStore();
const listsStore = useListsStore();

onMounted(async () => {
  const boardId = route.params.id;
  await boardsStore.fetchBoard(boardId);
  await listsStore.fetchLists(boardId);
});

const board = computed(() => boardsStore.currentBoard);
const lists = computed(() => listsStore.lists);

const tasksStore = useTasksStore();
</script>
