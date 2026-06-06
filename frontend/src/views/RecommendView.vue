<template>
  <div class="recommend-page">
    <div class="page-header">
      <div>
        <h2>智能推荐</h2>
        <p class="page-subtitle">AI 为你搭配今日穿搭</p>
      </div>
    </div>

    <n-card class="form-card" :bordered="false">
      <n-form label-placement="left" label-width="60">
        <n-form-item label="日期">
          <n-date-picker
            v-model:formatted-value="date"
            type="date"
            value-format="yyyy-MM-dd"
            style="width: 100%"
          />
        </n-form-item>

        <n-form-item label="场合">
          <div class="occasion-pills">
            <button
              v-for="o in occasions"
              :key="o.value"
              :class="['pill', { active: occasion === o.value }]"
              @click="occasion = o.value"
            >
              <n-icon :component="o.icon" :size="16" />
              {{ o.label }}
            </button>
          </div>
        </n-form-item>

        <n-form-item label="要求">
          <n-input
            v-model:value="extra"
            type="textarea"
            placeholder="例如：今天想穿得可爱一点"
            :rows="2"
          />
        </n-form-item>

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
      </n-form>
    </n-card>

    <div v-if="loading" class="loading-area">
      <n-spin size="large" />
      <p class="loading-text">AI 正在为你搭配中...</p>
    </div>

    <n-card v-if="result" class="result-card" :bordered="false" style="margin-top: 24px">
      <div class="result-header">
        <n-icon :component="SparklesOutline" :size="20" color="#7C5CFC" />
        <span class="result-title">推荐方案</span>
      </div>

      <p v-if="result.reason || result.explanation" class="result-reason">
        {{ result.reason || result.explanation }}
      </p>

      <div class="result-grid">
        <div v-for="(item, i) in resultItems" :key="i" class="result-item-card">
          <div class="result-item-img-wrap">
            <img :src="getImgUrl(item)" class="result-item-img" />
          </div>
          <div class="result-item-info">
            <div class="result-item-tags">
              <n-tag size="small" :bordered="false" round style="background: rgba(124, 92, 252, 0.1); color: #7C5CFC; font-weight: 500;">
                {{ item.category }}
              </n-tag>
              <n-tag v-if="item.is_cold_palace" size="small" :bordered="false" round style="background: rgba(255, 107, 157, 0.12); color: #FF6B9D; font-weight: 500;">
                冷宫唤醒
              </n-tag>
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
    </n-card>

    <div v-if="coldPalaceItems.length" class="cold-section">
      <div class="cold-header">
        <n-icon :component="SparklesOutline" :size="18" color="#6B7280" />
        <span class="cold-title">冷宫衣物 ({{ coldPalaceItems.length }} 件)</span>
      </div>
      <div class="cold-grid">
        <div v-for="item in coldPalaceItems" :key="item.id" class="cold-card">
          <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="cold-img" />
          <div class="cold-card-info">
            <n-tag size="tiny" :bordered="false" round style="background: #F3F4F6; color: #6B7280;">
              {{ item.category }}
            </n-tag>
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
  animation: pageEnter 0.25s ease;
}

@keyframes pageEnter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1A1625;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 14px;
  color: #6B6580;
  margin-top: 6px;
}

.form-card {
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(124, 92, 252, 0.04);
  border: 1px solid rgba(124, 92, 252, 0.08);
  margin-bottom: 8px;
}

.occasion-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
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

.recommend-btn {
  border-radius: 12px;
  height: 44px;
  font-weight: 600;
  background: linear-gradient(135deg, #7C5CFC, #9B82FD) !important;
  border: none !important;
  transition: all 0.2s ease;
}

.recommend-btn:hover {
  background: linear-gradient(135deg, #6344E0, #7C5CFC) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(124, 92, 252, 0.35);
}

.loading-area {
  text-align: center;
  padding: 60px 0;
}

.loading-text {
  font-size: 13px;
  color: #6B6580;
  margin-top: 12px;
}

.result-card {
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(124, 92, 252, 0.04);
  border: 1px solid rgba(124, 92, 252, 0.08);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.result-title {
  font-size: 18px;
  font-weight: 700;
  color: #1A1625;
}

.result-reason {
  font-size: 14px;
  line-height: 1.7;
  color: #6B6580;
  margin-bottom: 20px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

.result-item-card {
  background: #FFFFFF;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(124, 92, 252, 0.04);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(124, 92, 252, 0.08);
}

.result-item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(124, 92, 252, 0.12), 0 4px 12px rgba(0, 0, 0, 0.04);
}

.result-item-img-wrap {
  aspect-ratio: 1;
  background: #F5F3FF;
  overflow: hidden;
}

.result-item-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-item-info {
  padding: 10px;
}

.result-item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.result-item-reason {
  font-size: 12px;
  color: #6B6580;
  margin-top: 6px;
  line-height: 1.5;
}

.save-btn {
  margin-top: 24px;
  border-radius: 12px;
  height: 44px;
  font-weight: 600;
  background: #7C5CFC !important;
  border: none !important;
  transition: all 0.2s ease;
}

.save-btn:hover {
  background: #6344E0 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(124, 92, 252, 0.35);
}

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
  font-size: 16px;
  font-weight: 600;
  color: #1A1625;
}

.cold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.cold-card {
  background: #FFFFFF;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(124, 92, 252, 0.04);
  border: 1px solid rgba(124, 92, 252, 0.08);
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
}

.cold-days {
  font-size: 11px;
  color: #6B6580;
}
</style>
