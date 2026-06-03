<template>
  <div class="calendar-page">
    <div class="cal-header">
      <button class="nav-btn" @click="changeMonth(-1)">‹</button>
      <h2>{{ year }}年{{ month }}月</h2>
      <button class="nav-btn" @click="changeMonth(1)">›</button>
    </div>

    <div class="weekdays">
      <span v-for="d in weekdays" :key="d">{{ d }}</span>
    </div>

    <div class="cal-grid">
      <div
        v-for="(day, i) in calendarDays"
        :key="i"
        :class="['day-cell', { today: day.isToday, other: !day.currentMonth, hasOutfit: day.hasOutfit }]"
        @click="day.currentMonth && openDay(day)"
      >
        <span class="day-num">{{ day.date }}</span>
        <div v-if="day.hasOutfit" class="outfit-dots">
          <span v-for="j in Math.min(day.garmentCount, 3)" :key="j" class="dot"></span>
        </div>
        <div v-if="day.outfitPreviews?.length" class="mini-preview">
          <img v-for="(p, k) in day.outfitPreviews.slice(0,2)" :key="k" :src="p" class="mini-img" />
        </div>
      </div>
    </div>

    <div v-if="selectedDay" class="modal-overlay" @click.self="selectedDay = null">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedDay.fullDate }} 穿搭</h3>
          <button class="close-btn" @click="selectedDay = null">×</button>
        </div>
        <div v-if="selectedDay.outfit" class="outfit-detail">
          <div class="outfit-grid">
            <div v-for="(g, i) in selectedDay.outfit.garments" :key="i" class="outfit-item">
              <img :src="g.image_url || g.thumbnail_url" class="outfit-img" />
              <span class="outfit-cat">{{ g.category }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-outfit">
          <p>这天还没有穿搭记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api/index.js'

const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const outfits = ref({})
const selectedDay = ref(null)

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
      garmentCount: outfitData?.garments?.length || 0,
      outfitPreviews: (outfitData?.garments || []).slice(0, 2).map(g => g.image_url || g.thumbnail_url),
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
    const items = data.outfits || data.calendar || data || []
    if (Array.isArray(items)) {
      items.forEach(o => {
        const key = o.date
        if (key) map[key] = o
      })
    }
    outfits.value = map
  } catch {}
}

function openDay(day) {
  selectedDay.value = day
}

onMounted(() => loadCalendar())
</script>

<style scoped>
.cal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
}
.cal-header h2 { font-size: 18px; color: #7c3aed; }
.nav-btn {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid #e9d5ff; background: white;
  font-size: 18px; cursor: pointer; color: #7c3aed;
  display: flex; align-items: center; justify-content: center;
}

.weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr);
  text-align: center; font-size: 13px; color: #a78bfa;
  font-weight: 600; margin-bottom: 8px;
}

.cal-grid {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1; border-radius: 12px; padding: 4px;
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; cursor: pointer; transition: all 0.2s;
  background: white; position: relative;
}
.day-cell:hover { background: #f3e8ff; }
.day-cell.other { opacity: 0.3; cursor: default; }
.day-cell.today { background: #ede9fe; border: 2px solid #a78bfa; }
.day-cell.hasOutfit { background: #fce7f3; }

.day-num { font-size: 14px; font-weight: 500; }

.outfit-dots { display: flex; gap: 3px; margin-top: 2px; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: #e879f9; }

.mini-preview { display: flex; gap: 2px; margin-top: 2px; }
.mini-img { width: 16px; height: 16px; border-radius: 4px; object-fit: cover; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 200;
}
.modal {
  background: white; border-radius: 24px 24px 0 0;
  width: 100%; max-width: 500px; max-height: 70vh;
  overflow-y: auto; padding: 24px;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
}
.modal-header h3 { color: #7c3aed; font-size: 16px; }
.close-btn {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: #f3e8ff; font-size: 18px; cursor: pointer; color: #7c3aed;
}

.outfit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.outfit-item { text-align: center; }
.outfit-img {
  width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.outfit-cat { font-size: 12px; color: #888; display: block; margin-top: 4px; }

.no-outfit { text-align: center; padding: 32px; color: #aaa; }
</style>
