<template>
  <div class="weather-page">
    <div class="page-header">
      <div>
        <h2>天气预报</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- 城市选择 -->
    <div class="search-bar">
      <n-input
        v-model:value="city"
        placeholder="输入城市名称（如：北京、Shanghai）"
        clearable
        @keyup.enter="fetchWeather"
      >
        <template #prefix>
          <n-icon :component="SearchOutline" />
        </template>
      </n-input>
      <n-button type="primary" @click="fetchWeather" :loading="loading">
        查询
      </n-button>
    </div>

    <!-- 当前天气 -->
    <div v-if="currentWeather" class="current-weather-card">
      <div class="current-main">
        <div class="current-left">
          <div class="weather-icon">
            <span class="weather-emoji">{{ getWeatherEmoji(currentWeather.weather_code) }}</span>
          </div>
          <div class="current-temp">
            <span class="temp-value">{{ currentWeather.temp_c }}</span>
            <span class="temp-unit">°C</span>
          </div>
        </div>
        <div class="current-right">
          <div class="current-desc">{{ currentWeather.weather_desc }}</div>
          <div class="current-city">{{ city }}</div>
          <div class="current-time">体感温度 {{ currentWeather.feels_like_c }}°C</div>
        </div>
      </div>
      
      <div class="current-details">
        <div class="detail-item">
          <n-icon :component="WaterOutline" :size="16" />
          <span class="detail-label">湿度</span>
          <span class="detail-value">{{ currentWeather.humidity }}%</span>
        </div>
        <div class="detail-item">
          <n-icon :component="LeafOutline" :size="16" />
          <span class="detail-label">风速</span>
          <span class="detail-value">{{ currentWeather.wind_speed_kmph }} km/h {{ currentWeather.wind_dir }}</span>
        </div>
        <div class="detail-item">
          <n-icon :component="EyeOutline" :size="16" />
          <span class="detail-label">能见度</span>
          <span class="detail-value">{{ currentWeather.visibility }} km</span>
        </div>
        <div class="detail-item">
          <n-icon :component="SunnyOutline" :size="16" />
          <span class="detail-label">紫外线</span>
          <span class="detail-value">{{ getUVLevel(currentWeather.uv_index) }}</span>
        </div>
      </div>
    </div>

    <!-- 天气预报 -->
    <div v-if="forecast.length" class="forecast-section">
      <div class="section-header">
        <n-icon :component="CalendarOutline" :size="18" />
        <span>未来 {{ forecast.length }} 天预报</span>
      </div>
      
      <div class="forecast-grid">
        <div v-for="day in forecast" :key="day.date" class="forecast-card">
          <div class="forecast-date">{{ formatForecastDate(day.date) }}</div>
          <div class="forecast-emoji">{{ getDayWeatherEmoji(day) }}</div>
          <div class="forecast-temp">
            <span class="temp-high">{{ day.max_temp_c }}°</span>
            <span class="temp-divider">/</span>
            <span class="temp-low">{{ day.min_temp_c }}°</span>
          </div>
          <div class="forecast-sun">
            <span>🌅 {{ day.sunrise }}</span>
            <span>🌇 {{ day.sunset }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 穿衣建议 -->
    <div v-if="currentWeather && Number(currentWeather.temp_c) !== NaN" class="outfit-suggestion-card">
      <div class="section-header">
        <n-icon :component="ShirtOutline" :size="18" />
        <span>今日穿衣建议</span>
      </div>
      <div class="suggestion-content">
        <div class="suggestion-icon">{{ getOutfitIcon(currentWeather.temp_c) }}</div>
        <div class="suggestion-text">
          <p class="suggestion-main">{{ getOutfitSuggestion(currentWeather.temp_c) }}</p>
          <p class="suggestion-detail">{{ getOutfitDetail(currentWeather.temp_c, currentWeather.weather_desc) }}</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !currentWeather" class="loading-state">
      <n-spin size="large" />
      <p>正在获取天气数据...</p>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !currentWeather && !error" class="empty-state">
      <div class="empty-icon">🌤️</div>
      <p class="empty-text">输入城市名称查看天气</p>
      <p class="empty-sub">支持中文城市名，如：北京、上海、广州</p>
    </div>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p class="error-text">获取天气数据失败</p>
      <p class="error-sub">请检查城市名称是否正确，或稍后重试</p>
      <n-button @click="fetchWeather" size="small">重试</n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  SearchOutline,
  WaterOutline,
  LeafOutline,
  EyeOutline,
  SunnyOutline,
  CalendarOutline,
  ShirtOutline,
} from '@vicons/ionicons5'
import { NInput, NButton, NIcon, NSpin } from 'naive-ui'
import api from '../api/index.js'

const city = ref('Beijing')
const loading = ref(false)
const error = ref(false)
const currentWeather = ref(null)
const forecast = ref([])

// 天气代码对应 emoji
const weatherEmojiMap = {
  '113': '☀️', '116': '⛅', '119': '☁️', '122': '☁️',
  '143': '🌫️', '176': '🌦️', '179': '🌨️', '182': '🌧️',
  '185': '🌧️', '200': '⛈️', '227': '🌨️', '230': '❄️',
  '248': '🌫️', '260': '🌫️', '263': '🌦️', '266': '🌧️',
  '281': '🌧️', '284': '🌧️', '293': '🌦️', '296': '🌧️',
  '299': '🌧️', '302': '🌧️', '305': '🌧️', '308': '🌧️',
  '311': '🌧️', '314': '🌧️', '317': '🌨️', '320': '🌨️',
  '323': '🌨️', '326': '🌨️', '329': '❄️', '332': '❄️',
  '335': '❄️', '338': '❄️', '350': '🌨️', '353': '🌦️',
  '356': '🌧️', '359': '🌧️', '362': '🌨️', '365': '🌨️',
  '368': '🌨️', '371': '❄️', '374': '🌨️', '377': '🌨️',
  '386': '⛈️', '389': '⛈️', '392': '⛈️', '395': '❄️',
}

function getWeatherEmoji(code) {
  return weatherEmojiMap[code] || '🌤️'
}

function getDayWeatherEmoji(day) {
  // 取中午的天气
  const noon = day.hourly?.find(h => h.time === '1200')
  if (noon) return getWeatherEmoji(noon.weather_code)
  return '🌤️'
}

function getUVLevel(index) {
  const i = Number(index)
  if (i <= 2) return '低'
  if (i <= 5) return '中等'
  if (i <= 7) return '高'
  if (i <= 10) return '很高'
  return '极高'
}

function getOutfitIcon(temp) {
  const t = Number(temp)
  if (t >= 30) return '🩳'
  if (t >= 25) return '👕'
  if (t >= 20) return '👔'
  if (t >= 15) return '🧥'
  if (t >= 10) return '🧣'
  if (t >= 5) return '🧤'
  return '🧥'
}

function getOutfitSuggestion(temp) {
  const t = Number(temp)
  if (t >= 30) return '炎热天气，建议穿着轻薄透气'
  if (t >= 25) return '温暖天气，短袖短裤即可'
  if (t >= 20) return '舒适温度，薄外套或长袖'
  if (t >= 15) return '微凉天气，建议穿外套'
  if (t >= 10) return '较冷天气，需要厚外套'
  if (t >= 5) return '寒冷天气，注意保暖'
  return '严寒天气，全副武装'
}

function getOutfitDetail(temp, weather) {
  const t = Number(temp)
  let detail = ''
  if (weather && weather.includes('雨')) {
    detail += '记得带伞！'
  }
  if (t >= 30) {
    detail += '选择棉麻材质，浅色系更凉爽。'
  } else if (t >= 20) {
    detail += '可以搭配薄外套，方便穿脱。'
  } else if (t >= 10) {
    detail += '内搭+外套的组合最实用。'
  } else {
    detail += '多层叠穿，注意头部和手脚保暖。'
  }
  return detail || '根据体感适当调整穿着。'
}

function formatForecastDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}/${d.getDate()} ${weekdays[d.getDay()]}`
}

async function fetchWeather() {
  if (!city.value.trim()) return
  
  loading.value = true
  error.value = false
  currentWeather.value = null
  forecast.value = []
  
  try {
    // 获取当前天气
    const { data: current } = await api.get('/weather/current', {
      params: { city: city.value.trim() }
    })
    
    if (current.error) {
      error.value = true
      return
    }
    
    currentWeather.value = current
    
    // 获取预报
    const { data: forecastData } = await api.get('/weather/forecast', {
      params: { city: city.value.trim(), days: 3 }
    })
    
    forecast.value = forecastData.forecasts || []
    
  } catch (err) {
    console.error('Weather fetch error:', err)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchWeather()
})
</script>

<style scoped>
.weather-page {
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

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-bar .n-input {
  flex: 1;
}

/* 当前天气卡片 */
.current-weather-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: var(--theme-card-shadow);
  transition: background 0.4s ease;
}

.current-main {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 24px;
}

.current-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.weather-emoji {
  font-size: 56px;
  line-height: 1;
}

.current-temp {
  display: flex;
  align-items: flex-start;
}

.temp-value {
  font-family: 'Noto Serif SC', serif;
  font-size: 64px;
  font-weight: 700;
  color: var(--theme-text, #2E2A23);
  line-height: 1;
}

.temp-unit {
  font-size: 24px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 8px;
  margin-left: 4px;
}

.current-right {
  flex: 1;
}

.current-desc {
  font-size: 20px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 4px;
}

.current-city {
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 2px;
}

.current-time {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
}

.current-details {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.3));
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--theme-text-secondary, #8C8478);
}

.detail-label {
  font-size: 12px;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
}

/* 预报区域 */
.forecast-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 16px;
}

.forecast-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.forecast-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: var(--theme-card-shadow);
  transition: all 0.3s ease;
}

.forecast-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.forecast-date {
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 12px;
}

.forecast-emoji {
  font-size: 36px;
  margin-bottom: 12px;
}

.forecast-temp {
  margin-bottom: 8px;
}

.temp-high {
  font-size: 20px;
  font-weight: 700;
  color: var(--theme-text, #2E2A23);
}

.temp-divider {
  color: var(--theme-text-secondary, #8C8478);
  margin: 0 4px;
}

.temp-low {
  font-size: 16px;
  color: var(--theme-text-secondary, #8C8478);
}

.forecast-sun {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
}

/* 穿衣建议 */
.outfit-suggestion-card {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: background 0.4s ease;
}

.outfit-suggestion-card .section-header {
  color: #FFFFFF;
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.suggestion-icon {
  font-size: 48px;
}

.suggestion-text {
  flex: 1;
}

.suggestion-main {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 6px;
}

.suggestion-detail {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* 状态 */
.loading-state,
.empty-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon,
.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text,
.error-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 8px;
}

.empty-sub,
.error-sub {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-bottom: 16px;
}

.loading-state p {
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 16px;
}

@media (max-width: 768px) {
  .current-main {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .current-left {
    justify-content: center;
  }
  
  .current-details {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .forecast-grid {
    grid-template-columns: 1fr;
  }
  
  .suggestion-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
