import { createRouter, createWebHistory } from 'vue-router';

// Lazy-loaded route components
const LoginView = () => import('../views/LoginView.vue');
const RegisterView = () => import('../views/RegisterView.vue');
const BoardListView = () => import('../views/BoardListView.vue');
const BoardView = () => import('../views/BoardView.vue');
const ProfileView = () => import('../views/ProfileView.vue');
const TaskDetailView = () => import('../views/TaskDetailView.vue');
const ChangePasswordView = () => import('../views/ChangePasswordView.vue');
const ForgotPasswordView = () => import('../views/ForgotPasswordView.vue');
const ResetPasswordView = () => import('../views/ResetPasswordView.vue');

const routes = [
  { path: '/login', component: LoginView, name: 'login' },
  { path: '/register', component: RegisterView, name: 'register' },
  { path: '/forgot-password', component: ForgotPasswordView, name: 'forgot-password' },
  { path: '/reset-password', component: ResetPasswordView, name: 'reset-password' },
  { path: '/boards', component: BoardListView, name: 'boards' },
  { path: '/boards/:id', component: BoardView, name: 'board', props: true },
  { path: '/tasks/:id', component: TaskDetailView, name: 'task', props: true },
  { path: '/profile', component: ProfileView, name: 'profile' },
  { path: '/change-password', component: ChangePasswordView, name: 'change-password' },
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
