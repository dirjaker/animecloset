<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2>我的</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- User info + stats side by side -->
    <div class="info-stats-row">
      <div class="user-card">
        <div class="user-card-inner">
          <div class="avatar-wrap">
            <n-avatar :size="56" round :style="{ background: 'var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.45))', backdropFilter: 'blur(12px)', fontSize: '24px', fontWeight: '600', fontFamily: 'Noto Serif SC, serif' }">
              {{ editingNickname ? editingNickname.charAt(0) : (user?.nickname?.charAt(0) || '?') }}
            </n-avatar>
          </div>
          <div class="user-info">
            <!-- 显示模式 -->
            <div v-if="!isEditing" class="user-info-display">
              <p class="user-name">
                {{ user?.nickname || user?.email || '用户' }}
                <n-button text type="primary" size="tiny" @click="startEdit" style="margin-left: 8px;">
                  <template #icon><n-icon :component="CreateOutline" /></template>
                  编辑
                </n-button>
              </p>
              <p class="user-email">{{ user?.email }}</p>
              <p class="user-join-date" v-if="user?.created_at">
                加入于 {{ formatDate(user.created_at) }}
              </p>
            </div>
            <!-- 编辑模式 -->
            <div v-else class="user-info-edit">
              <div class="edit-row">
                <n-input
                  v-model:value="editingNickname"
                  placeholder="请输入昵称"
                  :maxlength="50"
                  size="small"
                  style="flex: 1;"
                />
                <n-button type="primary" size="small" @click="saveNickname" :loading="savingNickname">
                  保存
                </n-button>
                <n-button size="small" @click="cancelEdit">
                  取消
                </n-button>
              </div>
              <p class="user-email">{{ user?.email }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-card">
        <div class="stats-grid">
          <div class="stat-item">
            <p class="stat-num">{{ stats?.total_garments || 0 }}</p>
            <p class="stat-label">衣物总数</p>
          </div>
          <div class="stat-item">
            <p class="stat-num">{{ stats?.total_outfits || 0 }}</p>
            <p class="stat-label">穿搭记录</p>
          </div>
          <div class="stat-item">
            <p class="stat-num">{{ stats?.total_wears || 0 }}</p>
            <p class="stat-label">总穿着次数</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Account actions section -->
    <div class="section-card">
      <div class="section-header">
        <n-icon :component="PersonOutline" :size="18" />
        <span>账户安全</span>
      </div>
      <div class="account-actions">
        <div class="action-item" @click="showPasswordModal = true">
          <div class="action-icon">
            <n-icon :component="LockClosedOutline" :size="20" />
          </div>
          <div class="action-text">
            <p class="action-title">修改密码</p>
            <p class="action-desc">定期更换密码，保护账户安全</p>
          </div>
          <n-icon :component="ChevronForwardOutline" :size="16" class="action-arrow" />
        </div>
      </div>
    </div>

    <!-- AI card -->
    <div class="ai-card">
      <div class="ai-card-inner">
        <div class="ai-icon-wrap">
          <n-icon :component="SparklesOutline" :size="20" color="#fff" />
        </div>
        <div class="ai-text">
          <p class="ai-title">AI 穿搭插画</p>
          <p class="ai-desc">保存穿搭后，在日历页面点击「生成 AI 穿搭插画」即可生成动漫风格形象</p>
        </div>
      </div>
    </div>

    <!-- 穿搭统计 Section -->
    <div class="section-card">
      <div class="section-header">
        <n-icon :component="StatsChartOutline" :size="18" />
        <span>穿搭统计</span>
      </div>
      <div class="quick-stats-grid">
        <div class="quick-stat-item">
          <n-statistic label="本月穿着" :value="profileStats.month_wears || 0" />
        </div>
        <div class="quick-stat-item">
          <n-statistic label="最爱分类" :value="profileStats.favorite_category || '-'" />
        </div>
        <div class="quick-stat-item">
          <n-statistic label="平均单次成本">
            <template #prefix>¥</template>
            {{ profileStats.avg_cost_per_wear || '0.0' }}
          </n-statistic>
        </div>
      </div>
      <div style="text-align: center; margin-top: 16px">
        <n-button quaternary size="small" @click="$router.push('/stats')">
          查看完整统计
          <template #icon><n-icon :component="ChevronForwardOutline" /></template>
        </n-button>
      </div>
    </div>

    <!-- 每日提醒 Section -->
    <div class="section-card">
      <div class="section-header">
        <n-icon :component="NotificationsOutline" :size="18" />
        <span>每日提醒</span>
      </div>
      <div class="reminder-content">
        <div class="reminder-row">
          <div class="reminder-info">
            <p class="reminder-title">开启每日穿搭提醒</p>
            <p class="reminder-desc">每天提醒你记录今日穿搭</p>
          </div>
          <n-switch
            v-model:value="reminderEnabled"
            @update:value="saveReminder"
          />
        </div>
        <div v-if="reminderEnabled" class="reminder-time-row">
          <span class="reminder-time-label">提醒时间</span>
          <n-time-picker
            v-model:formatted-value="reminderTime"
            format="HH:mm"
            style="width: 120px"
            @update:formatted-value="saveReminder"
          />
        </div>
      </div>
    </div>

    <!-- Frequency + Favorites 2-col -->
    <div class="two-col-row">
      <div class="section-card">
        <div class="section-header">
          <span>穿着最多</span>
        </div>
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
      </div>

      <div class="section-card">
        <div class="section-header">
          <span>收藏场景</span>
        </div>
        <div class="empty-inline">
          <p class="empty-inline-text">暂无收藏</p>
          <p class="empty-inline-sub">收藏推荐场景会出现在这里</p>
        </div>
      </div>
    </div>

    <!-- 冷宫衣物 -->
    <div class="section-card">
      <div class="section-header">
        <span>冷宫衣物</span>
      </div>
      <n-spin :show="coldLoading">
        <div v-if="coldItems.length" class="cold-grid">
          <div
            v-for="(item, i) in coldItems"
            :key="item.id"
            :class="['cold-item', getColdSize(i)]"
          >
            <div class="cold-img-wrap">
              <img v-if="getImgUrl(item)" :src="getImgUrl(item)" class="cold-img" />
            </div>
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
    </div>

    <!-- 修改密码弹窗 -->
    <n-modal
      v-model:show="showPasswordModal"
      preset="card"
      title="修改密码"
      :style="{ maxWidth: '420px' }"
      :bordered="false"
      :mask-closable="false"
    >
      <n-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-placement="left"
        label-width="80"
      >
        <n-form-item label="当前密码" path="old_password">
          <n-input
            v-model:value="passwordForm.old_password"
            type="password"
            show-password-on="click"
            placeholder="请输入当前密码"
          />
        </n-form-item>
        <n-form-item label="新密码" path="new_password">
          <n-input
            v-model:value="passwordForm.new_password"
            type="password"
            show-password-on="click"
            placeholder="请输入新密码（至少6位）"
          />
        </n-form-item>
        <n-form-item label="确认密码" path="confirm_password">
          <n-input
            v-model:value="passwordForm.confirm_password"
            type="password"
            show-password-on="click"
            placeholder="请再次输入新密码"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 12px;">
          <n-button @click="showPasswordModal = false">取消</n-button>
          <n-button type="primary" @click="handleChangePassword" :loading="changingPassword">
            确认修改
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  SparklesOutline,
  StatsChartOutline,
  ChevronForwardOutline,
  NotificationsOutline,
  PersonOutline,
  LockClosedOutline,
  CreateOutline,
} from '@vicons/ionicons5'
import { NStatistic, NSwitch, NTimePicker, NInput, NForm, NFormItem, NModal, useMessage } from 'naive-ui'
import { getWardrobeStats, getWearRanking, getColdPalace } from '../api/index.js'
import { authStore } from '../stores/auth.js'
import api from '../api/index.js'

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`
const message = useMessage()

const user = ref(null)
const stats = ref(null)
const statsLoading = ref(false)
const ranking = ref([])
const rankingLoading = ref(false)
const coldItems = ref([])
const coldLoading = ref(false)

const profileStats = ref({
  month_wears: 0,
  favorite_category: '-',
  avg_cost_per_wear: '0.0',
})

const reminderEnabled = ref(false)
const reminderTime = ref('08:00')

// 编辑昵称相关
const isEditing = ref(false)
const editingNickname = ref('')
const savingNickname = ref(false)

// 修改密码相关
const showPasswordModal = ref(false)
const changingPassword = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 密码表单校验规则
const passwordRules = {
  old_password: {
    required: true,
    message: '请输入当前密码',
    trigger: 'blur',
  },
  new_password: [
    {
      required: true,
      message: '请输入新密码',
      trigger: 'blur',
    },
    {
      min: 6,
      message: '密码至少6位',
      trigger: 'blur',
    },
  ],
  confirm_password: [
    {
      required: true,
      message: '请确认新密码',
      trigger: 'blur',
    },
    {
      validator: (rule, value) => {
        return value === passwordForm.new_password || new Error('两次密码不一致')
      },
      trigger: 'blur',
    },
  ],
}

function getImgUrl(item) {
  const url = item.image_url || item.thumbnail_url || item.processed_url
  if (url && url.startsWith('/')) return API_BASE + url
  return url || ''
}

function getColdSize(index) {
  const row = Math.floor(index / 3)
  const col = index % 3
  if (row % 2 === 0) {
    return col === 0 ? 'cold-large' : 'cold-medium'
  } else {
    return col === 2 ? 'cold-large' : 'cold-medium'
  }
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}年${month}月${day}日`
}

// 编辑昵称
function startEdit() {
  editingNickname.value = user.value?.nickname || ''
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  editingNickname.value = ''
}

async function saveNickname() {
  if (!editingNickname.value.trim()) {
    message.warning('昵称不能为空')
    return
  }
  if (editingNickname.value.trim().length < 2) {
    message.warning('昵称至少2个字符')
    return
  }

  savingNickname.value = true
  try {
    const { data } = await api.put('/user/me', {
      nickname: editingNickname.value.trim(),
    })
    // 更新本地用户数据
    user.value.nickname = data.nickname
    authStore.user.nickname = data.nickname
    localStorage.setItem('nickname', data.nickname)
    isEditing.value = false
    message.success('昵称修改成功')
  } catch (err) {
    message.error(err.response?.data?.detail || '修改失败，请重试')
  } finally {
    savingNickname.value = false
  }
}

// 修改密码
async function handleChangePassword() {
  // 表单验证
  if (!passwordForm.old_password) {
    message.warning('请输入当前密码')
    return
  }
  if (!passwordForm.new_password || passwordForm.new_password.length < 6) {
    message.warning('新密码至少6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    message.warning('两次密码不一致')
    return
  }

  changingPassword.value = true
  try {
    await api.put('/user/password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    message.success('密码修改成功')
    showPasswordModal.value = false
    // 清空表单
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (err) {
    message.error(err.response?.data?.detail || '修改失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

async function saveReminder() {
  try {
    await api.put('/user/me', {
      daily_reminder: reminderEnabled.value,
      reminder_time: reminderTime.value,
    })
  } catch {}
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

  try {
    const { data } = await api.get('/stats/monthly')
    profileStats.value.month_wears = data.month_wears || data.total_wears || 0
    profileStats.value.favorite_category = data.favorite_category || '-'
    profileStats.value.avg_cost_per_wear = data.avg_cost_per_wear
      ? Number(data.avg_cost_per_wear).toFixed(1)
      : '0.0'
  } catch {}

  try {
    const { data } = await api.get('/user/me')
    if (data.daily_reminder !== undefined) {
      reminderEnabled.value = !!data.daily_reminder
    }
    if (data.reminder_time) {
      reminderTime.value = data.reminder_time
    }
  } catch {}
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

.page-header {
  margin-bottom: 28px;
}

.page-header h2 {
  font-family: 'Noto Serif SC', serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  letter-spacing: 1px;
}

.page-line {
  width: 100%;
  height: 1px;
  background: var(--theme-glass-border, rgba(255, 255, 255, 0.4));
  margin-top: 8px;
}

/* Info + Stats row */
.info-stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.user-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
  transition: background 0.4s ease, border-color 0.4s ease;
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
  color: var(--theme-text, #2E2A23);
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-email {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 4px;
}

.user-join-date {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 2px;
}

/* Edit mode styles */
.user-info-edit {
  flex: 1;
}

.edit-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}

/* Account actions */
.account-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.2));
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-item:hover {
  background: var(--theme-input-focus-bg, rgba(255, 255, 255, 0.35));
  transform: translateX(4px);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.4));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.action-text {
  flex: 1;
}

.action-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text, #2E2A23);
}

.action-desc {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 2px;
}

.action-arrow {
  color: var(--theme-text-secondary, #8C8478);
}

.stats-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
  transition: background 0.4s ease, border-color 0.4s ease;
}

.stats-grid {
  display: flex;
  gap: 24px;
  width: 100%;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-num {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 700;
  color: var(--theme-text, #2E2A23);
  line-height: 1.1;
}

.stat-label {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 6px;
  font-weight: 500;
}

/* AI card */
.ai-card {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.45));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  margin-bottom: 24px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: background 0.4s ease;
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

/* Quick stats */
.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.quick-stat-item {
  text-align: center;
  padding: 8px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.2));
  border-radius: 8px;
  transition: background 0.3s ease;
}

/* Reminder */
.reminder-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.reminder-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reminder-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text, #2E2A23);
}

.reminder-desc {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 2px;
}

.reminder-time-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.2));
  border-radius: 8px;
}

.reminder-time-label {
  font-size: 13px;
  color: var(--theme-primary-pressed, #5A5048);
  font-weight: 500;
}

/* Two col row */
.two-col-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

/* Section cards */
.section-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
  transition: background 0.4s ease, border-color 0.4s ease;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 16px;
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
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.25));
  backdrop-filter: blur(12px);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.ranking-item:hover {
  background: var(--theme-input-focus-bg, rgba(255, 255, 255, 0.4));
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
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
  color: var(--theme-text-secondary, #8C8478);
  flex-shrink: 0;
}

.rank-0 {
  background: var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.5));
  color: #FFFFFF;
}

.rank-1 {
  background: var(--theme-accent, rgba(200, 160, 155, 0.5));
  color: #FFFFFF;
}

.rank-2 {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.25));
  color: var(--theme-text-secondary, #8C8478);
}

.ranking-img {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.4));
}

.ranking-info {
  flex: 1;
}

.ranking-cat {
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text, #2E2A23);
}

.ranking-count {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 700;
  color: var(--theme-primary-pressed, #5A5048);
}

/* Cold items */
.cold-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  grid-auto-flow: dense;
}

.cold-item {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  box-shadow: var(--theme-card-shadow, 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 0 rgba(255, 255, 255, 0.5) inset);
}

.cold-item.cold-large {
  grid-column: span 2;
}

.cold-item:hover {
  border-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.cold-img-wrap {
  aspect-ratio: 1;
  overflow: hidden;
}

.cold-large .cold-img-wrap {
  aspect-ratio: 16/10;
}

.cold-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cold-info {
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.4));
}

.cold-cat {
  font-size: 12px;
  color: var(--theme-primary-pressed, #5A5048);
  font-weight: 500;
}

.cold-days {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
}

/* Empty state */
.empty-inline {
  text-align: center;
  padding: 36px 0;
}

.empty-inline-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  color: var(--theme-text-secondary, #8C8478);
  font-weight: 500;
}

.empty-inline-sub {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .info-stats-row {
    grid-template-columns: 1fr;
  }

  .two-col-row {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    gap: 12px;
  }

  .stat-num {
    font-size: 22px;
  }

  .quick-stats-grid {
    grid-template-columns: 1fr;
  }

  .cold-grid {
    grid-template-columns: 1fr;
  }

  .cold-item.cold-large {
    grid-column: span 1;
  }

  .cold-large .cold-img-wrap {
    aspect-ratio: 1;
  }

  .ai-card-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
