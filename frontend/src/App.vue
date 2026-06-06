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
              <!-- Desktop top nav -->
              <nav class="top-nav">
                <div class="nav-inner">
                  <div class="nav-logo">
                    <div class="logo-seal">
                      <n-icon :component="ShirtOutline" :size="18" color="#FFFFFF" />
                    </div>
                    <span class="logo-text">衫 间</span>
                  </div>

                  <div class="nav-links">
                    <a
                      v-for="item in menuOptions"
                      :key="item.key"
                      :class="['nav-link', { active: currentRoute === item.key }]"
                      @click="onMenuSelect(item.key)"
                    >
                      {{ item.label }}
                    </a>
                  </div>

                  <div class="nav-right">
                    <a class="logout-link" @click="logout">退出</a>
                  </div>
                </div>
              </nav>

              <!-- Main content -->
              <main class="main-area">
                <div class="main-content">
                  <router-view v-slot="{ Component }">
                    <transition name="page-fade" mode="out-in">
                      <component :is="Component" />
                    </transition>
                  </router-view>
                </div>
              </main>

              <!-- Mobile bottom tab bar -->
              <nav class="mobile-tabs">
                <a
                  v-for="item in menuOptions"
                  :key="item.key"
                  :class="['mobile-tab', { active: currentRoute === item.key }]"
                  @click="onMenuSelect(item.key)"
                >
                  <n-icon :component="item.iconComponent" :size="20" />
                  <span>{{ item.label }}</span>
                </a>
              </nav>
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
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const currentRoute = computed(() => route.path)

const themeOverrides = {
  common: {
    primaryColor: '#A0815A',
    primaryColorHover: '#B8956E',
    primaryColorPressed: '#8A6F4E',
    primaryColorSuppl: '#C27C4E',
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
    borderRadius: '8px',
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
  --color-primary: #A0815A;
  --color-primary-hover: #B8956E;
  --color-primary-pressed: #8A6F4E;
  --color-accent: #C27C4E;
  --color-bg: #F5F0E8;
  --color-surface: #FFFDF8;
  --color-text: #2E2A23;
  --color-text-secondary: #8C8478;
  --color-border: #E0D8CC;
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #F5F0E8;
  color: #2E2A23;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-root {
  min-height: 100vh;
}

/* Top nav */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(245, 240, 232, 0.85);
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
  border-bottom: 1px solid #E0D8CC;
  z-index: 200;
  display: flex;
  align-items: center;
}

.nav-inner {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-seal {
  width: 36px;
  height: 36px;
  background: #A0815A;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2E2A23;
  letter-spacing: 2px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  font-size: 14px;
  color: #8C8478;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  padding: 16px 0;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.nav-link:hover {
  color: #2E2A23;
}

.nav-link.active {
  color: #A0815A;
  border-bottom-color: #A0815A;
}

.nav-right {
  display: flex;
  align-items: center;
}

.logout-link {
  font-size: 13px;
  color: #8C8478;
  cursor: pointer;
  transition: color 0.2s ease;
  text-decoration: none;
}

.logout-link:hover {
  color: #2E2A23;
}

/* Main area */
.main-area {
  padding-top: 56px;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

.main-content {
  width: 100%;
  max-width: 1200px;
  padding: 36px 36px 80px;
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* Mobile bottom tabs */
.mobile-tabs {
  display: none;
}

@media (max-width: 768px) {
  .top-nav {
    display: none;
  }

  .main-area {
    padding-top: 0;
    padding-bottom: 56px;
  }

  .main-content {
    padding: 24px 16px 70px;
  }

  .mobile-tabs {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: rgba(245, 240, 232, 0.85);
    backdrop-filter: blur(8px) saturate(120%);
    -webkit-backdrop-filter: blur(8px) saturate(120%);
    border-top: 1px solid #E0D8CC;
    z-index: 200;
    align-items: center;
    justify-content: space-around;
  }

  .mobile-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    color: #8C8478;
    cursor: pointer;
    text-decoration: none;
    padding: 6px 0;
    transition: color 0.2s ease;
  }

  .mobile-tab:hover {
    color: #2E2A23;
  }

  .mobile-tab.active {
    color: #A0815A;
  }
}
</style>
