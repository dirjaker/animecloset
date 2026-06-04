<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2>个人中心</h2>
        <p class="page-subtitle">你的衣橱数据概览</p>
      </div>
    </div>

    <!-- 用户卡片 -->
    <n-card class="user-card" :bordered="false">
      <div class="user-card-inner">
        <div class="avatar-ring">
          <n-avatar :size="56" round :style="{ background: 'linear-gradient(135deg, #D4884A 0%, #E8A060 100%)', fontSize: '24px', fontWeight: '600' }">
            {{ user?.nickname?.charAt(0) || '?' }}
          </n-avatar>
        </div>
        <div class="user-info">
          <p class="user-name">{{ user?.nickname || user?.email || '用户' }}</p>
          <p class="user-email">{{ user?.email }}</p>
        </div>
      </div>
    </n-card>

    <!-- 统计概览 - 3列并排 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-amber">
          <n-icon :component="ShirtOutline" :size="20" />
        </div>
        <p class="stat-num">{{ stats?.total_garments || 0 }}</p>
        <p class="stat-label">衣物总数</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-green">
          <n-icon :component="CalendarOutline" :size="20" />
        </div>
        <p class="stat-num">{{ stats?.total_outfits || 0 }}</p>
        <p class="stat-label">穿搭记录</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap stat-icon-brown">
          <n-icon :component="HeartOutline" :size="20" />
        </div>
        <p class="stat-num">{{ stats?.total_wears || 0 }}</p>
        <p class="stat-label">总穿着次数</p>
      </div>
    </div>

    <!-- AI 插画说明 -->
    <n-card class="ai-card" :bordered="false">
      <div class="ai-card-inner">
        <div class="ai-icon-wrap">
          <n-icon :component="SparklesOutline" :size="22" color="#fff" />
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
          <n-icon :component="TrophyOutline" :size="18" color="#D4884A" />
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
          <n-icon :component="ShirtOutline" :size="32" color="#E5E7EB" />
          <p class="empty-inline-text">暂无数据</p>
          <p class="empty-inline-sub">穿着记录会出现在这里</p>
        </div>
      </n-spin>
    </n-card>

    <!-- 冷宫衣物 -->
    <n-card class="section-card" :bordered="false">
      <template #header>
        <div class="section-header">
          <n-icon :component="SnowOutline" :size="18" color="#6B7280" />
          <span>冷宫衣物</span>
        </div>
      </template>
      <n-spin :show="coldLoading">
        <div v-if="coldItems.length" class="cold-grid">
          <div v-for="item in coldItems" :key="item.id" class="cold-item">
            <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="cold-img" />
            <div class="cold-info">
              <n-tag size="tiny" :bordered="false" round style="background: #F3F4F6; color: #6B7280;">
                {{ item.category }}
              </n-tag>
              <span v-if="item.last_wear_date" class="cold-days">{{ item.days_since }}天未穿</span>
              <span v-else class="cold-days">从未穿过</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-inline">
          <n-icon :component="CheckmarkCircleOutline" :size="32" color="#10B981" />
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
  animation: pageEnter 0.25s ease;
}

@keyframes pageEnter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ─── Page header ─── */
.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1F2937;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 14px;
  color: #9CA3AF;
  margin-top: 6px;
}

/* ─── User card ─── */
.user-card {
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 6px 16px rgba(0,0,0,0.03);
  border: 1px solid #F0EFEC;
  margin-bottom: 24px;
  border-radius: 16px;
}

.user-card-inner {
  display: flex;
  align-items: center;
  gap: 18px;
}

.avatar-ring {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FDF4EC 0%, #FCEEE0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(212, 136, 74, 0.12);
}

.user-name {
  font-size: 18px;
  font-weight: 700;
  color: #1F2937;
}

.user-email {
  font-size: 13px;
  color: #9CA3AF;
  margin-top: 4px;
}

/* ─── Stats row ─── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px 20px;
  text-align: center;
  border: 1px solid #F0EFEC;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 6px 16px rgba(0,0,0,0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.04);
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.stat-icon-amber {
  background: linear-gradient(135deg, #FDF4EC 0%, #FCEEE0 100%);
  color: #D4884A;
}

.stat-icon-green {
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  color: #10B981;
}

.stat-icon-brown {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  color: #92400E;
}

.stat-num {
  font-size: 36px;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.1;
}

.stat-label {
  font-size: 13px;
  color: #9CA3AF;
  margin-top: 6px;
  font-weight: 500;
}

/* ─── AI card ─── */
.ai-card {
  background: linear-gradient(135deg, #D4884A 0%, #E8A060 100%);
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(212, 136, 74, 0.2);
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
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  backdrop-filter: blur(8px);
}

.ai-title {
  font-size: 17px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.ai-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  line-height: 1.6;
}

/* ─── Section cards ─── */
.section-card {
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 6px 16px rgba(0,0,0,0.03);
  border: 1px solid #F0EFEC;
  margin-bottom: 20px;
  border-radius: 16px;
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
  font-size: 16px;
  font-weight: 600;
  color: #1F2937;
}

/* ─── Ranking ─── */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: #FAFAF8;
  border-radius: 12px;
  transition: background 0.2s ease, transform 0.15s ease;
}

.ranking-item:hover {
  background: #F3F4F6;
  transform: translateX(2px);
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: #F3F4F6;
  color: #6B7280;
  flex-shrink: 0;
}

.rank-0 {
  background: linear-gradient(135deg, #FDF4EC 0%, #FCEEE0 100%);
  color: #D4884A;
  box-shadow: 0 2px 6px rgba(212, 136, 74, 0.15);
}

.rank-1 {
  background: #F3F4F6;
  color: #6B7280;
}

.rank-2 {
  background: #F3F4F6;
  color: #9CA3AF;
}

.ranking-img {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid #F0EFEC;
}

.ranking-info {
  flex: 1;
}

.ranking-cat {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.ranking-count {
  font-size: 15px;
  font-weight: 700;
  color: #D4884A;
}

/* ─── Cold items ─── */
.cold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
}

.cold-item {
  background: #FAFAF8;
  border-radius: 14px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #F0EFEC;
}

.cold-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
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
}

.cold-days {
  font-size: 12px;
  color: #9CA3AF;
}

/* ─── Empty state ─── */
.empty-inline {
  text-align: center;
  padding: 36px 0;
}

.empty-inline-text {
  font-size: 14px;
  color: #6B7280;
  margin-top: 12px;
  font-weight: 500;
}

.empty-inline-sub {
  font-size: 12px;
  color: #9CA3AF;
  margin-top: 4px;
}

/* ─── Responsive ─── */
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

  .stat-icon-wrap {
    width: 36px;
    height: 36px;
    margin-bottom: 10px;
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
