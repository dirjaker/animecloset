<template>
  <div class="wardrobe-page">
    <div class="page-header">
      <div>
        <h2>我的衣橱</h2>
        <p class="page-subtitle">管理你的所有衣物</p>
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

    <div class="category-pills">
      <button
        v-for="cat in categories"
        :key="cat.value"
        :class="['pill', { active: activeCategory === cat.value }]"
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
      <div v-for="g in garments" :key="g.id" class="garment-card">
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
          <n-tag size="small" :bordered="false" round style="background: rgba(124, 92, 252, 0.1); color: #7C5CFC; font-weight: 500;">
            {{ categoryLabel(g.category) }}
          </n-tag>
          <div v-if="g.tags" class="card-tags">
            <span v-for="t in parseTags(g.tags)" :key="t" class="card-tag-chip">{{ t }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!garments.length && !loading" class="empty-state">
      <div class="empty-icon-ring">
        <n-icon :component="ShirtOutline" :size="40" color="#D1D5DB" />
      </div>
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
import { AddOutline, CloseOutline, ShirtOutline } from '@vicons/ionicons5'
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
  animation: pageEnter 0.25s ease;
}

@keyframes pageEnter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1A1625;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 13px;
  color: #6B6580;
  margin-top: 4px;
}

.upload-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(124, 92, 252, 0.08);
  border-radius: 12px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #7C5CFC;
  font-weight: 500;
}

.category-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.pill {
  padding: 7px 18px;
  border-radius: 20px;
  border: 1px solid #E5E7EB;
  background: #FFFFFF;
  font-size: 13px;
  font-weight: 500;
  color: #6B6580;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  outline: none;
}

.pill:hover {
  border-color: #7C5CFC;
  color: #7C5CFC;
}

.pill.active {
  background: #7C5CFC;
  border-color: #7C5CFC;
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(124, 92, 252, 0.25);
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.sort-label {
  font-size: 13px;
  color: #6B6580;
  font-weight: 500;
}

.loading-area {
  text-align: center;
  padding: 80px 0;
}

.garment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.garment-card {
  background: #FFFFFF;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(124, 92, 252, 0.04);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(124, 92, 252, 0.08);
}

.garment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(124, 92, 252, 0.12), 0 4px 12px rgba(0, 0, 0, 0.04);
}

.card-img-wrap {
  position: relative;
  aspect-ratio: 1;
  background: #F5F3FF;
  overflow: hidden;
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
  background: rgba(0, 0, 0, 0.55);
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 8px;
  backdrop-filter: blur(4px);
}

.cold-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: #FF6B9D;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 8px;
  backdrop-filter: blur(4px);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
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
  border-radius: 10px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  color: #EF4444;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.btn-delete:hover {
  background: #EF4444;
  color: #FFFFFF;
}

.card-info {
  padding: 12px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.card-tag-chip {
  font-size: 11px;
  color: #6B6580;
  background: rgba(124, 92, 252, 0.06);
  padding: 2px 8px;
  border-radius: 6px;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(124, 92, 252, 0.08), rgba(255, 107, 157, 0.08));
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #1A1625;
  margin-bottom: 6px;
}

.empty-desc {
  font-size: 13px;
  color: #6B6580;
}

@media (max-width: 768px) {
  .garment-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
