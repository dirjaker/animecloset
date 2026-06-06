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
                  <span class="mobile-title">AnimeCloset</span>
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
                      <span>AnimeCloset</span>
                    </div>

                    <n-menu
                      :value="currentRoute"
                      :options="menuOptions"
                      :root-indent="20"
                      :indent="20"
                      @update:value="onMenuSelect"
                    />

                    <div class="sidebar-footer">
                      <n-button quaternary block @click="logout">
                        <template #icon><n-icon :component="LogOutOutline" /></template>
                        退出登录
                      </n-button>
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
    primaryColor: '#7C5CFC',
    primaryColorHover: '#9B82FD',
    primaryColorPressed: '#6344E0',
    primaryColorSuppl: '#B4A2FE',
    borderRadius: '14px',
    borderRadiusSmall: '10px',
    fontFamily: "'Outfit', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
  Button: {
    borderRadiusMedium: '14px',
    borderRadiusSmall: '10px',
  },
  Card: {
    borderRadius: '18px',
  },
  Input: {
    borderRadius: '12px',
  },
  Tag: {
    borderRadius: '10px',
  },
}

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  { label: '衣橱', key: '/wardrobe', icon: renderIcon(ShirtOutline) },
  { label: '推荐', key: '/recommend', icon: renderIcon(SparklesOutline) },
  { label: '日历', key: '/calendar', icon: renderIcon(CalendarOutline) },
  { label: '我的', key: '/profile', icon: renderIcon(PersonOutline) },
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

body {
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #FAFBFE;
  color: #1A1625;
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

/* ───── Sidebar ───── */
.sidebar {
  width: 240px;
  background: #FFFFFF;
  border-right: 1px solid rgba(124, 92, 252, 0.08);
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
  padding: 32px 0 24px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 28px 28px;
  font-size: 20px;
  font-weight: 700;
  color: #1A1625;
  letter-spacing: -0.5px;
  border-bottom: 1px solid rgba(124, 92, 252, 0.08);
  margin-bottom: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #7C5CFC 0%, #9B82FD 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(124, 92, 252, 0.3);
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px 16px 0;
  border-top: 1px solid rgba(124, 92, 252, 0.08);
}

/* ───── Main area ───── */
.main-area {
  flex: 1;
  margin-left: 240px;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

.main-content {
  width: 100%;
  max-width: 960px;
  padding: 44px 56px;
}

/* ───── Page transition ───── */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ───── Mobile ───── */
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
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
  }

  .drawer-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.2);
    z-index: 199;
    animation: fadeOverlay 0.2s ease;
  }

  @keyframes fadeOverlay {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #FFFFFF;
    border-bottom: 1px solid rgba(124, 92, 252, 0.08);
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .mobile-title {
    font-size: 18px;
    font-weight: 700;
    color: #1A1625;
  }

  .main-area {
    margin-left: 0;
  }

  .main-content {
    padding: 24px 20px;
  }
}
</style>
