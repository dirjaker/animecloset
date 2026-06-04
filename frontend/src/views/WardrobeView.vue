<template>
  <div class="wardrobe-page">
    <div class="header">
      <h2>👗 我的衣橱</h2>
      <button class="btn-upload" @click="triggerUpload">+ 上传</button>
      <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="handleUpload" />
    </div>

    <div class="tabs">
      <button
        v-for="cat in categories"
        :key="cat.value"
        :class="['tab', { active: activeCategory === cat.value }]"
        @click="activeCategory = cat.value; loadGarments()"
      >{{ cat.label }}</button>
    </div>

    <div class="sort-bar">
      <label class="sort-label">排序:</label>
      <button
        v-for="s in sortOptions"
        :key="s.value"
        :class="['sort-btn', { active: sortBy === s.value }]"
        @click="sortBy = s.value; applySort()"
      >{{ s.label }}</button>
    </div>

    <div v-if="uploading" class="upload-status">
      <div class="spinner"></div>
      <span>{{ uploadStatus }}</span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="grid">
      <div v-for="g in garments" :key="g.id" class="card">
        <div class="card-img-wrap">
            <img :src="g.image_url || g.thumbnail_url" :alt="g.category" class="card-img" />
            <span v-if="g.wear_count != null" class="wear-count-badge">{{ g.wear_count }}次</span>
            <span v-if="isColdPalace(g)" class="cold-palace-tag">冷宫</span>
            <button class="btn-delete" @click="deleteGarment(g.id)">×</button>
        </div>
        <div class="card-info">
          <span class="cat-badge">{{ categoryLabel(g.category) }}</span>
          <div class="tags" v-if="g.tags?.length">
            <span v-for="t in g.tags" :key="t" class="tag">{{ t }}</span>
          </div>
        </div>
      </div>

      <div v-if="!garments.length && !loading" class="empty">
        <p>衣橱空空如也~</p>
        <p class="hint">点击右上角上传你的第一件衣服吧！</p>
      </div>
    </div>

    <div v-if="hasMore" class="load-more">
      <button @click="loadMore" class="btn-more">加载更多</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

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
  const diff = (Date.now() - new Date(g.last_wear_date).getTime()) / 86400000
  return diff > COLD_PALACE_DAYS
}

const activeCategory = ref('')
const garments = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const fileInput = ref(null)
const uploading = ref(false)
const uploadStatus = ref('上传中...')
const sortBy = ref('default')
const allGarments = ref([])
const sortOptions = [
  { label: '默认', value: 'default' },
  { label: '穿着次数', value: 'wear_count' },
]

async function loadGarments(append = false) {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (activeCategory.value) params.category = activeCategory.value
    const { data } = await api.get('/garments', { params })
    const items = data.items || data.garments || data || []
    garments.value = append ? [...garments.value, ...items] : items
    allGarments.value = [...garments.value]
    applySort()
    hasMore.value = data.has_more || (items.length === 20)
  } catch { garments.value = [] }
  finally { loading.value = false }
}

function loadMore() { page.value++; loadGarments(true) }

function triggerUpload() { fileInput.value?.click() }

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  uploading.value = true
  uploadStatus.value = '上传中...'
  try {
    const { data } = await api.post('/garments/upload', fd)
    const taskId = data.task_id
    if (taskId) {
      uploadStatus.value = '识别中...'
      await pollStatus(taskId)
    }
    page.value = 1
    await loadGarments()
  } catch (e) {
    uploadStatus.value = '上传失败'
    setTimeout(() => { uploading.value = false }, 2000)
    return
  }
  uploading.value = false
  e.target.value = ''
}

function pollStatus(taskId) {
  return new Promise((resolve, reject) => {
    const iv = setInterval(async () => {
      try {
        const { data } = await api.get(`/garments/status/${taskId}`)
        if (data.status === 'success' || data.status === 'completed' || data.status === 'done') {
          clearInterval(iv); resolve(data)
        } else if (data.status === 'failed' || data.status === 'error') {
          clearInterval(iv); reject(new Error('识别失败'))
        }
      } catch { clearInterval(iv); reject(new Error('查询失败')) }
    }, 2000)
  })
}

async function deleteGarment(id) {
  if (!confirm('确定删除这件衣服吗？')) return
  try {
    await api.delete(`/garments/${id}`)
    garments.value = garments.value.filter(g => g.id !== id)
  } catch {}
}

onMounted(() => loadGarments())
function applySort() {
  if (sortBy.value === 'wear_count') {
    garments.value = [...garments.value].sort((a, b) => (b.wear_count || 0) - (a.wear_count || 0))
  } else {
    garments.value = [...garments.value]
  }
}

</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header h2 { font-size: 20px; color: #8B6914; }
.btn-upload {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border: none; padding: 8px 18px;
  border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer;
}

.tabs {
  display: flex; gap: 8px; margin-bottom: 16px;
  overflow-x: auto; padding-bottom: 4px;
}

.tab {
  padding: 6px 16px; border: 2px solid #D4A574;
  background: #FFF5EB; border-radius: 10px; font-size: 13px;
  cursor: pointer; white-space: nowrap; color: #4A3728; transition: all 0.2s;
}
.tab.active {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border-color: transparent;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

@media (min-width: 600px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

.card {
  background: #FFF5EB; border-radius: 12px; overflow: hidden;
  border: 1px solid #D4A574;
  box-shadow: 0 2px 12px rgba(139, 105, 20, 0.08);
  transition: transform 0.2s;
}
.card:hover { transform: translateY(-2px); }

.card-img-wrap { position: relative; aspect-ratio: 1; overflow: hidden; background: #FFF8F0; }
.card-img { width: 100%; height: 100%; object-fit: cover; }
.btn-delete {
  position: absolute; top: 6px; right: 6px;
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(0,0,0,0.5); color: white; border: none;
  font-size: 14px; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
}

.card-info { padding: 12px 16px; }
.cat-badge {
  display: inline-block; background: #F5E6D3; color: #8B6914;
  padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: 500;
}
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.tag {
  background: #F5E6D3; color: #8B7355;
  padding: 2px 8px; border-radius: 8px; font-size: 11px;
}

.upload-status {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; background: #FFF8F0; border: 1px solid #D4A574;
  border-radius: 12px;
  margin-bottom: 16px; font-size: 14px; color: #8B6914;
}

.spinner {
  width: 20px; height: 20px; border: 3px solid #D4A574;
  border-top-color: #C17A3A; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.loading { text-align: center; padding: 40px; color: #C17A3A; }
.empty { text-align: center; padding: 60px 20px; color: #8B7355; }
.empty .hint { font-size: 13px; margin-top: 8px; }

.load-more { text-align: center; margin-top: 16px; }
.btn-more {
  padding: 8px 24px; border: 2px solid #D4A574; background: #FFF5EB;
  border-radius: 10px; color: #8B6914; cursor: pointer; font-size: 14px;
}

.sort-bar {
  display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
}
.sort-label { font-size: 13px; color: #4A3728; font-weight: 600; }
.sort-btn {
  padding: 4px 12px; border: 2px solid #D4A574; background: #FFF5EB;
  border-radius: 10px; font-size: 12px; cursor: pointer;
  color: #4A3728; transition: all 0.2s;
}
.sort-btn.active {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border-color: transparent;
}

.wear-count-badge {
  position: absolute; bottom: 6px; left: 6px;
  background: rgba(139, 105, 20, 0.85); color: white;
  padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;
}

.cold-palace-tag {
  position: absolute; top: 6px; left: 6px;
  background: rgba(91, 124, 80, 0.85); color: white;
  padding: 2px 8px; border-radius: 8px; font-size: 10px; font-weight: 600;
}
</style>
