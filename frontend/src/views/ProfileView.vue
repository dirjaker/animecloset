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
      <div class="user-card clickable" @click="openProfileModal">
        <div class="user-card-inner">
          <div class="avatar-wrap">
            <n-avatar 
              :size="64" 
              round 
              :src="user?.avatar_url || undefined"
              :style="{ 
                background: user?.avatar_url ? 'transparent' : 'var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.45))', 
                backdropFilter: 'blur(12px)', 
                fontSize: '28px', 
                fontWeight: '600', 
                fontFamily: 'Noto Serif SC, serif' 
              }"
            >
              {{ user?.nickname?.charAt(0) || '?' }}
            </n-avatar>
          </div>
          <div class="user-info">
            <p class="user-name">{{ user?.nickname || user?.email || '用户' }}</p>
            <p class="user-email">{{ user?.email }}</p>
            <div class="user-meta">
              <span v-if="genderLabel" class="meta-tag">{{ genderLabel }}</span>
              <span v-if="user?.created_at" class="meta-date">加入于 {{ formatDate(user.created_at) }}</span>
            </div>
          </div>
          <n-icon :component="ChevronForwardOutline" :size="20" class="card-arrow" />
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

    <!-- 个人资料编辑弹窗 -->
    <n-modal
      v-model:show="showProfileModal"
      preset="card"
      title="编辑个人资料"
      :style="{ maxWidth: '480px' }"
      :bordered="false"
      :mask-closable="false"
    >
      <div class="profile-edit-content">
        <!-- 头像区域 -->
        <div class="avatar-edit-section">
          <n-avatar 
            :size="80" 
            round 
            :src="editForm.avatar_url || undefined"
            :style="{ 
              background: editForm.avatar_url ? 'transparent' : 'var(--theme-dark-glass-bg, rgba(80, 70, 65, 0.45))', 
              fontSize: '36px', 
              fontWeight: '600', 
              fontFamily: 'Noto Serif SC, serif',
              cursor: 'pointer'
            }"
            @click="triggerAvatarUpload"
          >
            {{ editForm.nickname?.charAt(0) || '?' }}
          </n-avatar>
          <input 
            ref="avatarInputRef"
            type="file" 
            accept="image/*" 
            style="display: none" 
            @change="handleAvatarUpload"
          />
          <n-button size="small" @click="triggerAvatarUpload">更换头像</n-button>
        </div>

        <!-- 表单 -->
        <n-form
          ref="profileFormRef"
          :model="editForm"
          :rules="profileRules"
          label-placement="left"
          label-width="70"
        >
          <n-form-item label="昵称" path="nickname">
            <n-input
              v-model:value="editForm.nickname"
              placeholder="请输入昵称"
              :maxlength="50"
            />
          </n-form-item>

          <n-form-item label="邮箱">
            <n-input :value="user?.email" disabled placeholder="未绑定邮箱" />
          </n-form-item>

          <n-form-item label="性别" path="gender">
            <n-radio-group v-model:value="editForm.gender">
              <n-space>
                <n-radio value="male">男</n-radio>
                <n-radio value="female">女</n-radio>
                <n-radio value="other">其他</n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>

          <!-- 修改密码折叠面板 -->
          <div class="password-section">
            <div class="password-toggle" @click="showPasswordFields = !showPasswordFields">
              <span>修改密码</span>
              <n-icon 
                :component="showPasswordFields ? ChevronUpOutline : ChevronDownOutline" 
                :size="16" 
              />
            </div>
            
            <div v-if="showPasswordFields" class="password-fields">
              <n-form-item label="当前密码" path="old_password">
                <n-input
                  v-model:value="editForm.old_password"
                  type="password"
                  show-password-on="click"
                  placeholder="请输入当前密码"
                />
              </n-form-item>

              <n-form-item label="新密码" path="new_password">
                <n-input
                  v-model:value="editForm.new_password"
                  type="password"
                  show-password-on="click"
                  placeholder="请输入新密码（至少6位）"
                />
              </n-form-item>

              <n-form-item label="确认密码" path="confirm_password">
                <n-input
                  v-model:value="editForm.confirm_password"
                  type="password"
                  show-password-on="click"
                  placeholder="请再次输入新密码"
                />
              </n-form-item>
            </div>
          </div>
        </n-form>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 12px;">
          <n-button @click="showProfileModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveProfile" :loading="saving">
            保存
          </n-button>
        </div>
      </template>
    </n-modal>

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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  SparklesOutline,
  StatsChartOutline,
  ChevronForwardOutline,
  NotificationsOutline,
  ChevronUpOutline,
  ChevronDownOutline,
} from '@vicons/ionicons5'
import { 
  NStatistic, NSwitch, NTimePicker, NInput, NForm, NFormItem, 
  NModal, NAvatar, NRadioGroup, NRadio, NSpace, useMessage 
} from 'naive-ui'
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

// 个人资料弹窗相关
const showProfileModal = ref(false)
const saving = ref(false)
const showPasswordFields = ref(false)
const avatarInputRef = ref(null)
const profileFormRef = ref(null)

const editForm = reactive({
  nickname: '',
  gender: null,
  avatar_url: '',
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 性别显示
const genderLabel = computed(() => {
  const map = { male: '♂ 男', female: '♀ 女', other: '其他' }
  return map[user.value?.gender] || ''
})

// 表单校验规则
const profileRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 50, message: '昵称长度 2-50 个字符', trigger: 'blur' },
  ],
  new_password: [
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    {
      validator: (rule, value) => {
        if (editForm.new_password && !value) {
          return new Error('请确认新密码')
        }
        if (value && value !== editForm.new_password) {
          return new Error('两次密码不一致')
        }
        return true
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

// 打开编辑弹窗
async function openProfileModal() {
  // 从 API 获取最新用户信息
  try {
    const { data } = await api.get('/user/me')
    // 更新用户信息
    user.value = data
    authStore.user = { ...authStore.user, ...data }
  } catch (err) {
    console.error('Failed to fetch user info:', err)
  }
  
  editForm.nickname = user.value?.nickname || ''
  editForm.gender = user.value?.gender || null
  editForm.avatar_url = user.value?.avatar_url || ''
  editForm.old_password = ''
  editForm.new_password = ''
  editForm.confirm_password = ''
  showPasswordFields.value = false
  showProfileModal.value = true
}

// 触发头像上传
function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

// 处理头像上传
async function handleAvatarUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    message.error('请选择图片文件')
    return
  }

  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    message.error('图片大小不能超过 5MB')
    return
  }

  // 上传到后端
  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await api.post('/user/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    editForm.avatar_url = data.url
    message.success('头像上传成功')
  } catch (err) {
    message.error('头像上传失败')
  }

  // 清空 input
  event.target.value = ''
}

// 保存个人资料
async function handleSaveProfile() {
  // 验证表单
  try {
    await profileFormRef.value?.validate()
  } catch {
    return
  }

  // 如果要修改密码，验证旧密码
  if (editForm.new_password && !editForm.old_password) {
    message.warning('请输入当前密码')
    return
  }

  saving.value = true
  try {
    // 更新基本信息
    const { data } = await api.put('/user/me', {
      nickname: editForm.nickname,
      gender: editForm.gender,
      avatar_url: editForm.avatar_url,
    })

    // 更新本地用户数据
    user.value.nickname = data.nickname
    user.value.gender = data.gender
    user.value.avatar_url = data.avatar_url
    authStore.user.nickname = data.nickname
    localStorage.setItem('nickname', data.nickname)

    // 如果要修改密码
    if (editForm.new_password) {
      await api.put('/user/password', {
        old_password: editForm.old_password,
        new_password: editForm.new_password,
      })
      message.success('个人资料和密码已更新')
    } else {
      message.success('个人资料已更新')
    }

    showProfileModal.value = false
  } catch (err) {
    message.error(err.response?.data?.detail || '保存失败，请重试')
  } finally {
    saving.value = false
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
}

.user-email {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
  margin-top: 4px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 12px;
  padding: 2px 8px;
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.3));
  border-radius: 4px;
  color: var(--theme-text-secondary, #8C8478);
}

.meta-date {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
}

.card-arrow {
  color: var(--theme-text-secondary, #8C8478);
  margin-left: auto;
  flex-shrink: 0;
}

/* Clickable user card */
.user-card.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* Profile edit modal */
.profile-edit-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.avatar-edit-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.password-section {
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px dashed var(--theme-glass-border, rgba(0, 0, 0, 0.1));
}

.password-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 8px 0;
  color: var(--theme-primary, #A0815A);
  font-size: 14px;
  font-weight: 500;
}

.password-toggle:hover {
  opacity: 0.8;
}

.password-fields {
  margin-top: 12px;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
