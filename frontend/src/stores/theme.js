import { reactive } from 'vue'
import { themes, themeKeys } from '../themes.js'

const savedKey = localStorage.getItem('vestio-theme') || 'warm'
const validKey = themeKeys.includes(savedKey) ? savedKey : 'warm'
const savedCustomImage = localStorage.getItem('vestio-theme-custom-image') || ''

export const themeStore = reactive({
  currentKey: validKey,
  customImageUrl: savedCustomImage,

  get theme() {
    return themes[this.currentKey]
  },

  setTheme(key) {
    if (!themes[key]) return
    this.currentKey = key
    localStorage.setItem('vestio-theme', key)
    this._apply()
  },

  /** 仅预览主题，不保存到 localStorage */
  previewOnly(key) {
    if (!themes[key]) return
    this.currentKey = key
    this._apply()
  },

  setCustomImage(imageUrl) {
    this.customImageUrl = imageUrl
    if (imageUrl) {
      localStorage.setItem('vestio-theme-custom-image', imageUrl)
    } else {
      localStorage.removeItem('vestio-theme-custom-image')
    }
    if (this.currentKey === 'custom') {
      this._apply()
    }
  },

  /** 把主题变量写到 :root CSS 变量，供全局使用 */
  _apply() {
    const t = this.theme
    const root = document.documentElement.style
    root.setProperty('--theme-bg', t.bg)
    root.setProperty('--theme-surface-bg', t.surfaceBg)
    root.setProperty('--theme-glass-bg', t.glassBg)
    root.setProperty('--theme-glass-border', t.glassBorder)
    root.setProperty('--theme-nav-glass-bg', t.navGlassBg)
    root.setProperty('--theme-text', t.text)
    root.setProperty('--theme-text-secondary', t.textSecondary)
    root.setProperty('--theme-primary', t.primary)
    root.setProperty('--theme-primary-hover', t.primaryHover)
    root.setProperty('--theme-primary-pressed', t.primaryPressed)
    root.setProperty('--theme-accent', t.accent)
    root.setProperty('--theme-dark-glass-bg', t.darkGlassBg)
    root.setProperty('--theme-dark-glass-hover', t.darkGlassHover)
    root.setProperty('--theme-input-bg', t.inputBg)
    root.setProperty('--theme-input-focus-bg', t.inputFocusBg)
    root.setProperty('--theme-input-border', t.inputBorder)
    root.setProperty('--theme-placeholder', t.placeholder)
    root.setProperty('--theme-orb-opacity', t.orbOpacity)
    root.setProperty('--theme-card-shadow', t.cardShadow)
    
    // 自定义图片背景
    if (t.isCustom && this.customImageUrl) {
      root.setProperty('--theme-custom-bg', `url(${this.customImageUrl})`)
    } else {
      root.removeProperty('--theme-custom-bg')
    }
    
    // 4 个光斑
    t.orbs.forEach((c, i) => root.setProperty(`--theme-orb-${i + 1}`, c))
  },

  // 提供给导航栏等需要知道当前颜色的组件
  get keys() {
    return themeKeys
  },
  allThemes() {
    return themes
  },
})

// 首次加载立即应用
themeStore._apply()
