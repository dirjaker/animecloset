<template>
  <div class="profile-page">
    <h2>👤 个人中心</h2>

    <div class="user-card">
      <div class="avatar-section">
        <div class="avatar-placeholder" :style="{ background: avatarBg }">
          {{ user?.nickname?.charAt(0) || '?' }}
        </div>
        <h3>{{ user?.nickname || user?.email || '用户' }}</h3>
        <p class="email">{{ user?.email }}</p>
      </div>
    </div>

    <div class="avatar-config">
      <h3>🎨 虚拟形象配置</h3>

      <!-- 实时预览画布 -->
      <div class="avatar-preview-section">
        <AvatarCanvas
          :width="200"
          :height="300"
          :avatar-config="canvasConfig"
          :garments="[]"
        />
      </div>

      <div class="config-group">
        <label>发型</label>
        <div class="option-row">
          <button
            v-for="opt in hairOptions" :key="opt.value"
            :class="['opt-btn', { active: avatar.hair === opt.value }]"
            @click="avatar.hair = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <div class="config-group">
        <label>肤色</label>
        <div class="option-row">
          <button
            v-for="opt in skinOptions" :key="opt.value"
            :class="['opt-btn', { active: avatar.skin === opt.value }]"
            @click="avatar.skin = opt.value"
            :style="opt.color ? { background: opt.color, color: 'white' } : {}"
          >{{ opt.label }}</button>
        </div>
      </div>

      <div class="config-group">
        <label>眼睛颜色</label>
        <div class="option-row">
          <button
            v-for="opt in eyeOptions" :key="opt.value"
            :class="['opt-btn', { active: avatar.eye === opt.value }]"
            @click="avatar.eye = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <div class="config-group">
        <label>体型</label>
        <div class="option-row">
          <button
            v-for="opt in bodyOptions" :key="opt.value"
            :class="['opt-btn', { active: avatar.body === opt.value }]"
            @click="avatar.body = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <button class="btn-primary" @click="saveAvatar" :disabled="saving">
        {{ saving ? '保存中...' : '💾 保存形象' }}
      </button>
    </div>

    <!-- 统计仪表盘 -->
    <div class="stats-section">
      <h3>📊 衣橱统计</h3>

      <!-- 衣橱概览 -->
      <div class="stats-card">
        <h4>👗 衣橱概览</h4>
        <div v-if="statsLoading" class="stats-loading">加载中...</div>
        <div v-else-if="wardrobeStats" class="stats-overview">
          <div class="stat-item">
            <span class="stat-num">{{ wardrobeStats.total || 0 }}</span>
            <span class="stat-label">衣物总数</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ wardrobeStats.total_wears || 0 }}</span>
            <span class="stat-label">累计穿着</span>
          </div>
          <div class="category-breakdown" v-if="wardrobeStats.by_category && Object.keys(wardrobeStats.by_category).length">
            <span class="stat-label">分类:</span>
            <span v-for="(count, cat) in wardrobeStats.by_category" :key="cat" class="cat-stat-badge">
              {{ cat }} {{ count }}
            </span>
          </div>
        </div>
        <div v-else class="stats-empty">暂无数据~</div>
      </div>

      <!-- 穿着排行榜 -->
      <div class="stats-card">
        <h4>🏆 穿着排行榜 TOP5</h4>
        <div v-if="statsLoading" class="stats-loading">加载中...</div>
        <div v-else-if="wearRanking.length" class="ranking-list">
          <div v-for="(item, idx) in wearRanking" :key="item.id" class="ranking-item">
            <span class="rank-num">{{ idx + 1 }}</span>
            <img v-if="item.image_url || item.thumbnail_url" :src="item.image_url || item.thumbnail_url" class="rank-thumb" />
            <div class="rank-info">
              <span class="cat-badge">{{ item.category }}</span>
              <div class="rank-tags" v-if="item.tags?.length">
                <span v-for="t in item.tags.slice(0, 3)" :key="t" class="tag">{{ t }}</span>
              </div>
            </div>
            <span class="wear-count">{{ item.wear_count }} 次</span>
          </div>
        </div>
        <div v-else class="stats-empty">还没有穿着记录哦~</div>
      </div>

      <!-- 冷宫衣物 -->
      <div class="stats-card cold-palace-card">
        <h4>❄️ 冷宫衣物</h4>
        <div v-if="statsLoading" class="stats-loading">加载中...</div>
        <div v-else-if="coldPalaceItems.length">
          <p class="cold-palace-desc">以下衣物已经 {{ coldPalaceDays }} 天没有被宠幸了~</p>
          <div class="cold-palace-list">
            <div v-for="item in coldPalaceItems" :key="item.id" class="cold-item">
              <img v-if="item.image_url || item.thumbnail_url" :src="item.image_url || item.thumbnail_url" class="cold-thumb" />
              <div class="cold-info">
                <span class="cat-badge">{{ item.category }}</span>
                <span class="days-badge">{{ item.days_since }} 天未穿</span>
                <div class="rank-tags" v-if="item.tags?.length">
                  <span v-for="t in item.tags.slice(0, 3)" :key="t" class="tag">{{ t }}</span>
                </div>
              </div>
              <button class="btn-wear-today" @click="wearToday(item)">今天穿它</button>
            </div>
          </div>
        </div>
        <div v-else class="stats-empty">没有冷宫衣物，太棒了！🎉</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api/index.js'
import { getWardrobeStats, getWearRanking, getColdPalace } from '../api/index.js'
import { authStore } from '../stores/auth.js'
import AvatarCanvas from '../components/AvatarCanvas.vue'
import { useRouter } from 'vue-router'

// 将 profile 的 avatar 选项转换为 canvas 配置
const hairIdMap = { short: 1, long: 2, twintail: 3, ponytail: 4, bob: 5 }
const skinIdMap = { light: 1, medium: 2, tan: 3, dark: 4 }
const eyeIdMap = { brown: 'brown', blue: 'blue', green: 'green', purple: 'purple', red: 'red' }

const canvasConfig = computed(() => ({
  hair_id: hairIdMap[avatar.hair] || 1,
  skin_id: skinIdMap[avatar.skin] || 1,
  eye_id: eyeIdMap[avatar.eye] || 'brown',
  body_id: avatar.body || 'medium',
}))

const user = ref(null)
const saving = ref(false)

const avatar = reactive({
  hair: 'short',
  skin: 'light',
  eye: 'brown',
  body: 'medium',
})

const hairOptions = [
  { value: 'short', label: '短发' },
  { value: 'long', label: '长发' },
  { value: 'twintail', label: '双马尾' },
  { value: 'ponytail', label: '马尾' },
  { value: 'bob', label: '波波头' },
]

const skinOptions = [
  { value: 'light', label: '白皙' },
  { value: 'medium', label: '自然' },
  { value: 'tan', label: '小麦色' },
  { value: 'dark', label: '深色' },
]

const eyeOptions = [
  { value: 'brown', label: '棕色' },
  { value: 'blue', label: '蓝色' },
  { value: 'green', label: '绿色' },
  { value: 'purple', label: '紫色' },
  { value: 'red', label: '红色' },
]

const bodyOptions = [
  { value: 'slim', label: '纤细' },
  { value: 'medium', label: '标准' },
  { value: 'athletic', label: '运动型' },
]

const avatarBg = computed(() => {
  const colors = { light: '#fde8e8', medium: '#f5d0b0', tan: '#d4a574', dark: '#8d6e63' }
  return colors[avatar.skin] || '#f5d0b0'
})

async function loadProfile() {
  try {
    const { data } = await api.get('/user/me')
    user.value = data
    if (data.avatar) {
      Object.assign(avatar, data.avatar)
    }
  } catch {}
}

async function saveAvatar() {
  saving.value = true
  try {
    await api.put('/user/avatar', { avatar: { ...avatar } })
    alert('形象已保存！')
  } catch { alert('保存失败') }
  finally { saving.value = false }
}

onMounted(() => {
  loadProfile()
  loadStats()
})

// Stats
const router = useRouter()
const statsLoading = ref(false)
const wardrobeStats = ref(null)
const wearRanking = ref([])
const coldPalaceItems = ref([])
const coldPalaceDays = ref(30)

async function loadStats() {
  statsLoading.value = true
  try {
    const [statsRes, rankRes, coldRes] = await Promise.all([
      getWardrobeStats().catch(() => ({ data: null })),
      getWearRanking(5).catch(() => ({ data: { items: [] } })),
      getColdPalace(30).catch(() => ({ data: { items: [] } })),
    ])
    wardrobeStats.value = statsRes.data
    wearRanking.value = rankRes.data?.items || []
    coldPalaceItems.value = coldRes.data?.items || []
    coldPalaceDays.value = coldRes.data?.threshold_days || 30
  } catch {} finally { statsLoading.value = false }
}

function wearToday(item) {
  router.push({ path: '/recommend', query: { prefer_item: item.id } })
}
</script>

<style scoped>
.profile-page h2 { font-size: 20px; color: #8B6914; margin-bottom: 16px; }

.user-card {
  background: linear-gradient(135deg, #5C4033, #8B6914);
  border-radius: 12px; padding: 32px 24px;
  text-align: center; color: white; margin-bottom: 20px;
}

.avatar-placeholder {
  width: 80px; height: 80px; border-radius: 50%;
  margin: 0 auto 12px; display: flex; align-items: center;
  justify-content: center; font-size: 32px; font-weight: 700;
  border: 3px solid #D4A574; color: #4A3728;
}

.user-card h3 { font-size: 18px; margin-bottom: 4px; }
.email { font-size: 13px; opacity: 0.8; }

.avatar-config {
  background: #FFF5EB; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 16px rgba(139, 105, 20, 0.08);
  border: 1px solid #D4A574;
}
.avatar-config h3 { color: #8B6914; font-size: 16px; margin-bottom: 16px; }

.avatar-preview-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #FFF8F0, #FFF5EB);
  border-radius: 12px;
  border: 2px dashed #D4A574;
}

.config-group { margin-bottom: 18px; }
.config-group label { display: block; font-size: 14px; font-weight: 600; color: #4A3728; margin-bottom: 8px; }

.option-row { display: flex; flex-wrap: wrap; gap: 8px; }
.opt-btn {
  padding: 8px 16px; border: 2px solid #D4A574; background: #FFF8F0;
  border-radius: 10px; font-size: 13px; cursor: pointer; transition: all 0.2s;
  color: #4A3728;
}
.opt-btn.active {
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border-color: transparent;
}

.btn-primary {
  margin-top: 8px; width: 100%; padding: 14px;
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border: none; border-radius: 12px;
  font-size: 16px; font-weight: 600; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; }

/* Stats Dashboard */
.stats-section {
  margin-top: 24px;
}
.stats-section h3 { color: #8B6914; font-size: 16px; margin-bottom: 16px; }

.stats-card {
  background: #FFF5EB; border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 16px rgba(139, 105, 20, 0.08);
  margin-bottom: 16px;
  border: 1px solid #D4A574;
}
.stats-card h4 { color: #8B6914; font-size: 15px; margin-bottom: 12px; }
.stats-loading { text-align: center; color: #C17A3A; padding: 20px; }
.stats-empty { text-align: center; color: #8B7355; padding: 20px; font-size: 14px; }

.stats-overview { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
.stat-item { text-align: center; }
.stat-num { display: block; font-size: 28px; font-weight: 700; color: #C17A3A; }
.stat-label { display: block; font-size: 12px; color: #8B7355; margin-top: 2px; }
.category-breakdown { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; width: 100%; }
.cat-stat-badge {
  background: #D4A574; color: white; padding: 3px 10px;
  border-radius: 10px; font-size: 12px; font-weight: 500;
}

.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.ranking-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; background: #FFF8F0; border-radius: 12px;
  border: 1px solid #D4A574;
}
.rank-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; display: flex; align-items: center;
  justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.rank-thumb { width: 44px; height: 44px; border-radius: 10px; object-fit: cover; flex-shrink: 0; }
.rank-info { flex: 1; min-width: 0; }
.rank-tags { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 3px; }
.wear-count { font-size: 14px; font-weight: 700; color: #C17A3A; white-space: nowrap; }

.cold-palace-card { border: 2px solid #D4A574; background: #FFF8F0; }
.cold-palace-desc { font-size: 13px; color: #8B7355; margin-bottom: 12px; }
.cold-palace-list { display: flex; flex-direction: column; gap: 10px; }
.cold-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; background: #FFF5EB; border-radius: 12px;
  box-shadow: 0 1px 4px rgba(139, 105, 20, 0.08);
}
.cold-thumb { width: 44px; height: 44px; border-radius: 10px; object-fit: cover; flex-shrink: 0; }
.cold-info { flex: 1; min-width: 0; }
.days-badge {
  display: inline-block; background: #D4A574; color: white;
  padding: 2px 8px; border-radius: 8px; font-size: 11px; margin-left: 4px;
}
.btn-wear-today {
  padding: 6px 14px; background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: white; border: none; border-radius: 12px;
  font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0;
}
.btn-wear-today:hover { opacity: 0.9; }
</style>
