<template>
  <div class="ai-page">
    <div class="page-header">
      <div>
        <h2>AI 穿搭助手</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- 功能选项卡 -->
    <div class="ai-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        :class="['ai-tab', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <n-icon :component="tab.icon" :size="20" />
        <span>{{ tab.label }}</span>
      </div>
    </div>

    <!-- 智能穿搭推荐 -->
    <div v-if="activeTab === 'recommend'" class="ai-section">
      <div class="section-config">
        <div class="config-row">
          <div class="config-item">
            <label>城市</label>
            <n-input v-model:value="recommendCity" placeholder="如：北京" size="small" />
          </div>
          <div class="config-item">
            <label>场合</label>
            <n-select v-model:value="recommendOccasion" :options="occasionOptions" size="small" />
          </div>
          <n-button type="primary" @click="fetchRecommendation" :loading="recommendLoading">
            获取推荐
          </n-button>
        </div>
      </div>

      <!-- 天气信息 -->
      <div v-if="recommendation?.weather" class="weather-info-card">
        <div class="weather-main">
          <span class="weather-emoji">{{ getWeatherEmoji(recommendation.temp_category) }}</span>
          <div>
            <div class="weather-temp">{{ recommendation.weather.temp_c }}°C</div>
            <div class="weather-desc">{{ recommendation.weather.weather_desc }}</div>
          </div>
        </div>
        <div class="weather-tips">
          <p v-for="tip in recommendation.outfit_tips" :key="tip">{{ tip }}</p>
        </div>
      </div>

      <!-- 推荐理由 -->
      <div v-if="recommendation?.reason" class="recommend-reason">
        <n-icon :component="BulbOutline" :size="16" />
        <span>{{ recommendation.reason }}</span>
      </div>

      <!-- 推荐衣物列表 -->
      <div v-if="recommendation?.recommendations?.length" class="recommend-grid">
        <div v-for="item in recommendation.recommendations" :key="item.id" class="recommend-card">
          <div class="recommend-img-wrap">
            <img v-if="item.image_url" :src="getImageUrl(item.image_url)" class="recommend-img" />
            <div v-else class="recommend-img-placeholder">👕</div>
          </div>
          <div class="recommend-info">
            <div class="recommend-name">{{ item.name }}</div>
            <div class="recommend-category">{{ item.category }}</div>
            <div class="recommend-tags">
              <span v-for="tag in item.style_tags" :key="tag" class="style-tag">{{ tag }}</span>
            </div>
            <div class="recommend-score">
              <div class="score-bar">
                <div class="score-fill" :style="{ width: `${Math.min(item.score * 10, 100)}%` }"></div>
              </div>
              <span class="score-text">匹配度 {{ Math.min(item.score * 10, 100) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="recommendation && !recommendation.recommendations?.length" class="empty-state">
        <div class="empty-icon">👔</div>
        <p>{{ recommendation.message || '暂无推荐' }}</p>
      </div>
    </div>

    <!-- 风格分析 -->
    <div v-if="activeTab === 'style'" class="ai-section">
      <n-button type="primary" @click="fetchStyleAnalysis" :loading="styleLoading" style="margin-bottom: 20px;">
        分析我的风格
      </n-button>

      <div v-if="styleAnalysis" class="style-results">
        <!-- 主要风格 -->
        <div class="main-style-card">
          <div class="main-style-icon">{{ getStyleEmoji(styleAnalysis.main_style) }}</div>
          <div class="main-style-info">
            <div class="main-style-label">您的主要风格</div>
            <div class="main-style-name">{{ styleAnalysis.main_style }}</div>
            <div class="main-style-desc">{{ styleAnalysis.style_description }}</div>
          </div>
        </div>

        <!-- 风格分布 -->
        <div class="style-distribution">
          <h4>风格分布</h4>
          <div class="distribution-bars">
            <div v-for="([style, percent]) in styleAnalysis.style_tags" :key="style" class="distribution-item">
              <div class="distribution-label">
                <span class="distribution-emoji">{{ getStyleEmoji(style) }}</span>
                <span>{{ style }}</span>
              </div>
              <div class="distribution-bar">
                <div class="distribution-fill" :style="{ width: `${percent}%`, background: getStyleColor(style) }"></div>
              </div>
              <span class="distribution-percent">{{ percent }}%</span>
            </div>
          </div>
        </div>

        <!-- 衣橱统计 -->
        <div class="wardrobe-stats-grid">
          <div class="stat-card">
            <h4>衣物总数</h4>
            <div class="stat-number">{{ styleAnalysis.total_garments }}</div>
          </div>
          <div class="stat-card">
            <h4>主要品类</h4>
            <div class="stat-list">
              <div v-for="([cat, count]) in styleAnalysis.top_categories?.slice(0, 3)" :key="cat" class="stat-list-item">
                <span>{{ cat }}</span>
                <span class="stat-count">{{ count }}件</span>
              </div>
            </div>
          </div>
          <div class="stat-card">
            <h4>色彩偏好</h4>
            <div class="color-chips">
              <div v-for="([color, count]) in styleAnalysis.top_colors?.slice(0, 5)" :key="color" class="color-chip">
                <div class="color-dot" :style="{ background: getColorHex(color) }"></div>
                <span>{{ color }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI 建议 -->
        <div class="ai-suggestions">
          <h4>
            <n-icon :component="BulbOutline" :size="16" />
            <span>AI 建议</span>
          </h4>
          <ul>
            <li v-for="(suggestion, i) in styleAnalysis.suggestions" :key="i">{{ suggestion }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 衣物识别 -->
    <div v-if="activeTab === 'identify'" class="ai-section">
      <div class="identify-upload-area" @click="triggerUpload" @drop.prevent="handleDrop" @dragover.prevent>
        <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleFileSelect" />
        
        <div v-if="!identifyImage" class="upload-placeholder">
          <n-icon :component="CloudUploadOutline" :size="48" />
          <p>点击或拖拽上传衣物照片</p>
          <p class="upload-hint">支持 JPG、PNG 格式，最大 10MB</p>
        </div>
        
        <div v-else class="upload-preview">
          <img :src="identifyImage" class="preview-img" />
        </div>
      </div>

      <n-button 
        v-if="identifyImage" 
        type="primary" 
        @click="identifyGarment" 
        :loading="identifyLoading"
        style="margin-top: 16px; width: 100%;"
      >
        开始识别
      </n-button>

      <!-- 识别结果 -->
      <div v-if="identifyResult" class="identify-result">
        <div class="result-header">
          <n-icon :component="CheckmarkCircleOutline" :size="20" color="#52c41a" />
          <span>识别完成</span>
        </div>
        
        <div class="result-form">
          <div class="form-item">
            <label>衣物类型</label>
            <n-select 
              v-model:value="identifyResult.identified.category" 
              :options="identifyResult.suggested_categories.map(c => ({ label: c, value: c }))"
            />
          </div>
          <div class="form-item">
            <label>颜色</label>
            <n-select 
              v-model:value="identifyResult.identified.color" 
              :options="identifyResult.suggested_colors.map(c => ({ label: c, value: c }))"
            />
          </div>
          <div class="form-item">
            <label>材质</label>
            <n-select 
              v-model:value="identifyResult.identified.material" 
              :options="identifyResult.suggested_materials.map(m => ({ label: m, value: m }))"
            />
          </div>
          <div class="form-item">
            <label>季节</label>
            <n-select 
              v-model:value="identifyResult.identified.season" 
              :options="seasonOptions"
            />
          </div>
        </div>

        <div class="result-actions">
          <n-button @click="saveIdentifiedGarment" type="primary">保存到衣橱</n-button>
          <n-button @click="resetIdentify">重新识别</n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  SparklesOutline,
  ColorPaletteOutline,
  CameraOutline,
  BulbOutline,
  CloudUploadOutline,
  CheckmarkCircleOutline,
} from '@vicons/ionicons5'
import { NInput, NSelect, NButton, NIcon, useMessage } from 'naive-ui'
import api from '../api/index.js'

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`
const message = useMessage()

const activeTab = ref('recommend')

const tabs = [
  { key: 'recommend', label: '智能推荐', icon: SparklesOutline },
  { key: 'style', label: '风格分析', icon: ColorPaletteOutline },
  { key: 'identify', label: '衣物识别', icon: CameraOutline },
]

// 推荐相关
const recommendCity = ref('Beijing')
const recommendOccasion = ref('日常')
const recommendLoading = ref(false)
const recommendation = ref(null)

const occasionOptions = [
  { label: '日常', value: '日常' },
  { label: '工作', value: '工作' },
  { label: '约会', value: '约会' },
  { label: '运动', value: '运动' },
]

// 风格分析相关
const styleLoading = ref(false)
const styleAnalysis = ref(null)

// 衣物识别相关
const fileInput = ref(null)
const identifyImage = ref('')
const identifyFile = ref(null)
const identifyLoading = ref(false)
const identifyResult = ref(null)

const seasonOptions = [
  { label: '春季', value: '春季' },
  { label: '夏季', value: '夏季' },
  { label: '秋季', value: '秋季' },
  { label: '冬季', value: '冬季' },
  { label: '四季', value: '四季' },
]

// 工具函数
function getImageUrl(url) {
  if (url && url.startsWith('/')) return API_BASE + url
  return url
}

function getWeatherEmoji(category) {
  const map = { hot: '🥵', warm: '☀️', mild: '🌤️', cool: '🌥️', cold: '❄️', very_cold: '🥶' }
  return map[category] || '🌤️'
}

function getStyleEmoji(style) {
  const map = {
    '极简': '⬜', '复古': '🎞️', '街头': '🛹', '优雅': '👗',
    '运动': '🏃', '休闲': '😎', '商务': '💼', '文艺': '🎨',
  }
  return map[style] || '👔'
}

function getStyleColor(style) {
  const map = {
    '极简': '#888888', '复古': '#8B7355', '街头': '#FF6B6B', '优雅': '#C084FC',
    '运动': '#22C55E', '休闲': '#60A5FA', '商务': '#1E293B', '文艺': '#F59E0B',
  }
  return map[style] || '#888888'
}

function getColorHex(color) {
  const map = {
    '黑色': '#000000', '白色': '#FFFFFF', '灰色': '#808080', '蓝色': '#3B82F6',
    '红色': '#EF4444', '绿色': '#22C55E', '黄色': '#EAB308', '粉色': '#EC4899',
    '棕色': '#92400E', '米色': '#F5F0DC', '深蓝': '#1E3A5F', '浅蓝': '#93C5FD',
    '酒红': '#722F37', '卡其色': '#C3B091', '驼色': '#C19A6B',
  }
  return map[color] || '#CCCCCC'
}

// 获取推荐
async function fetchRecommendation() {
  recommendLoading.value = true
  try {
    const { data } = await api.get('/ai/recommend', {
      params: { city: recommendCity.value, occasion: recommendOccasion.value }
    })
    recommendation.value = data
  } catch (err) {
    message.error('获取推荐失败')
    console.error(err)
  } finally {
    recommendLoading.value = false
  }
}

// 获取风格分析
async function fetchStyleAnalysis() {
  styleLoading.value = true
  try {
    const { data } = await api.get('/ai/style-analysis')
    styleAnalysis.value = data
  } catch (err) {
    message.error('分析失败')
    console.error(err)
  } finally {
    styleLoading.value = false
  }
}

// 衣物识别
function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

function handleDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file) processFile(file)
}

function processFile(file) {
  if (!file.type.startsWith('image/')) {
    message.error('请选择图片文件')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    message.error('图片大小不能超过 10MB')
    return
  }
  
  identifyFile.value = file
  identifyImage.value = URL.createObjectURL(file)
  identifyResult.value = null
}

async function identifyGarment() {
  if (!identifyFile.value) return
  
  identifyLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', identifyFile.value)
    
    const { data } = await api.post('/ai/identify-garment', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    identifyResult.value = data
  } catch (err) {
    message.error('识别失败')
    console.error(err)
  } finally {
    identifyLoading.value = false
  }
}

async function saveIdentifiedGarment() {
  if (!identifyResult.value) return
  
  try {
    const { identified, image_url } = identifyResult.value
    await api.post('/garments', {
      name: identified.category,
      category: identified.category,
      color: identified.color,
      material: identified.material,
      season: identified.season,
      image_url: image_url,
    })
    message.success('已保存到衣橱')
    resetIdentify()
  } catch (err) {
    message.error('保存失败')
    console.error(err)
  }
}

function resetIdentify() {
  identifyImage.value = ''
  identifyFile.value = null
  identifyResult.value = null
}
</script>

<style scoped>
.ai-page {
  animation: pageEnter 0.3s ease;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  margin-bottom: 24px;
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
  background: var(--theme-glass-border, rgba(255, 255, 255, 0.4));
  margin-top: 8px;
}

/* 选项卡 */
.ai-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.ai-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--theme-text-secondary, #8C8478);
  font-size: 14px;
}

.ai-tab:hover {
  background: var(--theme-input-focus-bg, rgba(255, 255, 255, 0.45));
}

.ai-tab.active {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  color: #FFFFFF;
  border-color: transparent;
}

/* 配置区域 */
.section-config {
  margin-bottom: 20px;
}

.config-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.config-item {
  flex: 1;
}

.config-item label {
  display: block;
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 6px;
}

/* 天气信息卡片 */
.weather-info-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.weather-emoji {
  font-size: 40px;
}

.weather-temp {
  font-size: 24px;
  font-weight: 700;
  color: var(--theme-text, #2E2A23);
}

.weather-desc {
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
}

.weather-tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.weather-tips p {
  font-size: 12px;
  padding: 4px 10px;
  background: var(--theme-input-bg, rgba(0, 0, 0, 0.05));
  border-radius: 4px;
  color: var(--theme-text-secondary, #8C8478);
}

/* 推荐理由 */
.recommend-reason {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  border-radius: 8px;
  margin-bottom: 20px;
  color: #FFFFFF;
  font-size: 14px;
}

/* 推荐网格 */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.recommend-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.recommend-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.recommend-img-wrap {
  height: 160px;
  overflow: hidden;
}

.recommend-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommend-img-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  background: var(--theme-input-bg, rgba(0, 0, 0, 0.05));
}

.recommend-info {
  padding: 14px;
}

.recommend-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 4px;
}

.recommend-category {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 8px;
}

.recommend-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.style-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: var(--theme-input-bg, rgba(0, 0, 0, 0.05));
  border-radius: 4px;
  color: var(--theme-text-secondary, #8C8478);
}

.recommend-score {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: var(--theme-input-bg, rgba(0, 0, 0, 0.05));
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #70645A, #A0815A);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.score-text {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
  white-space: nowrap;
}

/* 风格分析结果 */
.style-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.main-style-card {
  display: flex;
  align-items: center;
  gap: 24px;
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  border-radius: 16px;
  padding: 28px;
}

.main-style-icon {
  font-size: 64px;
}

.main-style-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4px;
}

.main-style-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 6px;
}

.main-style-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.style-distribution {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
}

.style-distribution h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 16px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.distribution-label {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 80px;
  font-size: 13px;
  color: var(--theme-text, #2E2A23);
}

.distribution-emoji {
  font-size: 16px;
}

.distribution-bar {
  flex: 1;
  height: 8px;
  background: var(--theme-input-bg, rgba(0, 0, 0, 0.05));
  border-radius: 4px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.distribution-percent {
  width: 40px;
  text-align: right;
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
}

.wardrobe-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 16px;
}

.stat-card h4 {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 10px;
}

.stat-number {
  font-family: 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--theme-text, #2E2A23);
}

.stat-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-list-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--theme-text, #2E2A23);
}

.stat-count {
  color: var(--theme-text-secondary, #8C8478);
}

.color-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--theme-text, #2E2A23);
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--theme-glass-border, rgba(0, 0, 0, 0.1));
}

.ai-suggestions {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
}

.ai-suggestions h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 12px;
}

.ai-suggestions ul {
  list-style: none;
  padding: 0;
}

.ai-suggestions li {
  position: relative;
  padding-left: 16px;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--theme-text, #2E2A23);
  line-height: 1.5;
}

.ai-suggestions li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--theme-primary, #70645A);
}

/* 衣物识别 */
.identify-upload-area {
  border: 2px dashed var(--theme-glass-border, rgba(0, 0, 0, 0.15));
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.2));
}

.identify-upload-area:hover {
  border-color: var(--theme-primary, #70645A);
  background: var(--theme-input-focus-bg, rgba(255, 255, 255, 0.35));
}

.upload-placeholder {
  color: var(--theme-text-secondary, #8C8478);
}

.upload-placeholder p {
  margin-top: 12px;
  font-size: 15px;
}

.upload-hint {
  font-size: 12px !important;
  margin-top: 6px !important;
  opacity: 0.7;
}

.upload-preview {
  max-width: 300px;
  margin: 0 auto;
}

.preview-img {
  width: 100%;
  border-radius: 8px;
}

.identify-result {
  margin-top: 24px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 16px;
}

.result-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 6px;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
}

@media (max-width: 768px) {
  .ai-tabs {
    flex-wrap: wrap;
  }
  
  .config-row {
    flex-direction: column;
  }
  
  .recommend-grid {
    grid-template-columns: 1fr;
  }
  
  .wardrobe-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .main-style-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
