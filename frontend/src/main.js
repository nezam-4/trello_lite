import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// Force reload - timestamp: 2025-01-09 16:01
const app = createApp(App);
app.use(createPinia());
app.use(router);

app.mount('#app');
