<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <div class="app-root">
            <!-- Floating orbs background (shared across all internal pages) -->
            <div v-show="!isLoginPage" class="app-bg">
              <div class="app-orb app-orb-1"></div>
              <div class="app-orb app-orb-2"></div>
              <div class="app-orb app-orb-3"></div>
              <div class="app-orb app-orb-4"></div>
            </div>

            <!-- Nav: always mounted, hidden on login -->
            <nav v-show="!isLoginPage" class="top-nav">
              <div class="nav-inner">
                <div class="nav-logo">
                  <div class="logo-seal">
                    <n-icon :component="ShirtOutline" :size="18" color="#FFFFFF" />
                  </div>
                  <span class="logo-text">Vestio</span>
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

            <!-- Main: always mounted, router-view is the single source of truth -->
            <main v-show="!isLoginPage" class="main-area">
              <div class="main-content">
                <router-view />
              </div>
            </main>

            <!-- Mobile bottom tab bar -->
            <nav v-show="!isLoginPage" class="mobile-tabs">
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

            <!-- Login page: rendered by router, overlays everything (position: fixed in LoginView) -->
            <router-view v-if="isLoginPage" />
          </div>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { authStore } from './stores/auth.js'
import {
  ShirtOutline,
  CalendarOutline,
  SparklesOutline,
  PersonOutline,
  ColorWandOutline,
  BriefcaseOutline,
  StatsChartOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const currentRoute = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')

const themeOverrides = {
  common: {
    primaryColor: '#70645A',
    primaryColorHover: '#8A7A6E',
    primaryColorPressed: '#5A5048',
    primaryColorSuppl: '#C8A09B',
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
  { label: '搭配', key: '/builder', icon: renderIcon(ColorWandOutline), iconComponent: ColorWandOutline },
  { label: '推荐', key: '/recommend', icon: renderIcon(SparklesOutline), iconComponent: SparklesOutline },
  { label: '日历', key: '/calendar', icon: renderIcon(CalendarOutline), iconComponent: CalendarOutline },
  { label: '打包', key: '/packing', icon: renderIcon(BriefcaseOutline), iconComponent: BriefcaseOutline },
  { label: '统计', key: '/stats', icon: renderIcon(StatsChartOutline), iconComponent: StatsChartOutline },
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
  --color-primary: #70645A;
  --color-primary-hover: #8A7A6E;
  --color-primary-pressed: #5A5048;
  --color-accent: #C8A09B;
  --color-bg: #F0EBE3;
  --color-surface: rgba(255, 255, 255, 0.35);
  --color-text: #2E2A23;
  --color-text-secondary: #8C8478;
  --color-border: rgba(255, 255, 255, 0.45);
  --glass-blur: blur(40px) saturate(160%);
  --glass-bg: rgba(255, 255, 255, 0.35);
  --glass-border: 1px solid rgba(255, 255, 255, 0.45);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.06), 0 1px 0 rgba(255, 255, 255, 0.6) inset;
  --dark-glass-bg: rgba(80, 70, 65, 0.4);
  --dark-glass-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--color-bg);
  color: #2E2A23;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-root {
  min-height: 100vh;
  position: relative;
}

/* ── Floating orbs background ── */
.app-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.app-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.35;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}

.app-orb-1 {
  width: 500px;
  height: 500px;
  background: #D4A0A0;
  top: -8%;
  left: -5%;
  animation: orbFloat1 20s infinite alternate;
}

.app-orb-2 {
  width: 400px;
  height: 400px;
  background: #D4C5A0;
  top: -3%;
  right: -8%;
  animation: orbFloat2 24s infinite alternate;
}

.app-orb-3 {
  width: 450px;
  height: 450px;
  background: #D9B896;
  bottom: -8%;
  right: 5%;
  animation: orbFloat3 22s infinite alternate;
}

.app-orb-4 {
  width: 350px;
  height: 350px;
  background: #C5B8D4;
  bottom: 5%;
  left: 10%;
  animation: orbFloat4 26s infinite alternate;
}

@keyframes orbFloat1 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(80px, 60px) scale(1.1); }
}

@keyframes orbFloat2 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-60px, 80px) scale(1.15); }
}

@keyframes orbFloat3 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-50px, -70px) scale(1.08); }
}

@keyframes orbFloat4 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(70px, -40px) scale(1.12); }
}

/* ── Top nav (glass) ── */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(240, 235, 227, 0.65);
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  z-index: 200;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
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
  background: rgba(80, 70, 65, 0.4);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  color: #5A5048;
  border-bottom-color: #5A5048;
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

/* ── Main area ── */
.main-area {
  position: relative;
  z-index: 1;
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

/* ── Mobile bottom tabs (glass) ── */
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
    background: rgba(240, 235, 227, 0.65);
    backdrop-filter: blur(40px) saturate(160%);
    -webkit-backdrop-filter: blur(40px) saturate(160%);
    border-top: 1px solid rgba(255, 255, 255, 0.4);
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
    text-decoration: none;
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .mobile-tab.active {
    color: #5A5048;
  }
}
</style>
