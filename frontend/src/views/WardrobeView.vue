<template>
  <div class="wardrobe-page">
    <div class="page-header">
      <div>
        <h2>衣橱</h2>
        <div class="page-line"></div>
      </div>
      <n-button type="primary" @click="triggerUpload" :loading="uploading">
        <template #icon><n-icon :component="AddOutline" /></template>
        上传衣物
      </n-button>
      <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleUpload" />
    </div>

    <div v-if="uploading" class="upload-bar">
      <n-spin :size="16" />
      <span>{{ uploadStatus }}</span>
    </div>

    <!-- Wardrobe Selector -->
    <div class="wardrobe-tabs">
      <button
        :class="['wtab', { active: activeWardrobe === '' }]"
        @click="activeWardrobe = ''; loadGarments()"
      >
        全部
      </button>
      <button
        v-for="w in wardrobes"
        :key="w.id"
        :class="['wtab', { active: activeWardrobe === w.id }]"
        @click="activeWardrobe = w.id; loadGarments()"
        @contextmenu.prevent="openWardrobeMenu(w)"
      >
        {{ w.icon || '📁' }} {{ w.name }}
      </button>
      <div v-if="showNewWardrobe" class="wardrobe-inline-input">
        <n-input
          v-model:value="newWardrobeName"
          size="small"
          placeholder="衣橱名称"
          @keyup.enter="createWardrobe"
          @keyup.esc="showNewWardrobe = false"
          style="width: 120px"
        />
        <n-button size="tiny" @click="createWardrobe" :loading="wardrobeCreating">确定</n-button>
      </div>
      <button v-else class="wtab wtab-add" @click="showNewWardrobe = true">
        <n-icon :component="AddOutline" :size="14" />
      </button>
    </div>

    <!-- Category Tabs + Favorite Toggle -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.value"
        :class="['tab', { active: activeCategory === cat.value }]"
        @click="activeCategory = cat.value; loadGarments()"
      >
        {{ cat.label }}
      </button>
      <button
        :class="['tab', 'fav-toggle', { active: onlyFavorites }]"
        @click="onlyFavorites = !onlyFavorites; loadGarments()"
        title="只看收藏"
      >
        <n-icon :component="onlyFavorites ? Star : StarOutline" :size="16" />
      </button>
    </div>

    <div class="sort-bar">
      <span class="sort-label">排序</span>
      <n-radio-group v-model:value="sortBy" size="small" @update:value="applySort">
        <n-radio-button value="default">默认</n-radio-button>
        <n-radio-button value="wear_count">穿着次数</n-radio-button>
      </n-radio-group>
    </div>

    <div v-if="loading" class="loading-area">
      <n-spin size="large" />
    </div>

    <div v-else-if="garments.length" class="garment-grid">
      <div
        v-for="(g, i) in garments"
        :key="g.id"
        :class="['garment-card', getCardSize(i)]"
      >
        <div class="card-img-wrap">
          <img :src="getImgUrl(g)" :alt="g.category" class="card-img" />
          <div v-if="g.wear_count" class="wear-count-badge">{{ g.wear_count }}次</div>
          <div v-if="isColdPalace(g)" class="cold-badge">冷宫</div>
          <!-- Favorite heart -->
          <button class="btn-fav" @click.stop="toggleFavorite(g)">
            <n-icon :component="g.is_favorite ? Heart : HeartOutline" :size="18" :color="g.is_favorite ? '#C8A09B' : '#8C8478'" />
          </button>
          <div class="card-overlay">
            <button class="btn-delete" @click.stop="deleteGarment(g.id)">
              <n-icon :component="CloseOutline" :size="18" />
            </button>
          </div>
        </div>
        <div class="card-info">
          <span class="card-name">{{ g.category }}</span>
          <div v-if="g.tags" class="card-tags">
            <span v-for="t in parseTags(g.tags)" :key="t" class="card-tag-chip">{{ t }}</span>
          </div>
          <!-- Lifecycle info on hover -->
          <div class="card-lifecycle">
            <span v-if="g.purchase_date" class="lifecycle-item">购入 {{ g.purchase_date }}</span>
            <span v-if="g.purchase_price && g.wear_count" class="lifecycle-item">
              单次 ¥{{ (g.purchase_price / g.wear_count).toFixed(1) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!garments.length && !loading" class="empty-state">
      <p class="empty-title">衣橱空空如也</p>
      <p class="empty-desc">点击右上角上传你的第一件衣服</p>
    </div>

    <div v-if="hasMore" style="text-align: center; margin-top: 24px">
      <n-button quaternary @click="loadMore" size="large">加载更多</n-button>
    </div>

    <!-- Wardrobe context menu -->
    <n-modal v-model:show="showWardrobeMenu" preset="card" :title="`编辑「${editingWardrobe?.name}」`" style="max-width: 340px">
      <n-input v-model:value="editWardrobeName" placeholder="新名称" />
      <template #action>
        <n-button type="error" @click="deleteWardrobe" :loading="wardrobeDeleting">删除</n-button>
        <n-button type="primary" @click="updateWardrobe" :loading="wardrobeUpdating">保存</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline, CloseOutline, HeartOutline, Heart, StarOutline, Star } from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const categories = [
  { label: '全部', value: '' },
  { label: '上衣', value: '上衣' },
  { label: '下装', value: '下装' },
  { label: '外套', value: '外套' },
  { label: '鞋', value: '鞋' },
  { label: '配饰', value: '配饰' },
]

const COLD_PALACE_DAYS = 30
const isColdPalace = (g) => {
  if (!g.last_wear_date) return true
  return (Date.now() - new Date(g.last_wear_date).getTime()) / 86400000 > COLD_PALACE_DAYS
}

const getImgUrl = (g) => {
  const url = g.image_url || g.thumbnail_url || g.processed_url
  if (url && url.startsWith('/')) return `${API_BASE}${url}`
  return url || ''
}

const parseTags = (tags) => {
  if (Array.isArray(tags)) return tags
  if (typeof tags === 'string') {
    try { return JSON.parse(tags) } catch { return [] }
  }
  if (tags?.color) return [tags.color, tags.material, ...(tags.style || [])].filter(Boolean)
  return []
}

function getCardSize(index) {
  const row = Math.floor(index / 3)
  const col = index % 3
  if (row % 2 === 0) {
    return col === 0 ? 'card-large' : 'card-medium'
  } else {
    return col === 2 ? 'card-large' : 'card-medium'
  }
}

const activeCategory = ref('')
const activeWardrobe = ref('')
const onlyFavorites = ref(false)
const garments = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const fileInput = ref(null)
const uploading = ref(false)
const uploadStatus = ref('')
const sortBy = ref('default')

// Wardrobes
const wardrobes = ref([])
const showNewWardrobe = ref(false)
const newWardrobeName = ref('')
const wardrobeCreating = ref(false)
const showWardrobeMenu = ref(false)
const editingWardrobe = ref(null)
const editWardrobeName = ref('')
const wardrobeUpdating = ref(false)
const wardrobeDeleting = ref(false)

async function loadWardrobes() {
  try {
    const { data } = await api.get('/wardrobes')
    wardrobes.value = data.items || data.wardrobes || data || []
  } catch {
    wardrobes.value = []
  }
}

async function createWardrobe() {
  if (!newWardrobeName.value.trim()) return
  wardrobeCreating.value = true
  try {
    await api.post('/wardrobes', { name: newWardrobeName.value.trim() })
    message.success('衣橱已创建')
    newWardrobeName.value = ''
    showNewWardrobe.value = false
    await loadWardrobes()
  } catch {
    message.error('创建失败')
  } finally {
    wardrobeCreating.value = false
  }
}

function openWardrobeMenu(w) {
  editingWardrobe.value = w
  editWardrobeName.value = w.name
  showWardrobeMenu.value = true
}

async function updateWardrobe() {
  if (!editWardrobeName.value.trim()) return
  wardrobeUpdating.value = true
  try {
    await api.put(`/wardrobes/${editingWardrobe.value.id}`, { name: editWardrobeName.value.trim() })
    message.success('已更新')
    showWardrobeMenu.value = false
    await loadWardrobes()
  } catch {
    message.error('更新失败')
  } finally {
    wardrobeUpdating.value = false
  }
}

async function deleteWardrobe() {
  wardrobeDeleting.value = true
  try {
    await api.delete(`/wardrobes/${editingWardrobe.value.id}`)
    message.success('已删除')
    showWardrobeMenu.value = false
    if (activeWardrobe.value === editingWardrobe.value.id) activeWardrobe.value = ''
    await loadWardrobes()
    await loadGarments()
  } catch {
    message.error('删除失败')
  } finally {
    wardrobeDeleting.value = false
  }
}

async function toggleFavorite(g) {
  try {
    const { data } = await api.put(`/garments/${g.id}/favorite`)
    g.is_favorite = data.is_favorite ?? !g.is_favorite
    message.success(g.is_favorite ? '已收藏' : '已取消收藏')
  } catch {
    message.error('操作失败')
  }
}

async function loadGarments(append = false) {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (activeCategory.value) params.category = activeCategory.value
    if (activeWardrobe.value) params.wardrobe_id = activeWardrobe.value
    if (onlyFavorites.value) params.is_favorite = true
    const { data } = await api.get('/garments', { params })
    const items = data.items || data.garments || data || []
    garments.value = append ? [...garments.value, ...items] : items
    applySort()
    hasMore.value = data.has_more || (items.length === 20)
  } catch {
    garments.value = []
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value++
  loadGarments(true)
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  uploading.value = true
  uploadStatus.value = '上传并识别中...'
  try {
    const { data } = await api.post('/garments/upload', fd)
    if (data.task_id) {
      await pollStatus(data.task_id)
    }
    page.value = 1
    await loadGarments()
    message.success('衣物上传成功')
  } catch {
    message.error('上传失败')
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

function pollStatus(taskId) {
  return new Promise((resolve, reject) => {
    const iv = setInterval(async () => {
      try {
        const { data } = await api.get(`/garments/status/${taskId}`)
        if (['success', 'completed', 'done'].includes(data.status)) {
          clearInterval(iv)
          resolve(data)
        } else if (['failed', 'error'].includes(data.status)) {
          clearInterval(iv)
          reject(new Error('识别失败'))
        }
      } catch {
        clearInterval(iv)
        reject(new Error('查询失败'))
      }
    }, 2000)
  })
}

async function deleteGarment(id) {
  try {
    await api.delete(`/garments/${id}`)
    garments.value = garments.value.filter(g => g.id !== id)
    message.success('已删除')
  } catch {
    message.error('删除失败')
  }
}

function applySort() {
  if (sortBy.value === 'wear_count') {
    garments.value = [...garments.value].sort((a, b) => (b.wear_count || 0) - (a.wear_count || 0))
  } else {
    garments.value = [...garments.value]
  }
}

onMounted(async () => {
  await loadWardrobes()
  await loadGarments()
})
</script>

<style scoped>
.wardrobe-page {
  animation: pageEnter 0.3s ease;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-header h2 {
  font-family: 'Noto Serif SC', serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  letter-spacing: 1px;
}

.page-line {
  width: 100%;
  height: 1px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.4));
  margin-top: 8px;
}

.upload-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
  backdrop-filter: blur(20px);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.4));
  border-radius: 10px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--theme-primary-pressed, #5A5048);
  font-weight: 500;
}

/* Wardrobe tabs */
.wardrobe-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.25);
  align-items: center;
}

.wtab {
  padding: 8px 16px;
  border: none;
  background: none;
  font-size: 13px;
  font-weight: 500;
  color: var(--theme-text-secondary, #8C8478);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  outline: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.wtab:hover {
  color: var(--theme-text, #2E2A23);
}

.wtab.active {
  color: var(--theme-primary, #70645A);
  border-bottom-color: var(--theme-primary, #70645A);
}

.wtab-add {
  padding: 6px 10px;
  border-bottom: none;
  margin-bottom: 0;
  border-radius: 4px;
}

.wtab-add:hover {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
}

.wardrobe-inline-input {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
}

/* Category tabs */
.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.tab {
  padding: 8px 16px;
  border: none;
  background: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text-secondary, #8C8478);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  outline: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab:hover {
  color: var(--theme-text, #2E2A23);
}

.tab.active {
  color: var(--theme-primary, #70645A);
  border-bottom-color: var(--theme-primary, #70645A);
}

.fav-toggle {
  padding: 8px 10px;
  display: flex;
  align-items: center;
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.sort-label {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  font-weight: 500;
}

.loading-area {
  text-align: center;
  padding: 80px 0;
}

/* Alternating grid */
.garment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  grid-auto-flow: dense;
}

.garment-card.card-large {
  grid-column: span 2;
}

.garment-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  transition: all 0.3s ease;
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
}

.garment-card:hover {
  border-color: var(--theme-glass-border, rgba(255, 255, 255, 0.6));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.6) inset;
  transform: translateY(-2px);
}

.card-img-wrap {
  position: relative;
  aspect-ratio: 1;
  background: var(--theme-surface-bg, rgba(240, 235, 227, 0.5));
  overflow: hidden;
}

.card-large .card-img-wrap {
  aspect-ratio: 16/10;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.garment-card:hover .card-img {
  transform: scale(1.03);
}

.wear-count-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(46, 42, 37, 0.6);
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.cold-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(255, 253, 248, 0.9);
  color: var(--theme-accent, #C8A09B);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.btn-fav {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 253, 248, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
  z-index: 2;
}

.btn-fav:hover {
  background: rgba(255, 253, 248, 1);
  transform: scale(1.1);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(46, 42, 37, 0.1);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 8px;
  padding-top: 44px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.garment-card:hover .card-overlay {
  opacity: 1;
}

.btn-delete {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: rgba(255, 253, 248, 0.9);
  color: var(--theme-text-secondary, #8C8478);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.btn-delete:hover {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.5));
  color: #FFFFFF;
}

.card-info {
  padding: 12px;
}

.card-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text, #2E2A23);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.card-tag-chip {
  font-size: 11px;
  color: var(--theme-text-secondary, #8C8478);
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
  backdrop-filter: blur(8px);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.card-lifecycle {
  display: none;
  gap: 8px;
  margin-top: 6px;
}

.garment-card:hover .card-lifecycle {
  display: flex;
}

.lifecycle-item {
  font-size: 11px;
  color: var(--theme-accent, #C8A09B);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 6px;
}

.empty-desc {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
}

@media (max-width: 768px) {
  .garment-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .garment-card.card-large {
    grid-column: span 1;
  }

  .card-large .card-img-wrap {
    aspect-ratio: 1;
  }
}
</style>
