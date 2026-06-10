<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2>我的</h2>
        <div class="page-line"></div>
      </div>
    </div>

    <!-- 用户信息卡片 -->
    <div class="user-card" @click="openProfileModal">
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
        </div>
        <n-icon :component="ChevronForwardOutline" :size="20" class="card-arrow" />
      </div>
    </div>

    <!-- 统计卡片 -->
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

    <!-- 分类统计 -->
    <div class="section-card">
      <div class="section-header">
        <n-icon :component="ShirtOutline" :size="18" />
        <span>衣物分类</span>
      </div>
      <div class="category-grid">
        <div v-for="cat in categoryStats" :key="cat.name" class="category-item">
          <span class="cat-name">{{ cat.name }}</span>
          <span class="cat-count">{{ cat.count }} 件</span>
        </div>
      </div>
    </div>

    <!-- 设置 -->
    <div class="section-card">
      <div class="section-header">
        <n-icon :component="SettingsOutline" :size="18" />
        <span>设置</span>
      </div>
      <div class="settings-list">
        <div class="setting-item" @click="toggleDarkMode">
          <span>深色模式</span>
          <n-switch v-model:value="isDarkMode" />
        </div>
        <div class="setting-item logout" @click="handleLogout">
          <span>退出登录</span>
          <n-icon :component="LogOutOutline" :size="18" />
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
    >
      <div class="profile-edit-content">
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

        <n-form
          ref="profileFormRef"
          :model="editForm"
          label-placement="left"
          label-width="70"
        >
          <n-form-item label="昵称">
            <n-input
              v-model:value="editForm.nickname"
              placeholder="请输入昵称"
              :maxlength="50"
            />
          </n-form-item>

          <n-form-item label="邮箱">
            <n-input :value="user?.email || ''" disabled />
          </n-form-item>

          <n-form-item label="性别">
            <n-radio-group v-model:value="editForm.gender">
              <n-space>
                <n-radio value="male">男</n-radio>
                <n-radio value="female">女</n-radio>
                <n-radio value="other">其他</n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ChevronForwardOutline, ShirtOutline, SettingsOutline, LogOutOutline } from '@vicons/ionicons5'
import api from '../api/index.js'

const router = useRouter()
const message = useMessage()

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

const user = ref(null)
const stats = ref(null)
const showProfileModal = ref(false)
const saving = ref(false)
const avatarInputRef = ref(null)
const isDarkMode = ref(false)

const editForm = ref({
  nickname: '',
  gender: '',
  avatar_url: ''
})

// 分类统计
const categoryStats = computed(() => {
  if (!stats.value?.category_counts) return []
  return Object.entries(stats.value.category_counts).map(([name, count]) => ({ name, count }))
})

// 性别标签
const genderLabel = computed(() => {
  const map = { male: '男', female: '女', other: '其他' }
  return map[user.value?.gender] || ''
})

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 加载用户信息
async function loadUser() {
  try {
    const { data } = await api.get('/user/me')
    user.value = data
  } catch {
    // 忽略
  }
}

// 加载统计
async function loadStats() {
  try {
    const { data } = await api.get('/stats/summary')
    stats.value = data
  } catch {
    // 忽略
  }
}

// 打开编辑弹窗
function openProfileModal() {
  editForm.value = {
    nickname: user.value?.nickname || '',
    gender: user.value?.gender || '',
    avatar_url: user.value?.avatar_url || ''
  }
  showProfileModal.value = true
}

// 触发头像上传
function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

// 处理头像上传
async function handleAvatarUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  
  const fd = new FormData()
  fd.append('file', file)
  
  try {
    const { data } = await api.post('/user/avatar/upload', fd)
    editForm.value.avatar_url = data.avatar_url
    message.success('头像上传成功')
  } catch {
    message.error('头像上传失败')
  }
  
  e.target.value = ''
}

// 保存个人资料
async function handleSaveProfile() {
  saving.value = true
  try {
    await api.put('/user/me', {
      nickname: editForm.value.nickname,
      gender: editForm.value.gender,
      avatar_url: editForm.value.avatar_url
    })
    message.success('保存成功')
    showProfileModal.value = false
    await loadUser()
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 切换深色模式
function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : '')
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : '')
}

// 退出登录
function handleLogout() {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(async () => {
  // 检查深色模式
  isDarkMode.value = localStorage.getItem('theme') === 'dark'
  
  await Promise.all([loadUser(), loadStats()])
})
</script>

<style scoped>
.profile-page {
  animation: pageEnter 0.3s ease;
  max-width: 600px;
  margin: 0 auto;
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
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.4));
  margin-top: 8px;
}

/* 用户卡片 */
.user-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-card:hover {
  border-color: var(--theme-glass-border, rgba(255, 255, 255, 0.6));
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.user-card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 4px;
}

.user-email {
  font-size: 13px;
  color: var(--theme-text-secondary, #8C8478);
}

.card-arrow {
  color: var(--theme-text-secondary, #8C8478);
}

/* 统计卡片 */
.stats-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  text-align: center;
}

.stat-num {
  font-family: 'Noto Serif SC', serif;
  font-size: 24px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
}

/* 分类统计 */
.section-card {
  background: var(--theme-glass-bg, rgba(255, 255, 255, 0.35));
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid var(--theme-glass-border, rgba(255, 255, 255, 0.45));
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 16px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.category-item {
  text-align: center;
  padding: 12px 8px;
  background: var(--theme-surface-bg, rgba(240, 235, 227, 0.5));
  border-radius: 8px;
}

.cat-name {
  display: block;
  font-size: 13px;
  color: var(--theme-text, #2E2A23);
  margin-bottom: 4px;
}

.cat-count {
  font-size: 12px;
  color: var(--theme-text-secondary, #8C8478);
}

/* 设置列表 */
.settings-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: background 0.2s ease;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.setting-item span {
  font-size: 14px;
  color: var(--theme-text, #2E2A23);
}

.setting-item.logout {
  color: var(--theme-accent, #C8A09B);
}

.setting-item.logout span {
  color: var(--theme-accent, #C8A09B);
}

/* 编辑弹窗 */
.profile-edit-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-edit-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
