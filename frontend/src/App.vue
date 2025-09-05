<template>
  <ErrorAlert />
  <Header />
  <router-view />
</template>

<script setup>
import Header from './components/Header.vue';
import ErrorAlert from './components/ErrorAlert.vue';
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>
