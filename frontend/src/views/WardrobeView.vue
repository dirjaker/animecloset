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

    <!-- 固定4列网格 -->
    <div v-else-if="garments.length" class="garment-grid">
      <div
        v-for="g in garments"
        :key="g.id"
        class="garment-card"
        @click="openDetail(g)"
      >
        <div class="card-img-wrap">
          <img :src="getImgUrl(g)" :alt="g.category" class="card-img" />
          <div v-if="g.wear_count" class="wear-count-badge">{{ g.wear_count }}次</div>
          <div v-if="isColdPalace(g)" class="cold-badge">冷宫</div>
          <!-- Favorite heart -->
          <button class="btn-fav" @click.stop="toggleFavorite(g)">
            <n-icon :component="g.is_favorite ? Heart : HeartOutline" :size="18" :color="g.is_favorite ? '#C8A09B' : '#8C8478'" />
          </button>
        </div>
        <div class="card-info">
          <span class="card-name">{{ g.category }}</span>
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

    <!-- 衣物详情弹窗 -->
    <n-modal v-model:show="showDetail" preset="card" style="max-width: 700px; border-radius: 12px" :bordered="false">
      <div class="detail-layout" v-if="detailGarment">
        <!-- 左侧图片 -->
        <div class="detail-left">
          <img :src="getImgUrl(detailGarment)" :alt="detailGarment.category" class="detail-img" />
        </div>
        <!-- 右侧信息 -->
        <div class="detail-right">
          <h3 class="detail-title">衣物详情</h3>
          
          <!-- 分类 -->
          <div class="detail-field">
            <label>分类</label>
            <n-select
              v-model:value="editForm.category"
              :options="categoryOptions"
              size="small"
            />
          </div>

          <!-- 颜色 -->
          <div class="detail-field">
            <label>颜色</label>
            <n-input v-model:value="editForm.tags.color" size="small" placeholder="如：黑色、白色" />
          </div>

          <!-- 材质 -->
          <div class="detail-field">
            <label>材质</label>
            <n-input v-model:value="editForm.tags.material" size="small" placeholder="如：棉、涤纶" />
          </div>

          <!-- 风格 -->
          <div class="detail-field">
            <label>风格</label>
            <n-select
              v-model:value="editForm.tags.style"
              :options="styleOptions"
              multiple
              size="small"
            />
          </div>

          <!-- 季节 -->
          <div class="detail-field">
            <label>季节</label>
            <n-select
              v-model:value="editForm.tags.season"
              :options="seasonOptions"
              multiple
              size="small"
            />
          </div>

          <!-- 所属衣橱 -->
          <div class="detail-field">
            <label>所属衣橱</label>
            <n-select
              v-model:value="editForm.wardrobe_id"
              :options="wardrobeOptions"
              size="small"
              clearable
            />
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <n-button type="primary" @click="saveDetail" :loading="saving">保存修改</n-button>
            <n-button @click="showDetail = false">取消</n-button>
          </div>
        </div>
      </div>
    </n-modal>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline, HeartOutline, Heart, StarOutline, Star } from '@vicons/ionicons5'
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

// 冷宫标签：60天未穿
const COLD_PALACE_DAYS = 60
const isColdPalace = (g) => {
  // 有穿着记录且超过60天
  if (g.last_wear_date) {
    return (Date.now() - new Date(g.last_wear_date).getTime()) / 86400000 > COLD_PALACE_DAYS
  }
  // 无穿着记录，检查上传时间（created_at）
  if (g.created_at) {
    return (Date.now() - new Date(g.created_at).getTime()) / 86400000 > COLD_PALACE_DAYS
  }
  return false
}

const getImgUrl = (g) => {
  const url = g.image_url || g.thumbnail_url || g.processed_url
  if (url && url.startsWith('/')) return `${API_BASE}${url}`
  return url || ''
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

// Detail modal
const showDetail = ref(false)
const detailGarment = ref(null)
const saving = ref(false)
const editForm = reactive({
  category: '',
  wardrobe_id: null,
  tags: {
    color: '',
    material: '',
    style: [],
    season: [],
    occasion: []
  }
})

// Options for selects
const categoryOptions = [
  { label: '上衣', value: '上衣' },
  { label: '下装', value: '下装' },
  { label: '外套', value: '外套' },
  { label: '鞋', value: '鞋' },
  { label: '配饰', value: '配饰' },
]

const styleOptions = [
  { label: '休闲', value: '休闲' },
  { label: '商务', value: '商务' },
  { label: '运动', value: '运动' },
  { label: '正式', value: '正式' },
  { label: '街头', value: '街头' },
  { label: '复古', value: '复古' },
  { label: '简约', value: '简约' },
  { label: '甜美', value: '甜美' },
]

const seasonOptions = [
  { label: '春', value: '春' },
  { label: '夏', value: '夏' },
  { label: '秋', value: '秋' },
  { label: '冬', value: '冬' },
]

const wardrobeOptions = computed(() => {
  return wardrobes.value.map(w => ({ label: w.name, value: w.id }))
})

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
    const index = garments.value.findIndex(item => item.id === g.id)
    if (index !== -1) {
      garments.value[index] = { ...garments.value[index], is_favorite: data.is_favorite }
    }
    message.success(data.is_favorite ? '已收藏' : '已取消收藏')
  } catch {
    message.error('操作失败')
  }
}

async function loadGarments(append = false) {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 100 }
    if (activeCategory.value) params.category = activeCategory.value
    if (activeWardrobe.value) params.wardrobe_id = activeWardrobe.value
    if (onlyFavorites.value) params.is_favorite = true
    const { data } = await api.get('/garments', { params })
    const items = data.items || data.garments || data || []
    garments.value = append ? [...garments.value, ...items] : items
    applySort()
    hasMore.value = data.has_more || (items.length === 100)
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

function applySort() {
  if (sortBy.value === 'wear_count') {
    garments.value = [...garments.value].sort((a, b) => (b.wear_count || 0) - (a.wear_count || 0))
  } else {
    garments.value = [...garments.value]
  }
}

// 打开详情弹窗
function openDetail(g) {
  detailGarment.value = g
  // 初始化编辑表单
  editForm.category = g.category
  editForm.wardrobe_id = g.wardrobe_id || null
  editForm.tags = {
    color: g.tags?.color || '',
    material: g.tags?.material || '',
    style: g.tags?.style || [],
    season: g.tags?.season || [],
    occasion: g.tags?.occasion || []
  }
  showDetail.value = true
}

// 保存详情修改
async function saveDetail() {
  saving.value = true
  try {
    await api.put(`/garments/${detailGarment.value.id}`, {
      category: editForm.category,
      wardrobe_id: editForm.wardrobe_id,
      tags: editForm.tags
    })
    message.success('保存成功')
    showDetail.value = false
    // 刷新列表
    await loadGarments()
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
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

/* 固定4列网格 */
.garment-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
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
  cursor: pointer;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-img {
  width: 80%;
  height: 80%;
  object-fit: contain; /* 抠图居中显示 */
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.garment-card:hover .card-img {
  transform: scale(1.05);
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

.card-info {
  padding: 12px;
  text-align: center;
}

.card-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text, #2E2A23);
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

/* 详情弹窗布局 */
.detail-layout {
  display: flex;
  gap: 24px;
}

.detail-left {
  flex: 0 0 280px;
  background: var(--theme-surface-bg, rgba(240, 235, 227, 0.5));
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.detail-img {
  width: 80%;
  height: 80%;
  object-fit: contain;
}

.detail-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 8px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--theme-text-secondary, #8C8478);
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .garment-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .detail-layout {
    flex-direction: column;
  }

  .detail-left {
    flex: none;
    height: 200px;
  }
}
</style>
