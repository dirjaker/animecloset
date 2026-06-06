<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2>我的</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- 用户卡片 -->
    <n-card class="user-card" :bordered="false">
      <div class="user-card-inner">
        <div class="avatar-wrap">
          <n-avatar :size="56" round :style="{ background: '#5B7D6A', fontSize: '24px', fontWeight: '600', fontFamily: 'Noto Serif SC, serif' }">
            {{ user?.nickname?.charAt(0) || '?' }}
          </n-avatar>
        </div>
        <div class="user-info">
          <p class="user-name">{{ user?.nickname || user?.email || '用户' }}</p>
          <p class="user-email">{{ user?.email }}</p>
        </div>
      </div>
    </n-card>

    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="stat-card">
        <p class="stat-num">{{ stats?.total_garments || 0 }}</p>
        <p class="stat-label">衣物总数</p>
      </div>
      <div class="stat-card">
        <p class="stat-num">{{ stats?.total_outfits || 0 }}</p>
        <p class="stat-label">穿搭记录</p>
      </div>
      <div class="stat-card">
        <p class="stat-num">{{ stats?.total_wears || 0 }}</p>
        <p class="stat-label">总穿着次数</p>
      </div>
    </div>

    <!-- AI 插画说明 -->
    <n-card class="ai-card" :bordered="false">
      <div class="ai-card-inner">
        <div class="ai-icon-wrap">
          <n-icon :component="SparklesOutline" :size="20" color="#fff" />
        </div>
        <div class="ai-text">
          <p class="ai-title">AI 穿搭插画</p>
          <p class="ai-desc">保存穿搭后，在日历页面点击「生成 AI 穿搭插画」即可生成动漫风格形象</p>
        </div>
      </div>
    </n-card>

    <!-- 穿着最多 -->
    <n-card class="section-card" :bordered="false">
      <template #header>
        <div class="section-header">
          <span>穿着最多</span>
        </div>
      </template>
      <n-spin :show="rankingLoading">
        <div v-if="ranking.length" class="ranking-list">
          <div v-for="(item, i) in ranking" :key="item.id" class="ranking-item">
            <div :class="['rank-badge', `rank-${i}`]">
              {{ i + 1 }}
            </div>
            <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="ranking-img" />
            <div class="ranking-info">
              <span class="ranking-cat">{{ item.category }}</span>
            </div>
            <span class="ranking-count">{{ item.wear_count }}次</span>
          </div>
        </div>
        <div v-else class="empty-inline">
          <p class="empty-inline-text">暂无数据</p>
          <p class="empty-inline-sub">穿着记录会出现在这里</p>
        </div>
      </n-spin>
    </n-card>

    <!-- 冷宫衣物 -->
    <n-card class="section-card" :bordered="false">
      <template #header>
        <div class="section-header">
          <span>冷宫衣物</span>
        </div>
      </template>
      <n-spin :show="coldLoading">
        <div v-if="coldItems.length" class="cold-grid">
          <div v-for="item in coldItems" :key="item.id" class="cold-item">
            <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="cold-img" />
            <div class="cold-info">
              <span class="cold-cat">{{ item.category }}</span>
              <span v-if="item.last_wear_date" class="cold-days">{{ item.days_since }}天未穿</span>
              <span v-else class="cold-days">从未穿过</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-inline">
          <p class="empty-inline-text">没有冷宫衣物，太棒了</p>
          <p class="empty-inline-sub">所有衣物都在正常使用</p>
        </div>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  ShirtOutline,
  SparklesOutline,
  TrophyOutline,
  SnowOutline,
  CheckmarkCircleOutline,
  CalendarOutline,
  HeartOutline,
} from '@vicons/ionicons5'
import { getWardrobeStats, getWearRanking, getColdPalace } from '../api/index.js'
import { authStore } from '../stores/auth.js'

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const user = ref(null)
const stats = ref(null)
const statsLoading = ref(false)
const ranking = ref([])
const rankingLoading = ref(false)
const coldItems = ref([])
const coldLoading = ref(false)

function getImgUrl(item) {
  const url = item.image_url || item.thumbnail_url || item.processed_url
  if (url && url.startsWith('/')) return API_BASE + url
  return url || ''
}

async function loadAll() {
  user.value = authStore.user

  statsLoading.value = true
  try {
    const { data } = await getWardrobeStats()
    stats.value = data
  } catch {} finally { statsLoading.value = false }

  rankingLoading.value = true
  try {
    const { data } = await getWearRanking(5)
    ranking.value = data.items || data.ranking || []
  } catch {} finally { rankingLoading.value = false }

  coldLoading.value = true
  try {
    const { data } = await getColdPalace(30)
    coldItems.value = data.items || []
  } catch {} finally { coldLoading.value = false }
}

onMounted(() => loadAll())
</script>

<style scoped>
.profile-page {
  animation: pageEnter 0.3s ease;
}

@keyframes pageEnter {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Page header */
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

/* User card */
.user-card {
  border: 1px solid #E8E3DA;
  box-shadow: 0 1px 4px rgba(44, 42, 37, 0.04);
  margin-bottom: 24px;
}

.user-card-inner {
  display: flex;
  align-items: center;
  gap: 18px;
}

.avatar-wrap {
  flex-shrink: 0;
}

.user-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: #2C2A25;
}

.user-email {
  font-size: 13px;
  color: #8A8578;
  margin-top: 4px;
}

/* Stats row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #FFFDF9;
  border-radius: 8px;
  padding: 24px 20px;
  text-align: center;
  border: 1px solid #E8E3DA;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #5B7D6A;
}

.stat-num {
  font-family: 'Noto Serif SC', serif;
  font-size: 36px;
  font-weight: 700;
  color: #2C2A25;
  line-height: 1.1;
}

.stat-label {
  font-size: 13px;
  color: #8A8578;
  margin-top: 6px;
  font-weight: 500;
}

/* AI card */
.ai-card {
  background: #5B7D6A;
  border-radius: 8px;
  margin-bottom: 24px;
}

.ai-card :deep(.n-card__content) {
  padding: 24px;
}

.ai-card-inner {
  display: flex;
  align-items: center;
  gap: 18px;
}

.ai-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.ai-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* Section cards */
.section-card {
  border: 1px solid #E8E3DA;
  box-shadow: 0 1px 4px rgba(44, 42, 37, 0.04);
  margin-bottom: 20px;
}

.section-card :deep(.n-card-header) {
  padding: 20px 24px 0;
}

.section-card :deep(.n-card__content) {
  padding: 16px 24px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #2C2A25;
}

/* Ranking */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  background: #F6F3EE;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.ranking-item:hover {
  background: rgba(91, 125, 106, 0.06);
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: #E8E3DA;
  color: #8A8578;
  flex-shrink: 0;
}

.rank-0 {
  background: #5B7D6A;
  color: #FFFFFF;
}

.rank-1 {
  background: #C49A6C;
  color: #FFFFFF;
}

.rank-2 {
  background: #E8E3DA;
  color: #8A8578;
}

.ranking-img {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid #E8E3DA;
}

.ranking-info {
  flex: 1;
}

.ranking-cat {
  font-size: 14px;
  font-weight: 500;
  color: #2C2A25;
}

.ranking-count {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 700;
  color: #5B7D6A;
}

/* Cold items */
.cold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
}

.cold-item {
  background: #FFFDF9;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #E8E3DA;
}

.cold-item:hover {
  border-left: 2px solid #5B7D6A;
}

.cold-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.cold-info {
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid #E8E3DA;
}

.cold-cat {
  font-size: 12px;
  color: #5B7D6A;
  font-weight: 500;
}

.cold-days {
  font-size: 12px;
  color: #8A8578;
}

/* Empty state */
.empty-inline {
  text-align: center;
  padding: 36px 0;
}

.empty-inline-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  color: #8A8578;
  font-weight: 500;
}

.empty-inline-sub {
  font-size: 12px;
  color: #8A8578;
  margin-top: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }

  .stat-card {
    padding: 16px 8px;
  }

  .stat-num {
    font-size: 28px;
  }

  .cold-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .ai-card-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
