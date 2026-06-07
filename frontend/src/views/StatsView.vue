<template>
  <div class="stats-page">
    <div class="page-header">
      <div>
        <h2>穿搭统计</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="metrics-row">
      <div class="metric-card glass-card">
        <n-statistic label="衣物总数" :value="monthlyStats?.total_garments || 0" />
      </div>
      <div class="metric-card glass-card">
        <n-statistic label="总穿着次数" :value="monthlyStats?.total_wears || 0" />
      </div>
      <div class="metric-card glass-card">
        <n-statistic label="收藏衣物" :value="monthlyStats?.favorite_count || 0" />
      </div>
    </div>

    <!-- Monthly Wear Trend -->
    <div class="section-card glass-card">
      <div class="section-header">
        <span>本月穿着趋势</span>
      </div>
      <div v-if="trendLoading" class="loading-area">
        <n-spin size="small" />
      </div>
      <div v-else-if="wearTrend.length" class="bar-chart">
        <div
          v-for="day in wearTrend"
          :key="day.date"
          class="bar-col"
        >
          <div class="bar-tooltip">{{ day.count }}</div>
          <div
            class="bar-fill"
            :style="{ height: barHeight(day.count) + '%' }"
          ></div>
          <div class="bar-label">{{ dayLabel(day.date) }}</div>
        </div>
      </div>
      <div v-else class="empty-inline">
        <p class="empty-inline-text">暂无数据</p>
      </div>
    </div>

    <div class="two-col-row">
      <!-- Category Distribution -->
      <div class="section-card glass-card">
        <div class="section-header">
          <span>分类分布</span>
        </div>
        <div v-if="categoryLoading" class="loading-area">
          <n-spin size="small" />
        </div>
        <div v-else-if="categoryDist.length" class="pie-chart-wrap">
          <div class="pie-chart">
            <div class="pie-bg" :style="{ background: pieGradient }"></div>
            <div class="pie-center">
              <span class="pie-total">{{ totalCategory }}</span>
              <span class="pie-label">件</span>
            </div>
          </div>
          <div class="pie-legend">
            <div v-for="(cat, i) in categoryDist" :key="cat.category" class="legend-item">
              <span class="legend-dot" :style="{ background: pieColors[i % pieColors.length] }"></span>
              <span class="legend-text">{{ categoryLabel(cat.category) }}</span>
              <span class="legend-count">{{ cat.count }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-inline">
          <p class="empty-inline-text">暂无数据</p>
        </div>
      </div>

      <!-- Season Distribution -->
      <div class="section-card glass-card">
        <div class="section-header">
          <span>季节分布</span>
        </div>
        <div v-if="seasonLoading" class="loading-area">
          <n-spin size="small" />
        </div>
        <div v-else-if="seasonDist.length" class="season-bars">
          <div v-for="s in seasonDist" :key="s.season" class="season-row">
            <span class="season-name">{{ seasonLabel(s.season) }}</span>
            <div class="season-bar-track">
              <div
                class="season-bar-fill"
                :style="{ width: seasonPercent(s.count) + '%' }"
              ></div>
            </div>
            <span class="season-count">{{ s.count }}</span>
          </div>
        </div>
        <div v-else class="empty-inline">
          <p class="empty-inline-text">暂无数据</p>
        </div>
      </div>
    </div>

    <!-- Cost Per Wear -->
    <div class="section-card glass-card">
      <div class="section-header">
        <span>单次穿着成本排行</span>
      </div>
      <div v-if="costLoading" class="loading-area">
        <n-spin size="small" />
      </div>
      <div v-else-if="costPerWear.length" class="cost-table">
        <div class="cost-header-row">
          <span class="cost-rank">#</span>
          <span class="cost-cat">类别</span>
          <span class="cost-price">购入价</span>
          <span class="cost-wears">穿着次数</span>
          <span class="cost-cpw">单次成本</span>
        </div>
        <div v-for="(item, i) in costPerWear" :key="item.id || i" class="cost-row">
          <span :class="['cost-rank', `rank-${i}`]">{{ i + 1 }}</span>
          <span class="cost-cat">{{ categoryLabel(item.category) }}</span>
          <span class="cost-price">¥{{ (item.purchase_price || 0).toFixed(0) }}</span>
          <span class="cost-wears">{{ item.wear_count || 0 }}</span>
          <span class="cost-cpw">¥{{ calcCostPerWear(item) }}</span>
        </div>
      </div>
      <div v-else class="empty-inline">
        <p class="empty-inline-text">暂无数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { NStatistic, NSpin, NEmpty } from 'naive-ui'
import api from '../api/index.js'

const categoryMap = { top: '上衣', bottom: '下装', outer: '外套', shoes: '鞋', accessory: '配饰' }
const categoryLabel = (c) => categoryMap[c] || c
const seasonMap = { spring: '春季', summer: '夏季', autumn: '秋季', winter: '冬季' }
const seasonLabel = (s) => seasonMap[s] || s || '未知'

const pieColors = ['#5A5048', '#C8A09B', '#8C8478', '#A09080', '#D4B8B4', '#70645A']

const monthlyStats = ref(null)
const wearTrend = ref([])
const categoryDist = ref([])
const seasonDist = ref([])
const costPerWear = ref([])

const trendLoading = ref(false)
const categoryLoading = ref(false)
const seasonLoading = ref(false)
const costLoading = ref(false)

const totalCategory = computed(() => categoryDist.value.reduce((s, c) => s + c.count, 0))
const maxSeason = computed(() => Math.max(...seasonDist.value.map((s) => s.count), 1))
const maxTrend = computed(() => Math.max(...wearTrend.value.map((d) => d.count), 1))

const pieGradient = computed(() => {
  if (!categoryDist.value.length || !totalCategory.value) return 'none'
  let offset = 0
  const stops = categoryDist.value.map((cat, i) => {
    const pct = (cat.count / totalCategory.value) * 100
    const color = pieColors[i % pieColors.length]
    const seg = `${color} ${offset}% ${offset + pct}%`
    offset += pct
    return seg
  })
  return `conic-gradient(${stops.join(', ')})`
})

function barHeight(count) {
  return Math.max((count / maxTrend.value) * 100, 4)
}

function dayLabel(date) {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function seasonPercent(count) {
  return (count / maxSeason.value) * 100
}

function calcCostPerWear(item) {
  const price = item.purchase_price || 0
  const wears = item.wear_count || 0
  if (!wears) return '-'
  return (price / wears).toFixed(1)
}

async function loadAll() {
  trendLoading.value = true
  try {
    const { data } = await api.get('/stats/monthly')
    monthlyStats.value = data
  } catch {} finally { trendLoading.value = false }

  trendLoading.value = true
  try {
    const { data } = await api.get('/stats/wear-trend')
    wearTrend.value = data.items || data.trend || data || []
  } catch {} finally { trendLoading.value = false }

  categoryLoading.value = true
  try {
    const { data } = await api.get('/stats/category-distribution')
    categoryDist.value = data.items || data.distribution || data || []
  } catch {} finally { categoryLoading.value = false }

  seasonLoading.value = true
  try {
    const { data } = await api.get('/stats/season-distribution')
    seasonDist.value = data.items || data.distribution || data || []
  } catch {} finally { seasonLoading.value = false }

  costLoading.value = true
  try {
    const { data } = await api.get('/stats/cost-per-wear')
    costPerWear.value = data.items || data.ranking || data || []
  } catch {} finally { costLoading.value = false }
}

onMounted(() => loadAll())
</script>

<style scoped>
.stats-page {
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

/* Metrics */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  padding: 24px;
  text-align: center;
}

/* Section card */
.section-card {
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #2E2A23;
  margin-bottom: 20px;
}

.loading-area {
  text-align: center;
  padding: 40px 0;
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

/* Bar chart */
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 180px;
  padding-top: 20px;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  position: relative;
}

.bar-fill {
  width: 100%;
  max-width: 24px;
  background: linear-gradient(180deg, #C8A09B, #5A5048);
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
  min-height: 4px;
}

.bar-tooltip {
  position: absolute;
  top: 0;
  font-size: 10px;
  color: #5A5048;
  font-weight: 600;
}

.bar-label {
  font-size: 10px;
  color: #8C8478;
  margin-top: 6px;
  white-space: nowrap;
}

/* Two col row */
.two-col-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

/* Pie chart */
.pie-chart-wrap {
  display: flex;
  align-items: center;
  gap: 24px;
}

.pie-chart {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  position: relative;
  flex-shrink: 0;
}

.pie-bg {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(255, 253, 248, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pie-total {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 700;
  color: #2E2A23;
  line-height: 1;
}

.pie-label {
  font-size: 11px;
  color: #8C8478;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-text {
  font-size: 13px;
  color: #5A5048;
  flex: 1;
}

.legend-count {
  font-size: 13px;
  font-weight: 600;
  color: #2E2A23;
}

/* Season bars */
.season-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.season-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.season-name {
  width: 40px;
  font-size: 13px;
  color: #5A5048;
  font-weight: 500;
  flex-shrink: 0;
}

.season-bar-track {
  flex: 1;
  height: 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.season-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #C8A09B, #5A5048);
  border-radius: 4px;
  transition: width 0.4s ease;
}

.season-count {
  width: 30px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #2E2A23;
}

/* Cost table */
.cost-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cost-header-row {
  display: grid;
  grid-template-columns: 40px 1fr 80px 80px 80px;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  color: #8C8478;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.cost-row {
  display: grid;
  grid-template-columns: 40px 1fr 80px 80px 80px;
  gap: 8px;
  padding: 10px 12px;
  align-items: center;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.cost-row:hover {
  background: rgba(255, 255, 255, 0.2);
}

.cost-rank {
  font-size: 14px;
  font-weight: 700;
  color: #8C8478;
  text-align: center;
}

.cost-rank.rank-0 {
  color: #5A5048;
}

.cost-rank.rank-1 {
  color: #C8A09B;
}

.cost-cat {
  font-size: 13px;
  color: #2E2A23;
}

.cost-price,
.cost-wears,
.cost-cpw {
  font-size: 13px;
  color: #5A5048;
  text-align: right;
}

.cost-cpw {
  font-weight: 600;
  color: #2E2A23;
}

@media (max-width: 768px) {
  .metrics-row {
    grid-template-columns: 1fr;
  }

  .two-col-row {
    grid-template-columns: 1fr;
  }

  .pie-chart-wrap {
    flex-direction: column;
    align-items: center;
  }

  .bar-chart {
    height: 120px;
  }

  .cost-header-row,
  .cost-row {
    grid-template-columns: 30px 1fr 60px 60px 60px;
    font-size: 12px;
  }
}
</style>
