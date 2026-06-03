<template>
  <div class="app">
    <nav v-if="authStore.isLoggedIn" class="nav-bar">
      <router-link to="/wardrobe">👗 衣橱</router-link>
      <router-link to="/recommend">✨ 推荐</router-link>
      <router-link to="/calendar">📅 日历</router-link>
      <router-link to="/profile">👤 我的</router-link>
      <a @click="logout" class="logout-link">退出</a>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { authStore } from './stores/auth.js'

const router = useRouter()

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #faf5ff;
  color: #333;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(168, 85, 247, 0.3);
}

.nav-bar a {
  color: white;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  transition: background 0.2s;
  cursor: pointer;
}

.nav-bar a:hover,
.nav-bar a.router-link-active {
  background: rgba(255, 255, 255, 0.25);
}

.logout-link {
  font-size: 12px !important;
  opacity: 0.8;
}

.main-content {
  flex: 1;
  padding: 16px;
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .main-content {
    max-width: 900px;
    padding: 24px;
  }
}
</style>
