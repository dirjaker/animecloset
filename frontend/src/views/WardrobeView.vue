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

    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.value"
        :class="['tab', { active: activeCategory === cat.value }]"
        @click="activeCategory = cat.value; loadGarments()"
      >
        {{ cat.label }}
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
          <div class="card-overlay">
            <button class="btn-delete" @click.stop="deleteGarment(g.id)">
              <n-icon :component="CloseOutline" :size="18" />
            </button>
          </div>
        </div>
        <div class="card-info">
          <span class="card-name">{{ categoryLabel(g.category) }}</span>
          <div v-if="g.tags" class="card-tags">
            <span v-for="t in parseTags(g.tags)" :key="t" class="card-tag-chip">{{ t }}</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline, CloseOutline } from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const categories = [
  { label: '全部', value: '' },
  { label: '上衣', value: 'top' },
  { label: '下装', value: 'bottom' },
  { label: '外套', value: 'outer' },
  { label: '鞋', value: 'shoes' },
  { label: '配饰', value: 'accessory' },
]
const categoryMap = { top: '上衣', bottom: '下装', outer: '外套', shoes: '鞋', accessory: '配饰' }
const categoryLabel = (c) => categoryMap[c] || c

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
  // Row 1: large, medium, medium
  // Row 2: medium, medium, large (alternating)
  const row = Math.floor(index / 3)
  const col = index % 3
  if (row % 2 === 0) {
    // even row: first is large
    return col === 0 ? 'card-large' : 'card-medium'
  } else {
    // odd row: last is large
    return col === 2 ? 'card-large' : 'card-medium'
  }
}

const activeCategory = ref('')
const garments = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const fileInput = ref(null)
const uploading = ref(false)
const uploadStatus = ref('')
const sortBy = ref('default')

async function loadGarments(append = false) {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (activeCategory.value) params.category = activeCategory.value
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

onMounted(() => loadGarments())
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
  color: #2E2A23;
  letter-spacing: 1px;
}

.page-line {
  width: 100%;
  height: 1px;
  background: #E0D8CC;
  margin-top: 8px;
}

.upload-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(160, 129, 90, 0.06);
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #A0815A;
  font-weight: 500;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-bottom: 16px;
  border-bottom: 1px solid #E0D8CC;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: none;
  font-size: 14px;
  font-weight: 500;
  color: #8C8478;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  outline: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab:hover {
  color: #2E2A23;
}

.tab.active {
  color: #A0815A;
  border-bottom-color: #A0815A;
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.sort-label {
  font-size: 13px;
  color: #8C8478;
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
  background: #FFFDF8;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E0D8CC;
  transition: all 0.3s ease;
}

.garment-card:hover {
  border-left: 2px solid #A0815A;
  box-shadow: 0 2px 12px rgba(46, 42, 37, 0.08);
}

.card-img-wrap {
  position: relative;
  aspect-ratio: 1;
  background: #F5F0E8;
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
  color: #C27C4E;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(46, 42, 37, 0.1);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 8px;
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
  color: #8C8478;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.btn-delete:hover {
  background: #A0815A;
  color: #FFFFFF;
}

.card-info {
  padding: 12px;
}

.card-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 500;
  color: #2E2A23;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.card-tag-chip {
  font-size: 11px;
  color: #8C8478;
  background: rgba(160, 129, 90, 0.06);
  padding: 2px 8px;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #8C8478;
  margin-bottom: 6px;
}

.empty-desc {
  font-size: 13px;
  color: #8C8478;
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
