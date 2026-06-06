<template>
  <div class="calendar-page">
    <div class="page-header">
      <div>
        <h2>穿搭日历</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <div class="month-header">
      <span class="month-nav-btn" @click="changeMonth(-1)">◀</span>
      <span class="month-label">{{ year }}年{{ month }}月</span>
      <span class="month-nav-btn" @click="changeMonth(1)">▶</span>
      <n-button type="primary" size="small" class="gen-today-btn" @click="generateToday">
        生成今日推荐
      </n-button>
    </div>

    <div class="weekday-row">
      <span v-for="d in weekdays" :key="d" class="weekday-cell">{{ d }}</span>
    </div>

    <div class="cal-grid">
      <div
        v-for="(day, i) in calendarDays"
        :key="i"
        :class="['day-cell', {
          today: day.isToday,
          other: !day.currentMonth,
          selected: selectedDay?.fullDate === day.fullDate && day.currentMonth,
          weekend: day.isWeekend
        }]"
        @click="day.currentMonth && openDay(day)"
      >
        <span :class="['day-num', { 'day-num-today': day.isToday }]">{{ day.date }}</span>
        <template v-if="day.hasOutfit && day.currentMonth">
          <img v-if="day.thumbnailUrl" :src="day.thumbnailUrl" class="day-thumb" />
          <div v-else class="day-dot" />
        </template>
      </div>
    </div>

    <!-- Floating detail drawer -->
    <Transition name="drawer">
      <div v-if="selectedDay?.currentMonth" class="detail-drawer">
        <div class="drawer-handle" @click="selectedDay = null">
          <span class="drawer-handle-bar"></span>
        </div>
        <div v-if="selectedDay?.outfit" class="drawer-content">
          <span class="drawer-date">{{ selectedDay.fullDate }}</span>
          <div class="drawer-items">
            <img
              v-for="(g, i) in (selectedDay.outfit.garments || [])"
              :key="i"
              :src="getGarmentImg(g)"
              class="drawer-item-img"
            />
          </div>
          <span v-if="selectedDay.outfit.weather" class="drawer-weather">
            {{ selectedDay.outfit.weather }} {{ selectedDay.outfit.temperature }}℃
          </span>
          <span v-if="selectedDay.outfit.reason" class="drawer-reason">{{ selectedDay.outfit.reason }}</span>
        </div>
        <div v-else class="drawer-empty">
          <span class="drawer-date">{{ selectedDay.fullDate }}</span>
          <span class="drawer-empty-text">这天还没有穿搭记录</span>
          <n-button type="primary" size="small" class="record-btn" @click="goToRecommend">
            记录今日穿搭
          </n-button>
        </div>
      </div>
    </Transition>

    <!-- Illustration modal -->
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
        <p v-if="selectedDay.outfit.reason" class="outfit-reason">{{ selectedDay.outfit.reason }}</p>
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
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ColorWandOutline } from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()
const router = useRouter()
const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const weekdays = ['一', '二', '三', '四', '五', '六', '日']
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
  selectedDay.value = null
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
  let startDay = first.getDay() - 1
  if (startDay < 0) startDay = 6
  const daysInMonth = new Date(year.value, month.value, 0).getDate()
  const prevDays = new Date(year.value, month.value - 1, 0).getDate()
  const todayStr = new Date().toISOString().split('T')[0]
  const days = []

  for (let i = startDay - 1; i >= 0; i--) {
    days.push({ date: prevDays - i, currentMonth: false, isToday: false, hasOutfit: false, isWeekend: false })
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const ds = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const outfitData = outfits.value[ds]
    const dayOfWeek = new Date(year.value, month.value - 1, d).getDay()
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
    days.push({
      date: d,
      currentMonth: true,
      isToday: ds === todayStr,
      hasOutfit: !!outfitData,
      thumbnailUrl: outfitData?.garments?.[0] ? getGarmentImg(outfitData.garments[0]) : '',
      illustrationUrl: getIllustrationUrl(outfitData?.illustration_url),
      fullDate: ds,
      outfit: outfitData,
      isWeekend,
    })
  }

  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ date: d, currentMonth: false, isToday: false, hasOutfit: false, isWeekend: false })
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
}

function goToRecommend() {
  router.push('/recommend')
}

function generateToday() {
  router.push('/recommend')
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
  position: relative;
  min-height: calc(100vh - 56px - 72px - 36px);
  padding-bottom: 20px;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ── Header ── */
.page-header {
  margin-bottom: 16px;
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

/* ── Month header ── */
.month-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.month-nav-btn {
  font-size: 16px;
  color: #8C8478;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s ease;
  user-select: none;
}

.month-nav-btn:hover {
  color: #A0815A;
}

.month-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2E2A23;
}

.gen-today-btn {
  margin-left: auto;
  background: #A0815A !important;
  border-color: #A0815A !important;
  font-family: 'Noto Serif SC', serif;
}

/* ── Weekday row ── */
.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  height: 28px;
  align-items: center;
  margin-bottom: 4px;
}

.weekday-cell {
  font-size: 13px;
  font-weight: 500;
  color: #8C8478;
}

/* ── Calendar grid — 正方形格子 ── */
.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 6px;
}

.day-cell {
  aspect-ratio: 1;
  border-radius: 6px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #FFFDF8;
  border: 1px solid #E0D8CC;
  position: relative;
  min-height: 0;
}

.day-cell:hover:not(.other) {
  background: rgba(160, 129, 90, 0.04);
}

.day-cell.other {
  opacity: 0.15;
  cursor: default;
}

.day-cell.today {
  background: rgba(160, 129, 90, 0.08);
}

.day-cell.selected {
  border-left: 2px solid #A0815A;
  background: rgba(160, 129, 90, 0.06);
}

.day-cell.weekend .day-num {
  color: #C27C4E;
}

.day-num {
  font-size: 14px;
  font-weight: 500;
  color: #2E2A23;
  align-self: flex-end;
  line-height: 1;
}

.day-num-today {
  color: #A0815A;
  font-weight: 700;
}

.day-thumb {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid #E0D8CC;
}

.day-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #C27C4E;
}

/* ── Floating detail drawer ── */
.detail-drawer {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: min(90%, 700px);
  background: rgba(245, 240, 232, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid #E0D8CC;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  padding: 8px 24px 16px;
  z-index: 100;
  box-shadow: 0 -4px 24px rgba(46, 42, 35, 0.08);
}

.drawer-handle {
  display: flex;
  justify-content: center;
  padding: 4px 0 8px;
  cursor: pointer;
}

.drawer-handle-bar {
  width: 40px;
  height: 3px;
  border-radius: 2px;
  background: #D0C8BC;
}

.drawer-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.drawer-date {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
  color: #2E2A23;
  flex-shrink: 0;
}

.drawer-items {
  display: flex;
  gap: 8px;
  flex: 1;
}

.drawer-item-img {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid #E0D8CC;
}

.drawer-weather {
  font-size: 12px;
  color: #8C8478;
  background: #FFFDF8;
  padding: 4px 10px;
  border-radius: 4px;
  flex-shrink: 0;
}

.drawer-reason {
  font-size: 12px;
  color: #8C8478;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drawer-empty {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-empty-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 13px;
  color: #8C8478;
}

.record-btn {
  margin-left: auto;
  background: #A0815A !important;
  border-color: #A0815A !important;
  font-family: 'Noto Serif SC', serif;
}

/* Drawer transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(-50%) translateY(100%);
  opacity: 0;
}

.drawer-enter-to,
.drawer-leave-from {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}

/* ── Modal styles ── */
.illust-display {
  text-align: center;
  margin-bottom: 16px;
}

.illust-img {
  max-width: 100%;
  border-radius: 8px;
}

.illust-generate {
  text-align: center;
  margin-bottom: 16px;
}

.generate-btn {
  background: #A0815A !important;
  border-color: #A0815A !important;
}

.modal-garment-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.modal-garment-item {
  text-align: center;
}

.modal-garment-img {
  width: 56px;
  height: 56px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid #E0D8CC;
}

.modal-garment-cat {
  display: block;
  font-size: 11px;
  color: #8C8478;
  margin-top: 4px;
}

.weather-row {
  margin-bottom: 8px;
}

.weather-tag {
  font-size: 12px;
  color: #8C8478;
  background: #F5F0E8;
  padding: 4px 10px;
  border-radius: 4px;
}

.outfit-reason {
  font-size: 13px;
  color: #8C8478;
  line-height: 1.6;
}

.modal-empty {
  text-align: center;
  padding: 24px;
}

.modal-empty-text {
  font-family: 'Noto Serif SC', serif;
  color: #8C8478;
}
</style>
