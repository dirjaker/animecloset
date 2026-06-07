<template>
  <div class="packing-page">
    <div class="page-header">
      <div>
        <h2>行李清单</h2>
        <div class="page-line"></div>
      </div>
      <n-button type="primary" @click="showCreate = true">
        <template #icon><n-icon :component="AddOutline" /></template>
        新建行程
      </n-button>
    </div>

    <!-- Trip List -->
    <div v-if="loading" class="loading-area">
      <n-spin size="large" />
    </div>

    <div v-else-if="!trips.length" class="empty-state glass-card">
      <n-empty description="暂无行程" :size="48">
        <template #extra>
          <n-button size="small" @click="showCreate = true">创建第一个行程</n-button>
        </template>
      </n-empty>
    </div>

    <div v-else class="trips-list">
      <div
        v-for="trip in trips"
        :key="trip.id"
        class="trip-card glass-card"
      >
        <div class="trip-header" @click="toggleExpand(trip.id)">
          <div class="trip-info">
            <p class="trip-name">{{ trip.name }}</p>
            <p class="trip-meta">
              <span v-if="trip.destination">{{ trip.destination }}</span>
              <span v-if="trip.start_date" class="trip-dates">
                {{ trip.start_date }} ~ {{ trip.end_date }}
              </span>
            </p>
          </div>
          <div class="trip-actions">
            <span class="trip-count">{{ trip.item_count || 0 }} 件</span>
            <n-icon
              :component="expandedId === trip.id ? ChevronUpOutline : ChevronDownOutline"
              :size="18"
            />
          </div>
        </div>

        <!-- Expanded detail -->
        <div v-if="expandedId === trip.id" class="trip-detail">
          <div class="detail-toolbar">
            <n-button
              size="small"
              :loading="autoFilling"
              @click="autoFill(trip.id)"
            >
              <template #icon><n-icon :component="SparklesOutline" /></template>
              AI 填充
            </n-button>
            <n-button
              size="small"
              quaternary
              type="error"
              @click="deleteTrip(trip.id)"
            >
              删除行程
            </n-button>
          </div>

          <div v-if="detailLoading" class="loading-area">
            <n-spin size="small" />
          </div>

          <div v-else-if="tripDetail?.days?.length" class="days-list">
            <div v-for="day in tripDetail.days" :key="day.date" class="day-block">
              <p class="day-label">{{ day.date }}</p>
              <div class="day-garments">
                <div
                  v-for="item in day.items"
                  :key="item.id || item.garment_id"
                  class="day-garment-thumb"
                >
                  <img :src="getImgUrl(item)" :alt="item.category" />
                </div>
                <div v-if="!day.items?.length" class="day-empty">未安排</div>
              </div>
            </div>
          </div>

          <div v-else class="empty-inline">
            <p class="empty-inline-text">暂无搭配安排</p>
            <p class="empty-inline-sub">点击「AI 填充」自动生成</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <n-modal v-model:show="showCreate" preset="card" title="新建行程" style="max-width: 440px">
      <n-form ref="formRef" :model="form" label-placement="left" label-width="70">
        <n-form-item label="行程名称" path="name">
          <n-input v-model:value="form.name" placeholder="如：国庆出游" />
        </n-form-item>
        <n-form-item label="目的地" path="destination">
          <n-input v-model:value="form.destination" placeholder="如：东京" />
        </n-form-item>
        <n-form-item label="开始日期" path="start_date">
          <n-date-picker
            v-model:formatted-value="form.start_date"
            type="date"
            value-format="yyyy-MM-dd"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="结束日期" path="end_date">
          <n-date-picker
            v-model:formatted-value="form.end_date"
            type="date"
            value-format="yyyy-MM-dd"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showCreate = false">取消</n-button>
        <n-button type="primary" :loading="creating" @click="createTrip">创建</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  AddOutline,
  ChevronDownOutline,
  ChevronUpOutline,
  SparklesOutline,
} from '@vicons/ionicons5'
import api from '../api/index.js'

const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const getImgUrl = (item) => {
  const url = item.image_url || item.thumbnail_url || item.processed_url
  if (url && url.startsWith('/')) return `${API_BASE}${url}`
  return url || ''
}

const trips = ref([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const form = ref({ name: '', destination: '', start_date: '', end_date: '' })

const expandedId = ref(null)
const tripDetail = ref(null)
const detailLoading = ref(false)
const autoFilling = ref(false)

async function loadTrips() {
  loading.value = true
  try {
    const { data } = await api.get('/packing')
    trips.value = data.items || data.packing_lists || data || []
  } catch {
    trips.value = []
  } finally {
    loading.value = false
  }
}

async function createTrip() {
  if (!form.value.name) {
    message.warning('请输入行程名称')
    return
  }
  creating.value = true
  try {
    await api.post('/packing', form.value)
    message.success('行程已创建')
    showCreate.value = false
    form.value = { name: '', destination: '', start_date: '', end_date: '' }
    await loadTrips()
  } catch {
    message.error('创建失败')
  } finally {
    creating.value = false
  }
}

async function toggleExpand(tripId) {
  if (expandedId.value === tripId) {
    expandedId.value = null
    tripDetail.value = null
    return
  }
  expandedId.value = tripId
  detailLoading.value = true
  tripDetail.value = null
  try {
    const { data } = await api.get(`/packing/${tripId}`)
    tripDetail.value = data
  } catch {
    tripDetail.value = null
  } finally {
    detailLoading.value = false
  }
}

async function autoFill(tripId) {
  autoFilling.value = true
  try {
    const { data } = await api.post(`/packing/${tripId}/auto-fill`)
    tripDetail.value = data
    message.success('AI 填充完成')
    await loadTrips()
  } catch {
    message.error('AI 填充失败')
  } finally {
    autoFilling.value = false
  }
}

async function deleteTrip(tripId) {
  try {
    await api.delete(`/packing/${tripId}`)
    trips.value = trips.value.filter((t) => t.id !== tripId)
    if (expandedId.value === tripId) {
      expandedId.value = null
      tripDetail.value = null
    }
    message.success('已删除')
  } catch {
    message.error('删除失败')
  }
}

onMounted(() => loadTrips())
</script>

<style scoped>
.packing-page {
  animation: pageEnter 0.3s ease;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
  background: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset;
}

.loading-area {
  text-align: center;
  padding: 60px 0;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.trips-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trip-card {
  padding: 0;
  overflow: hidden;
}

.trip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.trip-header:hover {
  background: rgba(255, 255, 255, 0.15);
}

.trip-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #2E2A23;
}

.trip-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 13px;
  color: #8C8478;
}

.trip-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #8C8478;
}

.trip-count {
  font-size: 13px;
  font-weight: 500;
  background: rgba(200, 160, 155, 0.2);
  padding: 2px 10px;
  border-radius: 10px;
}

.trip-detail {
  padding: 0 24px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.detail-toolbar {
  display: flex;
  gap: 10px;
  padding: 16px 0;
}

.days-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.day-block {
  background: rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  padding: 12px;
}

.day-label {
  font-size: 13px;
  font-weight: 600;
  color: #5A5048;
  margin-bottom: 8px;
}

.day-garments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.day-garment-thumb {
  width: 52px;
  height: 52px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.day-garment-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.day-empty {
  font-size: 12px;
  color: #8C8478;
  padding: 8px 0;
}

.empty-inline {
  text-align: center;
  padding: 36px 0;
}

.empty-inline-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  color: #8C8478;
  font-weight: 500;
}

.empty-inline-sub {
  font-size: 12px;
  color: #8C8478;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
  }

  .trip-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
