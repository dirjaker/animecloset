<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <div class="app-root">
            <template v-if="!authStore.isLoggedIn">
              <router-view />
            </template>

            <template v-else>
              <div class="app-layout">
                <div class="mobile-header">
                  <n-button quaternary @click="showDrawer = true" size="large">
                    <template #icon><n-icon :component="MenuOutline" /></template>
                  </n-button>
                  <span class="mobile-title">衣 楷</span>
                  <n-button quaternary circle size="small" @click="logout">
                    <template #icon><n-icon :component="LogOutOutline" /></template>
                  </n-button>
                </div>

                <div v-if="showDrawer" class="drawer-overlay" @click="showDrawer = false" />
                <aside class="sidebar" :class="{ open: showDrawer }">
                  <div class="sidebar-inner">
                    <div class="sidebar-logo">
                      <div class="logo-icon">
                        <n-icon :component="ShirtOutline" :size="20" color="#FFFFFF" />
                      </div>
                      <span>衣 楷</span>
                    </div>

                    <nav class="sidebar-nav">
                      <a
                        v-for="item in menuOptions"
                        :key="item.key"
                        :class="['nav-item', { active: currentRoute === item.key }]"
                        @click="onMenuSelect(item.key)"
                      >
                        <n-icon :component="item.iconComponent" :size="20" />
                        <span>{{ item.label }}</span>
                      </a>
                    </nav>

                    <div class="sidebar-divider"></div>

                    <div class="sidebar-footer">
                      <a class="logout-link" @click="logout">退出登录</a>
                    </div>
                  </div>
                </aside>

                <main class="main-area">
                  <div class="main-content">
                    <router-view v-slot="{ Component }">
                      <transition name="page-fade" mode="out-in">
                        <component :is="Component" />
                      </transition>
                    </router-view>
                  </div>
                </main>
              </div>
            </template>
          </div>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { authStore } from './stores/auth.js'
import {
  ShirtOutline,
  CalendarOutline,
  SparklesOutline,
  PersonOutline,
  LogOutOutline,
  MenuOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const showDrawer = ref(false)

const currentRoute = computed(() => route.path)

const themeOverrides = {
  common: {
    primaryColor: '#5B7D6A',
    primaryColorHover: '#6B8D7A',
    primaryColorPressed: '#4A6C59',
    primaryColorSuppl: '#7FA88E',
    borderRadius: '8px',
    borderRadiusSmall: '6px',
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusSmall: '6px',
  },
  Card: {
    borderRadius: '8px',
  },
  Input: {
    borderRadius: '4px',
  },
  Tag: {
    borderRadius: '6px',
  },
}

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  { label: '衣橱', key: '/wardrobe', icon: renderIcon(ShirtOutline), iconComponent: ShirtOutline },
  { label: '推荐', key: '/recommend', icon: renderIcon(SparklesOutline), iconComponent: SparklesOutline },
  { label: '日历', key: '/calendar', icon: renderIcon(CalendarOutline), iconComponent: CalendarOutline },
  { label: '我的', key: '/profile', icon: renderIcon(PersonOutline), iconComponent: PersonOutline },
]

function onMenuSelect(key) {
  router.push(key)
  showDrawer.value = false
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-primary: #5B7D6A;
  --color-primary-hover: #6B8D7A;
  --color-primary-pressed: #4A6C59;
  --color-accent: #C49A6C;
  --color-bg: #F6F3EE;
  --color-surface: #FFFDF9;
  --color-text: #2C2A25;
  --color-text-secondary: #8A8578;
  --color-border: #E8E3DA;
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #F6F3EE;
  color: #2C2A25;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-root {
  min-height: 100vh;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 200px;
  background: #FDFCF9;
  background-image:
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 40px,
      rgba(196, 154, 108, 0.03) 40px,
      rgba(196, 154, 108, 0.03) 41px
    ),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 60px,
      rgba(196, 154, 108, 0.02) 60px,
      rgba(196, 154, 108, 0.02) 61px
    );
  border-right: 1px solid #E8E3DA;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 28px 0 20px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 24px 24px;
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2C2A25;
  letter-spacing: 2px;
  border-bottom: 1px solid #E8E3DA;
  margin-bottom: 16px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  background: #5B7D6A;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #8A8578;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  color: #2C2A25;
  background: rgba(91, 125, 106, 0.04);
}

.nav-item.active {
  color: #5B7D6A;
  border-left-color: #5B7D6A;
  background: rgba(91, 125, 106, 0.06);
}

.sidebar-divider {
  height: 1px;
  background: #E8E3DA;
  margin: 16px 24px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 0 24px;
}

.logout-link {
  font-size: 13px;
  color: #8A8578;
  cursor: pointer;
  transition: color 0.2s ease;
  text-decoration: none;
}

.logout-link:hover {
  color: #2C2A25;
}

/* Main area */
.main-area {
  flex: 1;
  margin-left: 200px;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

.main-content {
  width: 100%;
  max-width: 1080px;
  padding: 36px 48px;
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* Mobile */
.mobile-header {
  display: none;
}

.drawer-overlay {
  display: none;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  .sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(44, 42, 37, 0.1);
  }

  .drawer-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: #F6F3EE;
    opacity: 0.85;
    z-index: 199;
    animation: fadeOverlay 0.2s ease;
  }

  @keyframes fadeOverlay {
    from { opacity: 0; }
    to { opacity: 0.85; }
  }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #FDFCF9;
    border-bottom: 1px solid #E8E3DA;
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .mobile-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 18px;
    font-weight: 600;
    color: #2C2A25;
    letter-spacing: 2px;
  }

  .main-area {
    margin-left: 0;
  }

  .main-content {
    padding: 24px 20px;
  }
}
</style>
