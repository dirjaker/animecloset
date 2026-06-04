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
        <div v-if="day.hasOutfit && day.currentMonth" class="avatar-mini-wrap">
          <AvatarCanvas
            :width="40"
            :height="60"
            :avatar-config="defaultAvatar"
            :garments="day.outfit?.garments || []"
          />
        </div>
        <div v-else-if="day.currentMonth" class="avatar-mini-wrap avatar-mini-empty">
          <AvatarCanvas
            :width="40"
            :height="60"
            :avatar-config="defaultAvatar"
            :garments="[]"
          />
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
import AvatarCanvas from '../components/AvatarCanvas.vue'

// 默认头像配置（日历预览用）
const defaultAvatar = ref({ hair_id: 1, skin_id: 1, eye_id: 'brown', body_id: 'medium' })

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
.cal-header h2 { font-size: 18px; color: #8B6914; font-weight: 700; }
.nav-btn {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid #D4A574; background: linear-gradient(135deg, #FFF5EB, #FFF8F0);
  font-size: 18px; cursor: pointer; color: #8B6914;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(139, 105, 20, 0.08);
  transition: all 0.2s;
}
.nav-btn:hover { background: linear-gradient(135deg, #D4A574, #C17A3A); color: #fff; }

.weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr);
  text-align: center; font-size: 13px; color: #C17A3A;
  font-weight: 600; margin-bottom: 8px;
}

.cal-grid {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1; border-radius: 10px; padding: 4px;
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; cursor: pointer; transition: all 0.2s;
  background: #FFF5EB; position: relative;
  box-shadow: 0 1px 4px rgba(139, 105, 20, 0.08);
}
.day-cell:hover { background: #FFEDD5; }
.day-cell.other { opacity: 0.3; cursor: default; }
.day-cell.today {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: #fff; box-shadow: 0 2px 8px rgba(193, 122, 58, 0.3);
}
.day-cell.today .day-num { color: #fff; }
.day-cell.hasOutfit { border: 2px solid #5B7C50; position: relative; }
.day-cell.hasOutfit::after {
  content: '';
  position: absolute; bottom: 6px; right: 6px;
  width: 8px; height: 8px; border-radius: 50%;
  background: #5B7C50;
  box-shadow: 0 1px 3px rgba(91, 124, 80, 0.4);
}

.day-num { font-size: 14px; font-weight: 500; color: #4A3728; }

.avatar-mini-wrap {
  margin-top: 2px;
  display: flex;
  justify-content: center;
}
.avatar-mini-wrap :deep(canvas) {
  width: 40px !important;
  height: 60px !important;
}
.avatar-mini-empty {
  opacity: 0.35;
}

.modal-overlay {
  position: fixed; inset: 0; background: rgba(74, 55, 40, 0.45);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 200;
}
.modal {
  background: #FFF5EB; border-radius: 20px 20px 0 0;
  width: 100%; max-width: 500px; max-height: 70vh;
  overflow-y: auto; padding: 24px;
  border-top: 3px solid #D4A574;
  box-shadow: 0 -4px 20px rgba(139, 105, 20, 0.12);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
}
.modal-header h3 { color: #8B6914; font-size: 16px; font-weight: 700; }
.close-btn {
  width: 32px; height: 32px; border-radius: 8px; border: 2px solid #D4A574;
  background: linear-gradient(135deg, #FFF8F0, #FFF5EB);
  font-size: 18px; cursor: pointer; color: #8B6914;
  transition: all 0.2s;
}
.close-btn:hover { background: linear-gradient(135deg, #D4A574, #C17A3A); color: #fff; }

.outfit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.outfit-item { text-align: center; }
.outfit-img {
  width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 10px;
  box-shadow: 0 2px 8px rgba(139, 105, 20, 0.1);
}
.outfit-cat { font-size: 12px; color: #8B6914; display: block; margin-top: 4px; font-weight: 500; }

.no-outfit { text-align: center; padding: 32px; color: #C17A3A; }
</style>
