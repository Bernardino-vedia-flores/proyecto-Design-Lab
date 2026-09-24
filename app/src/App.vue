<template>
  <div class="app-wrapper">
    <NavBar />
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script>
import NavBar from './components/navbar.vue'

export default {
  components: { NavBar }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  width: 100%;
  min-height: 100vh;
  background-color: #0a0a0a;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  width: 100%;
  min-height: 100vh;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.app-main {
  flex: 1;
  width: 100%;
}
</style>