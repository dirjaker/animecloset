<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <div class="app-root">
            <!-- Floating orbs background -->
            <div v-show="!isLoginPage" class="app-bg">
              <div class="app-orb app-orb-1"></div>
              <div class="app-orb app-orb-2"></div>
              <div class="app-orb app-orb-3"></div>
              <div class="app-orb app-orb-4"></div>
            </div>

            <!-- Nav -->
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
                  <!-- 主题选择按钮 -->
                  <n-popover trigger="click" placement="bottom-end" :show="showThemePicker" @update:show="showThemePicker = $event">
                    <template #trigger>
                      <a class="theme-btn" @click="showThemePicker = true">
                        <n-icon :component="ColorPaletteOutline" :size="18" />
                      </a>
                    </template>
                    <div class="theme-picker-popup">
                      <div class="theme-picker-title">主题配色</div>
                      <div class="theme-picker-grid">
                        <div
                          v-for="key in themeKeys"
                          :key="key"
                          :class="['theme-option', { active: selectedTheme === key }]"
                          @click="previewTheme(key)"
                        >
                          <div class="theme-preview" :style="{ background: allThemes[key].bg }">
                            <div class="theme-orb" v-for="(orb, i) in allThemes[key].orbs.slice(0, 2)" :key="i" :style="{ background: orb }"></div>
                          </div>
                          <span class="theme-emoji">{{ allThemes[key].emoji }}</span>
                          <span class="theme-name">{{ allThemes[key].name }}</span>
                          <div v-if="selectedTheme === key" class="theme-check">✓</div>
                        </div>
                      </div>
                      <div class="theme-picker-actions">
                        <n-button size="small" @click="cancelTheme">取消</n-button>
                        <n-button size="small" type="primary" @click="applyTheme">确定</n-button>
                      </div>
                    </div>
                  </n-popover>

                  <a class="logout-link" @click="logout">退出</a>
                </div>
              </div>
            </nav>

            <!-- Main -->
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

            <!-- Login page overlays everything -->
            <router-view v-if="isLoginPage" />
          </div>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { h, computed, watch, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { authStore } from './stores/auth.js'
import { themeStore } from './stores/theme.js'
import {
  ShirtOutline,
  CalendarOutline,
  SparklesOutline,
  PersonOutline,
  ColorWandOutline,
  BriefcaseOutline,
  StatsChartOutline,
  ColorPaletteOutline,
} from '@vicons/ionicons5'
import { themes as allThemes, themeKeys } from './themes.js'

const router = useRouter()
const route = useRoute()

const currentRoute = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')

// 主题选择器状态
const showThemePicker = ref(false)
const selectedTheme = ref(themeStore.currentKey)
const originalTheme = ref(themeStore.currentKey)

function previewTheme(key) {
  selectedTheme.value = key
  themeStore.setTheme(key)
}

function cancelTheme() {
  selectedTheme.value = originalTheme.value
  themeStore.setTheme(originalTheme.value)
  showThemePicker.value = false
}

function applyTheme() {
  originalTheme.value = selectedTheme.value
  showThemePicker.value = false
}

// Naive UI 主题跟随当前主题色
const themeOverrides = computed(() => ({
  common: {
    primaryColor: themeStore.theme.primary,
    primaryColorHover: themeStore.theme.primaryHover,
    primaryColorPressed: themeStore.theme.primaryPressed,
    primaryColorSuppl: themeStore.theme.accent,
    borderRadius: '8px',
    borderRadiusSmall: '6px',
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
  Button: { borderRadiusMedium: '8px', borderRadiusSmall: '6px' },
  Card: { borderRadius: '8px' },
  Input: { borderRadius: '8px' },
  Tag: { borderRadius: '6px' },
}))

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

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--theme-bg, #F5F0E8);
  color: var(--theme-text, #2E2A23);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.5s ease, color 0.3s ease;
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
  opacity: var(--theme-orb-opacity, 0.35);
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
  transition: background 0.8s ease, opacity 0.5s ease;
}

.app-orb-1 {
  width: 500px;
  height: 500px;
  background: var(--theme-orb-1, #D4A0A0);
  top: -8%;
  left: -5%;
  animation: orbFloat1 20s infinite alternate;
}

.app-orb-2 {
  width: 400px;
  height: 400px;
  background: var(--theme-orb-2, #D4C5A0);
  top: -3%;
  right: -8%;
  animation: orbFloat2 24s infinite alternate;
}

.app-orb-3 {
  width: 450px;
  height: 450px;
  background: var(--theme-orb-3, #D9B896);
  bottom: -8%;
  right: 5%;
  animation: orbFloat3 22s infinite alternate;
}

.app-orb-4 {
  width: 350px;
  height: 350px;
  background: var(--theme-orb-4, #C5B8D4);
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
  background: var(--theme-nav-glass-bg, rgba(240, 235, 227, 0.65));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border-bottom: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.4));
  z-index: 200;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
  transition: background 0.4s ease, border-color 0.4s ease;
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
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  backdrop-filter: blur(12px);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: background 0.4s ease;
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  letter-spacing: 2px;
  transition: color 0.3s ease;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  padding: 16px 0;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.nav-link:hover {
  color: var(--theme-text, #2E2A23);
}

.nav-link.active {
  color: var(--theme-primary-pressed, #5A5048);
  border-bottom-color: var(--theme-primary-pressed, #5A5048);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: var(--theme-text-secondary, #8C8478);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
  color: var(--theme-text, #2E2A23);
}

.logout-link {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  cursor: pointer;
  transition: color 0.2s ease;
  text-decoration: none;
}

.logout-link:hover {
  color: var(--theme-text, #2E2A23);
}

/* ── Theme Picker Popup ── */
.theme-picker-popup {
  width: 280px;
  padding: 4px;
}

.theme-picker-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 12px;
  font-family: 'Noto Serif SC', serif;
}

.theme-picker-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.theme-option {
  position: relative;
  padding: 8px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s ease;
}

.theme-option:hover {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
}

.theme-option.active {
  border-color: var(--theme-primary, #A0815A);
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
}

.theme-preview {
  width: 100%;
  height: 40px;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
  margin-bottom: 4px;
}

.theme-orb {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  filter: blur(8px);
  opacity: 0.6;
}

.theme-orb:first-child {
  top: -5px;
  left: -5px;
}

.theme-orb:last-child {
  bottom: -5px;
  right: -5px;
}

.theme-emoji {
  font-size: 12px;
}

.theme-name {
  display: block;
  font-size: 11px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 2px;
}

.theme-check {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--theme-primary, #A0815A);
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-picker-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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
    background: var(--theme-nav-glass-bg, rgba(240, 235, 227, 0.65));
    backdrop-filter: blur(40px) saturate(160%);
    -webkit-backdrop-filter: blur(40px) saturate(160%);
    border-top: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.4));
    z-index: 200;
    align-items: center;
    justify-content: space-around;
    transition: background 0.4s ease;
  }

  .mobile-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    color: var(--theme-text-secondary, #8C8478);
    text-decoration: none;
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .mobile-tab.active {
    color: var(--theme-primary-pressed, #5A5048);
  }
}
</style>
