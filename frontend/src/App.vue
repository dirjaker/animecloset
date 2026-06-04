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
                        <n-icon :component="ShirtOutline" :size="20" color="#fff" />
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
    primaryColor: '#D4884A',
    primaryColorHover: '#E8A060',
    primaryColorPressed: '#B8743E',
    primaryColorSuppl: '#F0B878',
    borderRadius: '10px',
    borderRadiusSmall: '8px',
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  },
  Button: {
    borderRadiusMedium: '12px',
    borderRadiusSmall: '10px',
  },
  Card: {
    borderRadius: '16px',
  },
  Input: {
    borderRadius: '10px',
  },
  Tag: {
    borderRadius: '8px',
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: #F8F6F3;
  color: #1F2937;
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
  border-right: 1px solid #F0EFEC;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease;
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
  color: #1F2937;
  letter-spacing: -0.5px;
  border-bottom: 1px solid #F0EFEC;
  margin-bottom: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #D4884A 0%, #E8A060 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(212, 136, 74, 0.25);
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px 16px 0;
  border-top: 1px solid #F0EFEC;
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
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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
    border-bottom: 1px solid #F0EFEC;
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .mobile-title {
    font-size: 18px;
    font-weight: 700;
    color: #1F2937;
  }

  .main-area {
    margin-left: 0;
  }

  .main-content {
    padding: 24px 20px;
  }
}
</style>
