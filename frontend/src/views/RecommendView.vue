<template>
  <div class="recommend-page">
    <div class="page-header">
      <div>
        <h2>穿搭推荐</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <div class="form-section">
      <p class="guide-text">今天想去哪里？</p>

      <div class="form-field">
        <label class="field-label">日期</label>
        <n-date-picker
          v-model:formatted-value="date"
          type="date"
          value-format="yyyy-MM-dd"
          style="width: 100%"
        />
      </div>

      <div class="form-field">
        <label class="field-label">场合</label>
        <div class="scene-grid">
          <div
            v-for="o in occasions"
            :key="o.value"
            :class="['scene-card', { active: occasion === o.value }]"
            @click="occasion = o.value"
          >
            <n-icon :component="o.icon" :size="24" />
            <span class="scene-label">{{ o.label }}</span>
          </div>
        </div>
      </div>

      <div class="form-field">
        <label class="field-label">要求</label>
        <n-input
          v-model:value="extra"
          type="textarea"
          placeholder="例如：今天想穿得可爱一点"
          :rows="2"
        />
      </div>

      <n-button
        type="primary"
        block
        :loading="loading"
        @click="getRecommend"
        size="large"
        class="recommend-btn"
      >
        <template #icon><n-icon :component="SparklesOutline" /></template>
        获取推荐
      </n-button>
    </div>

    <div v-if="loading" class="loading-area">
      <n-spin size="large" />
      <p class="loading-text">AI 正在为你搭配中...</p>
    </div>

    <div v-if="result" class="result-section">
      <div class="result-header">
        <span class="result-title">推荐方案</span>
      </div>

      <p v-if="result.reason || result.explanation" class="result-reason">
        {{ result.reason || result.explanation }}
      </p>

      <div class="result-list">
        <div v-for="(item, i) in resultItems" :key="i" class="result-item-card">
          <div class="result-item-img-wrap">
            <img :src="getImgUrl(item)" class="result-item-img" />
          </div>
          <div class="result-item-info">
            <div class="result-item-tags">
              <span class="result-cat">{{ item.category }}</span>
              <span v-if="item.is_cold_palace" class="cold-wake">冷宫唤醒</span>
            </div>
            <p v-if="item.reason" class="result-item-reason">{{ item.reason }}</p>
          </div>
        </div>
      </div>

      <n-button
        v-if="resultItems.length"
        type="primary"
        block
        size="large"
        class="save-btn"
        @click="saveOutfit"
      >
        <template #icon><n-icon :component="SaveOutline" /></template>
        保存这套穿搭
      </n-button>
    </div>

    <div v-if="coldPalaceItems.length" class="cold-section">
      <div class="cold-header">
        <span class="cold-title">冷宫衣物 ({{ coldPalaceItems.length }} 件)</span>
      </div>
      <div class="cold-grid">
        <div v-for="item in coldPalaceItems" :key="item.id" class="cold-card">
          <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="cold-img" />
          <div class="cold-card-info">
            <span class="cold-cat">{{ item.category }}</span>
            <span class="cold-days">{{ item.days_since }}天未穿</span>
          </div>
        </div>
      </div>
    </div>

    <n-alert v-if="error" type="error" :bordered="false" style="margin-top: 16px" closable @close="error = ''">
      {{ error }}
    </n-alert>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  SparklesOutline,
  SaveOutline,
  SunnyOutline,
  BriefcaseOutline,
  HeartOutline,
  WineOutline,
  BarbellOutline,
  RibbonOutline,
} from '@vicons/ionicons5'
import api from '../api/index.js'
import { getColdPalace } from '../api/index.js'

const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const today = new Date().toISOString().split('T')[0]
const date = ref(today)
const occasion = ref('')
const extra = ref('')
const loading = ref(false)
const result = ref(null)
const error = ref('')
const coldPalaceItems = ref([])

const occasions = [
  { value: 'daily', label: '日常', icon: SunnyOutline },
  { value: 'work', label: '工作', icon: BriefcaseOutline },
  { value: 'date', label: '约会', icon: HeartOutline },
  { value: 'party', label: '聚会', icon: WineOutline },
  { value: 'sport', label: '运动', icon: BarbellOutline },
  { value: 'formal', label: '正式', icon: RibbonOutline },
]

const resultItems = computed(() => result.value?.recommendations || result.value?.garments || result.value?.items || [])

function getImgUrl(item) {
  const url = item.image_url || item.thumbnail_url || item.processed_url
  if (url && url.startsWith('/')) return `${API_BASE}${url}`
  return url || ''
}

async function getRecommend() {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const { data } = await api.post('/recommend', {
      date: date.value,
      occasion: occasion.value,
      extra_requirements: extra.value,
    })
    result.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || '推荐失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await getColdPalace(30)
    coldPalaceItems.value = data?.items || []
  } catch {}
})

async function saveOutfit() {
  const items = resultItems.value
  const garmentIds = items.map(g => g.id).filter(Boolean)
  if (!garmentIds.length) return
  try {
    await api.post('/outfits', { date: date.value, garment_ids: garmentIds })
    message.success('穿搭已保存')
  } catch {
    message.error('保存失败')
  }
}
</script>

<style scoped>
.recommend-page {
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
  color: #2E2A23;
  letter-spacing: 1px;
}

.page-line {
  width: 100%;
  height: 1px;
  background: #E0D8CC;
  margin-top: 8px;
}

.form-section {
  background: #FFFDF8;
  border: 1px solid #E0D8CC;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.guide-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  color: #2E2A23;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.form-field {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: #8C8478;
  margin-bottom: 8px;
  font-weight: 500;
}

/* Scene cards */
.scene-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.scene-card {
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid #E0D8CC;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #8C8478;
  background: transparent;
}

.scene-card:hover {
  border-color: #A0815A;
  color: #2E2A23;
}

.scene-card.active {
  border-color: #A0815A;
  color: #A0815A;
  background: rgba(160, 129, 90, 0.06);
}

.scene-label {
  font-size: 14px;
  font-weight: 500;
}

.recommend-btn {
  border-radius: 8px;
  height: 44px;
  font-weight: 600;
  font-family: 'Noto Serif SC', serif;
  background: #A0815A !important;
  border-color: #A0815A !important;
  transition: all 0.2s ease;
}

.recommend-btn:hover {
  background: #B8956E !important;
  border-color: #B8956E !important;
}

.loading-area {
  text-align: center;
  padding: 60px 0;
}

.loading-text {
  font-size: 13px;
  color: #8C8478;
  margin-top: 12px;
}

/* Results */
.result-section {
  background: #FFFDF8;
  border: 1px solid #E0D8CC;
  border-radius: 8px;
  padding: 24px;
  margin-top: 24px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.result-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2E2A23;
}

.result-reason {
  font-size: 14px;
  line-height: 1.7;
  color: #8C8478;
  margin-bottom: 20px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item-card {
  display: flex;
  background: #FFFDF8;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E0D8CC;
  transition: all 0.3s ease;
}

.result-item-card:hover {
  border-left: 2px solid #A0815A;
}

.result-item-img-wrap {
  width: 50%;
  aspect-ratio: 1;
  background: #F5F0E8;
  overflow: hidden;
  flex-shrink: 0;
}

.result-item-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-item-info {
  width: 50%;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-left: 1px solid #E0D8CC;
}

.result-item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.result-cat {
  font-size: 13px;
  font-weight: 500;
  color: #A0815A;
}

.cold-wake {
  font-size: 11px;
  color: #C27C4E;
  background: rgba(194, 124, 78, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.result-item-reason {
  font-size: 12px;
  color: #8C8478;
  margin-top: 8px;
  line-height: 1.5;
}

.save-btn {
  margin-top: 24px;
  border-radius: 8px;
  height: 44px;
  font-weight: 600;
  background: #A0815A !important;
  border-color: #A0815A !important;
  transition: all 0.2s ease;
}

.save-btn:hover {
  background: #B8956E !important;
  border-color: #B8956E !important;
}

/* Cold palace */
.cold-section {
  margin-top: 28px;
}

.cold-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.cold-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #2E2A23;
}

.cold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.cold-card {
  background: #FFFDF8;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E0D8CC;
  transition: all 0.3s ease;
}

.cold-card:hover {
  border-left: 2px solid #A0815A;
}

.cold-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.cold-card-info {
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid #E0D8CC;
}

.cold-cat {
  font-size: 12px;
  color: #A0815A;
  font-weight: 500;
}

.cold-days {
  font-size: 11px;
  color: #8C8478;
}

@media (max-width: 768px) {
  .scene-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .result-item-card {
    flex-direction: column;
  }

  .result-item-img-wrap {
    width: 100%;
    aspect-ratio: 16/9;
  }

  .result-item-info {
    width: 100%;
    border-left: none;
    border-top: 1px solid #E0D8CC;
  }
}
</style>
