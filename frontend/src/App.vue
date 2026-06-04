<template>
  <div class="app">
    <nav v-if="authStore.isLoggedIn" class="nav-bar">
      <div class="nav-inner">
        <span class="nav-logo">🏠 AnimeCloset</span>
        <div class="nav-links">
          <router-link to="/wardrobe">👗 衣橱</router-link>
          <router-link to="/recommend">✨ 推荐</router-link>
          <router-link to="/calendar">📅 日历</router-link>
          <router-link to="/profile">👤 我的</router-link>
          <a @click="logout" class="logout-link">退出</a>
        </div>
      </div>
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
  background: #FFF8F0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(212, 165, 116, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(91, 124, 80, 0.06) 0%, transparent 50%),
    radial-gradient(circle at 50% 80%, rgba(193, 122, 58, 0.05) 0%, transparent 50%);
  color: #4A3728;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* === 木屋导航栏 === */
.nav-bar {
  background: linear-gradient(135deg, #5C4033 0%, #8B6914 50%, #6B4226 100%);
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow:
    0 3px 12px rgba(92, 64, 51, 0.3),
    inset 0 -1px 0 rgba(255, 255, 255, 0.1);
  /* 木纹质感 */
  background-image:
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 40px,
      rgba(0,0,0,0.03) 40px,
      rgba(0,0,0,0.03) 42px
    );
}

.nav-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 52px;
}

.nav-logo {
  font-size: 16px;
  font-weight: 700;
  color: #F5E6D3;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-bar a {
  color: #E8D5B7;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.nav-bar a:hover,
.nav-bar a.router-link-active {
  background: rgba(255, 248, 240, 0.15);
  color: #FFF8F0;
}

.logout-link {
  font-size: 12px !important;
  opacity: 0.7;
  color: #D4A574 !important;
}

/* === 主内容区 === */
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

/* === 通用木屋卡片样式 === */
.wood-card {
  background: #FFF5EB;
  border: 1px solid #D4A574;
  border-radius: 12px;
  padding: 20px;
  box-shadow:
    0 2px 8px rgba(139, 105, 20, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.8) inset;
}

/* === 通用木屋按钮 === */
.wood-btn {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: #FFF8F0;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(139, 105, 20, 0.2);
}

.wood-btn:hover {
  background: linear-gradient(135deg, #D4893A, #9B7924);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 105, 20, 0.3);
}

.wood-btn-green {
  background: linear-gradient(135deg, #5B7C50, #4A6B3F);
}

.wood-btn-green:hover {
  background: linear-gradient(135deg, #6B8C60, #5A7B4F);
}
</style>
