<template>
  <div class="builder-page">
    <div class="page-header">
      <div>
        <h2>穿搭搭配</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <div class="builder-layout">
      <!-- Left: Garment Grid -->
      <div class="garment-panel glass-card">
        <div class="panel-header">
          <span class="panel-title">我的衣物</span>
        </div>
        <div class="filter-tabs">
          <button
            v-for="cat in categories"
            :key="cat.value"
            :class="['tab', { active: activeCategory === cat.value }]"
            @click="activeCategory = cat.value; loadGarments()"
          >
            {{ cat.label }}
          </button>
        </div>
        <div v-if="garmentLoading" class="loading-area">
          <n-spin size="medium" />
        </div>
        <div v-else-if="garments.length" class="garment-scroll">
          <div
            v-for="g in garments"
            :key="g.id"
            :class="['garment-thumb', { selected: isInOutfit(g.id) }]"
            @click="addToSlot(g)"
          >
            <img :src="getImgUrl(g)" :alt="g.category" />
            <span class="thumb-label">{{ g.category }}</span>
          </div>
        </div>
        <div v-else class="empty-inline">
          <n-empty description="暂无衣物" size="40" />
        </div>
      </div>

      <!-- Right: Outfit Preview -->
      <div class="preview-panel">
        <div class="preview-canvas glass-card">
          <div class="panel-header">
            <span class="panel-title">今日穿搭</span>
          </div>
          <div class="slots-grid">
            <div
              v-for="slot in outfitSlots"
              :key="slot.category"
              :class="['slot-box', { filled: slot.garment }]"
              @click="removeFromSlot(slot.category)"
            >
              <img
                v-if="slot.garment"
                :src="getImgUrl(slot.garment)"
                :alt="slot.label"
                class="slot-img"
              />
              <div v-else class="slot-empty">
                <n-icon :component="AddOutline" :size="24" />
                <span>{{ slot.label }}</span>
              </div>
              <div v-if="slot.garment" class="slot-remove-hint">
                <n-icon :component="CloseOutline" :size="14" />
              </div>
            </div>
          </div>
        </div>

        <n-button
          type="primary"
          block
          size="large"
          :loading="saving"
          :disabled="!hasAnyGarment"
          class="save-btn"
          @click="saveOutfit"
        >
          保存今日穿搭
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline, CloseOutline } from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

// 标准分类 — 与后端 categories.py 保持一致
const categories = [
  { label: '全部', value: '' },
  { label: '上衣', value: '上衣' },
  { label: '下装', value: '下装' },
  { label: '外套', value: '外套' },
  { label: '鞋', value: '鞋' },
  { label: '配饰', value: '配饰' },
]

const getImgUrl = (g) => {
  const url = g.image_url || g.thumbnail_url || g.processed_url
  if (url && url.startsWith('/')) return `${API_BASE}${url}`
  return url || ''
}

const activeCategory = ref('')
const garments = ref([])
const garmentLoading = ref(false)
const saving = ref(false)

// 搭配槽位 — 使用标准分类名
const outfitSlots = reactive([
  { category: '上衣', label: '上衣', garment: null, required: true },
  { category: '下装', label: '下装', garment: null, required: true },
  { category: '外套', label: '外套', garment: null, required: false },
  { category: '鞋', label: '鞋', garment: null, required: false },
  { category: '配饰', label: '配饰', garment: null, required: false },
])

const hasAnyGarment = computed(() => outfitSlots.some((s) => s.garment))

function isInOutfit(garmentId) {
  return outfitSlots.some((s) => s.garment?.id === garmentId)
}

async function loadGarments() {
  garmentLoading.value = true
  try {
    const params = { page: 1, page_size: 100 }
    if (activeCategory.value) params.category = activeCategory.value
    const { data } = await api.get('/garments', { params })
    garments.value = data.items || data.garments || data || []
  } catch {
    garments.value = []
  } finally {
    garmentLoading.value = false
  }
}

/**
 * 将衣物添加到搭配槽位
 *
 * 规则：
 * 1. 同一件衣物不能重复添加
 * 2. 只能放入对应分类的槽位（上衣→上衣位，鞋→鞋位）
 * 3. 如果该分类已满，提示用户先移除
 * 4. 不再回退到其他分类的空位
 */
function addToSlot(garment) {
  // 规则1：已存在则跳过
  if (isInOutfit(garment.id)) return

  // 规则2：找对应分类的槽位
  const matchSlot = outfitSlots.find((s) => s.category === garment.category)

  if (!matchSlot) {
    // 分类不在搭配槽位中（不应该发生，但防御性处理）
    message.warning(`"${garment.category}" 不是有效的搭配分类`)
    return
  }

  if (matchSlot.garment) {
    // 规则3：该分类已满，替换已有衣物
    const oldName = matchSlot.garment.category
    matchSlot.garment = garment
    message.info(`已替换${oldName}`)
    return
  }

  // 放入对应槽位
  matchSlot.garment = garment
}

function removeFromSlot(category) {
  const slot = outfitSlots.find((s) => s.category === category)
  if (slot?.garment) {
    slot.garment = null
  }
}

async function saveOutfit() {
  // 检查必填槽位
  const emptyRequired = outfitSlots.filter((s) => s.required && !s.garment)
  if (emptyRequired.length > 0) {
    message.warning(`请先选择${emptyRequired.map((s) => s.label).join('和')}`)
    return
  }

  const garmentIds = outfitSlots.filter((s) => s.garment).map((s) => s.garment.id)
  if (!garmentIds.length) return

  saving.value = true
  try {
    await api.post('/outfits', { garment_ids: garmentIds })
    message.success('穿搭已保存')
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => loadGarments())
</script>

<style scoped>
.builder-page {
  animation: pageEnter 0.3s ease;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
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

.glass-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
}

.builder-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: start;
}

.garment-panel {
  padding: 20px;
}

.preview-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-canvas {
  padding: 20px;
}

.panel-header {
  margin-bottom: 16px;
}

.panel-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
}

.filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.tab {
  padding: 8px 14px;
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

.tab:hover {
  color: var(--theme-text, #2E2A23);
}

.tab.active {
  color: var(--theme-primary, #70645A);
  border-bottom-color: var(--theme-primary, #70645A);
}

.loading-area {
  text-align: center;
  padding: 40px 0;
}

.garment-scroll {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-height: 60vh;
  overflow-y: auto;
}

.garment-thumb {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  background: var(--theme-surface-bg, rgba(240, 235, 227, 0.5));
}

.garment-thumb:hover {
  border-color: rgba(200, 160, 155, 0.6);
  transform: translateY(-1px);
}

.garment-thumb.selected {
  border-color: var(--theme-accent, #C8A09B);
  opacity: 0.5;
  pointer-events: none;
}

.garment-thumb img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.thumb-label {
  display: block;
  text-align: center;
  font-size: 11px;
  color: var(--theme-text-secondary, #8C8478);
  padding: 4px;
}

.empty-inline {
  text-align: center;
  padding: 40px 0;
}

/* Slots grid */
.slots-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.slot-box {
  position: relative;
  aspect-ratio: 1;
  border: 2px dashed rgba(140, 132, 120, 0.35);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.2));
  overflow: hidden;
}

.slot-box:hover {
  border-color: rgba(200, 160, 155, 0.6);
}

.slot-box.filled {
  border-style: solid;
  border-color: rgba(200, 160, 155, 0.5);
}

.slot-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--theme-text-secondary, #8C8478);
}

.slot-empty span {
  font-size: 12px;
  font-weight: 500;
}

.slot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slot-remove-hint {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(46, 42, 37, 0.6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.slot-box.filled:hover .slot-remove-hint {
  opacity: 1;
}

.save-btn {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4)) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  font-family: 'Noto Serif SC', serif !important;
  font-weight: 600 !important;
}

@media (max-width: 768px) {
  .builder-layout {
    grid-template-columns: 1fr;
  }

  .garment-scroll {
    grid-template-columns: repeat(3, 1fr);
    max-height: 35vh;
  }

  .slots-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
