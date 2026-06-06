<template>
  <div class="calendar-page">
    <div class="cal-top-bar">
      <h2 class="cal-title">穿搭日历</h2>
      <div class="top-right">
        <div class="month-controls">
          <span class="month-nav-btn" @click="changeMonth(-1)">◀</span>
          <span class="month-label">{{ year }}年{{ month }}月</span>
          <span class="month-nav-btn" @click="changeMonth(1)">▶</span>
        </div>
        <n-button type="primary" size="small" class="gen-today-btn" @click="generateToday">
          生成今日推荐
        </n-button>
      </div>
    </div>

    <div class="cal-wrapper">
      <div class="cal-weekday-row">
        <span v-for="d in weekdays" :key="d" class="weekday-cell">{{ d }}</span>
      </div>
      <div class="cal-grid" ref="calGridRef">
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
        <span class="day-num">
          <span v-if="day.isToday" class="day-num-today">{{ day.date }}</span>
          <template v-else>{{ day.date }}</template>
        </span>
        <div v-if="day.hasOutfit && day.currentMonth" class="day-cell-body">
          <img v-if="day.thumbnailUrl" :src="day.thumbnailUrl" class="day-thumb" />
          <div v-else class="day-dot" />
        </div>
      </div>
    </div>
    </div>

    <!-- Floating detail drawer -->
    <Transition name="drawer">
      <div v-if="selectedDay?.currentMonth" class="detail-drawer">
        <div class="drawer-handle" @click="selectedDay = null">
          <span class="drawer-handle-bar"></span>
        </div>
        <button class="drawer-close" @click="selectedDay = null" title="关闭">×</button>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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
const calGridRef = ref(null)

let resizeObserver = null

function updateCellSize() {
  if (!calGridRef.value) return
  const grid = calGridRef.value
  const style = getComputedStyle(grid)
  const paddingTop = parseFloat(style.paddingTop) || 0
  const paddingBottom = parseFloat(style.paddingBottom) || 0
  const gap = parseFloat(style.gap) || parseFloat(style.gridRowGap) || 4
  const rows = 6
  const availableH = grid.clientHeight - paddingTop - paddingBottom - gap * (rows - 1)
  const cellSize = Math.floor(availableH / rows)
  // Set on calendar-page so both inline-weekdays and cal-grid inherit it
  const page = grid.closest('.calendar-page')
  if (page) {
    page.style.setProperty('--cell-size', cellSize + 'px')
  }
}

onMounted(() => {
  loadCalendar()
  nextTick(() => {
    updateCellSize()
    if (calGridRef.value) {
      resizeObserver = new ResizeObserver(updateCellSize)
      resizeObserver.observe(calGridRef.value)
    }
  })
})

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
})

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
  // Toggle: click same day to close
  if (selectedDay.value?.fullDate === day.fullDate) {
    selectedDay.value = null
  } else {
    selectedDay.value = { ...day }
  }
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
</script>

<style scoped>
/* ── Page: fill viewport minus nav, no scroll ── */
.calendar-page {
  animation: pageEnter 0.3s ease;
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  padding: 12px 24px 8px;
  box-sizing: border-box;
  overflow: hidden;
  z-index: 1;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ── Top bar: title + controls in one line ── */
.cal-top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-bottom: 6px;
  min-height: 28px;
}

.cal-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #2E2A23;
  letter-spacing: 1px;
  white-space: nowrap;
  flex-shrink: 0;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  margin-left: auto;
}

.month-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.month-nav-btn {
  font-size: 12px;
  color: #8C8478;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
  user-select: none;
}

.month-nav-btn:hover {
  color: #A0815A;
  background: rgba(160, 129, 90, 0.06);
}

.month-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
  color: #2E2A23;
  min-width: 80px;
  text-align: center;
}

.gen-today-btn {
  background: #A0815A !important;
  border-color: #A0815A !important;
  font-family: 'Noto Serif SC', serif;
  border-radius: 6px !important;
}

/* ── Calendar wrapper: weekday + grid, fills remaining space ── */
.cal-wrapper {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* ── Weekday row: same columns as grid ── */
.cal-weekday-row {
  display: grid;
  grid-template-columns: repeat(7, var(--cell-size, 1fr));
  gap: 4px;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 2px;
}

.weekday-cell {
  font-size: 11px;
  font-weight: 500;
  color: #8C8478;
  letter-spacing: 1px;
  height: 20px;
  line-height: 20px;
  text-align: center;
}

.weekday-cell:nth-child(6),
.weekday-cell:nth-child(7) {
  color: #C27C4E;
}

/* ── Calendar grid: fills remaining height, square cells via JS ── */
.cal-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(7, var(--cell-size, 1fr));
  grid-template-rows: repeat(6, minmax(0, 1fr));
  gap: 4px;
  justify-content: center;
}

.day-cell {
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  padding: 6px 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.18s ease;
  background: #FFFDF8;
  border: 1px solid #E0D8CC;
  position: relative;
  box-sizing: border-box;
}

.day-cell:hover:not(.other) {
  background: rgba(160, 129, 90, 0.05);
  border-color: #C8B99E;
}

.day-cell.other {
  opacity: 0.08;
  cursor: default;
  background: transparent;
  border-color: transparent;
}

.day-cell.today {
  background: rgba(160, 129, 90, 0.06);
  border-color: #A0815A;
}

.day-cell.selected {
  border: 1.5px solid #A0815A;
  background: rgba(160, 129, 90, 0.08);
  box-shadow: 0 1px 4px rgba(160, 129, 90, 0.12);
}

.day-cell.weekend:not(.other) {
  background: rgba(194, 124, 78, 0.03);
}

.day-num {
  font-size: 13px;
  font-weight: 500;
  color: #2E2A23;
  line-height: 1;
  margin-bottom: auto;
}

.day-cell.weekend:not(.other) .day-num {
  color: #C27C4E;
}

.day-num-today {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #A0815A;
  color: #FFFDF8 !important;
  font-size: 11px;
  font-weight: 700;
}

.day-cell-body {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
}

.day-thumb {
  width: 32px;
  height: 32px;
  max-width: 100%;
  max-height: 100%;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid #E0D8CC;
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

.drawer-close {
  position: absolute;
  top: 10px;
  right: 16px;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #8C8478;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.drawer-close:hover {
  color: #A0815A;
  background: rgba(160, 129, 90, 0.08);
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

/* ── Modal ── */
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

/* ── Mobile ── */
@media (max-width: 768px) {
  .calendar-page {
    padding: 12px 16px 8px;
  }

  .day-num {
    font-size: 11px;
  }

  .day-num-today {
    width: 18px;
    height: 18px;
    font-size: 10px;
  }

  .day-thumb {
    width: 24px;
    height: 24px;
  }

  .day-cell {
    padding: 4px 5px;
    border-radius: 4px;
  }
}
</style>
