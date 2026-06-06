<template>
  <div class="calendar-page">
    <div class="page-header">
      <div>
        <h2>穿搭日历</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <n-card class="month-nav" :bordered="false">
      <div class="month-nav-inner">
        <n-button quaternary circle @click="changeMonth(-1)">
          <template #icon><n-icon :component="ChevronBackOutline" /></template>
        </n-button>
        <span class="month-label">{{ year }}年{{ month }}月</span>
        <n-button quaternary circle @click="changeMonth(1)">
          <template #icon><n-icon :component="ChevronForwardOutline" /></template>
        </n-button>
      </div>
    </n-card>

    <div class="weekday-row">
      <span v-for="d in weekdays" :key="d" class="weekday-cell">{{ d }}</span>
    </div>

    <div class="cal-grid">
      <div
        v-for="(day, i) in calendarDays"
        :key="i"
        :class="['day-cell', { today: day.isToday, other: !day.currentMonth, hasOutfit: day.hasOutfit }]"
        @click="day.currentMonth && openDay(day)"
      >
        <span :class="['day-num', { 'day-num-today': day.isToday }]">{{ day.date }}</span>
        <template v-if="day.hasOutfit && day.currentMonth">
          <img v-if="day.illustrationUrl" :src="day.illustrationUrl" class="day-illust" />
          <div v-else class="day-dot" />
        </template>
      </div>
    </div>

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="max-width: 460px; border-radius: 12px"
      :title="selectedDay ? `${selectedDay.fullDate} 穿搭` : ''"
      :bordered="false"
    >
      <template v-if="selectedDay?.outfit">
        <div v-if="selectedDay.illustrationUrl" class="illust-display">
          <img :src="selectedDay.illustrationUrl" class="illust-img" />
        </div>

        <div v-if="!selectedDay.illustrationUrl" class="illust-generate">
          <n-button
            type="primary"
            :loading="generating"
            @click="generateIllustration"
            size="large"
            class="generate-btn"
          >
            <template #icon><n-icon :component="ColorWandOutline" /></template>
            生成 AI 穿搭插画
          </n-button>
        </div>

        <div class="modal-garment-grid">
          <div v-for="(g, i) in selectedDay.outfit.garments" :key="i" class="modal-garment-item">
            <img :src="getGarmentImg(g)" class="modal-garment-img" />
            <span class="modal-garment-cat">{{ g.category }}</span>
          </div>
        </div>

        <div v-if="selectedDay.outfit.weather" class="weather-row">
          <span class="weather-tag">{{ selectedDay.outfit.weather }} {{ selectedDay.outfit.temperature }}℃</span>
        </div>

        <p v-if="selectedDay.outfit.reason" class="outfit-reason">
          {{ selectedDay.outfit.reason }}
        </p>
      </template>

      <template v-else>
        <div class="modal-empty">
          <p class="modal-empty-text">这天还没有穿搭记录</p>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  ChevronBackOutline,
  ChevronForwardOutline,
  ColorWandOutline,
  CalendarOutline,
} from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()
const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const outfits = ref({})
const showModal = ref(false)
const selectedDay = ref(null)
const generating = ref(false)

function monthStr() {
  return `${year.value}-${String(month.value).padStart(2, '0')}`
}

function changeMonth(delta) {
  let m = month.value + delta
  let y = year.value
  if (m < 1) { m = 12; y-- }
  if (m > 12) { m = 1; y++ }
  month.value = m
  year.value = y
  loadCalendar()
}

function getGarmentImg(g) {
  const url = g.image_url || g.processed_url || g.thumbnail_url
  if (url && url.startsWith('/')) return API_BASE + url
  return url || ''
}

function getIllustrationUrl(url) {
  if (!url) return ''
  if (url.startsWith('/')) return API_BASE + url
  return url
}

const calendarDays = computed(() => {
  const first = new Date(year.value, month.value - 1, 1)
  const startDay = first.getDay()
  const daysInMonth = new Date(year.value, month.value, 0).getDate()
  const prevDays = new Date(year.value, month.value - 1, 0).getDate()
  const todayStr = new Date().toISOString().split('T')[0]
  const days = []

  for (let i = startDay - 1; i >= 0; i--) {
    days.push({ date: prevDays - i, currentMonth: false, isToday: false, hasOutfit: false })
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const ds = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const outfitData = outfits.value[ds]
    days.push({
      date: d,
      currentMonth: true,
      isToday: ds === todayStr,
      hasOutfit: !!outfitData,
      illustrationUrl: getIllustrationUrl(outfitData?.illustration_url),
      fullDate: ds,
      outfit: outfitData,
    })
  }

  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ date: d, currentMonth: false, isToday: false, hasOutfit: false })
  }

  return days
})

async function loadCalendar() {
  try {
    const { data } = await api.get('/outfits/calendar', { params: { month: monthStr() } })
    const map = {}
    const days = data.days || []
    if (Array.isArray(days)) {
      days.forEach(d => {
        if (d.outfit && d.date) map[d.date] = d.outfit
      })
    }
    outfits.value = map
  } catch {}
}

function openDay(day) {
  selectedDay.value = { ...day }
  showModal.value = true
}

async function generateIllustration() {
  if (!selectedDay.value?.outfit?.id) return
  generating.value = true
  try {
    const { data } = await api.post(`/outfits/${selectedDay.value.outfit.id}/illustration`)
    if (data.illustration_url) {
      const url = getIllustrationUrl(data.illustration_url)
      selectedDay.value = { ...selectedDay.value, illustrationUrl: url }
      if (outfits.value[selectedDay.value.fullDate]) {
        outfits.value[selectedDay.value.fullDate].illustration_url = data.illustration_url
      }
      message.success('插画生成成功')
    }
  } catch (err) {
    message.error(err.response?.data?.detail || '生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

onMounted(() => loadCalendar())
</script>

<style scoped>
.calendar-page {
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
  font-size: 24px;
  font-weight: 600;
  color: #2C2A25;
  letter-spacing: 1px;
}

.page-line {
  width: 100%;
  height: 1px;
  background: #E8E3DA;
  margin-top: 8px;
}

.month-nav {
  border: 1px solid #E8E3DA;
  box-shadow: 0 1px 4px rgba(44, 42, 37, 0.04);
  margin-bottom: 20px;
}

.month-nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.month-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2C2A25;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 8px;
}

.weekday-cell {
  font-size: 13px;
  font-weight: 600;
  color: #8A8578;
  padding: 8px 0;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  border-radius: 6px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #FFFDF9;
  border: 1px solid #E8E3DA;
  position: relative;
}

.day-cell:hover:not(.other) {
  background: rgba(91, 125, 106, 0.04);
  border-color: #5B7D6A;
}

.day-cell.other {
  opacity: 0.2;
  cursor: default;
}

.day-cell.today {
  background: rgba(91, 125, 106, 0.08);
  border-color: #5B7D6A;
}

.day-cell.hasOutfit {
  border-color: #C49A6C;
}

.day-num {
  font-size: 14px;
  font-weight: 600;
  color: #2C2A25;
}

.day-num-today {
  color: #5B7D6A;
  font-weight: 700;
}

.day-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C49A6C;
  margin-top: 4px;
}

.day-illust {
  width: 36px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  margin-top: 4px;
}

.illust-display {
  text-align: center;
  margin-bottom: 24px;
}

.illust-img {
  max-width: 280px;
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(44, 42, 37, 0.1);
}

.illust-generate {
  text-align: center;
  margin-bottom: 24px;
}

.generate-btn {
  border-radius: 8px;
  font-weight: 600;
  background: #5B7D6A !important;
  border-color: #5B7D6A !important;
  transition: all 0.2s ease;
}

.generate-btn:hover {
  background: #6B8D7A !important;
  border-color: #6B8D7A !important;
}

.modal-garment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.modal-garment-item {
  text-align: center;
}

.modal-garment-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 6px;
}

.modal-garment-cat {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #8A8578;
}

.weather-row {
  text-align: center;
  margin-top: 16px;
}

.weather-tag {
  font-size: 12px;
  color: #8A8578;
  background: #F6F3EE;
  padding: 4px 12px;
  border-radius: 4px;
}

.outfit-reason {
  text-align: center;
  font-size: 13px;
  color: #8A8578;
  margin-top: 10px;
  line-height: 1.6;
}

.modal-empty {
  text-align: center;
  padding: 24px 0;
}

.modal-empty-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  color: #8A8578;
}
</style>
