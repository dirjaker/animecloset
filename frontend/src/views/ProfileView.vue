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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api/index.js'
import { authStore } from '../stores/auth.js'

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

onMounted(() => loadProfile())
</script>

<style scoped>
.profile-page h2 { font-size: 20px; color: #7c3aed; margin-bottom: 16px; }

.user-card {
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  border-radius: 20px; padding: 32px 24px;
  text-align: center; color: white; margin-bottom: 20px;
}

.avatar-placeholder {
  width: 80px; height: 80px; border-radius: 50%;
  margin: 0 auto 12px; display: flex; align-items: center;
  justify-content: center; font-size: 32px; font-weight: 700;
  border: 3px solid white; color: #7c3aed;
}

.user-card h3 { font-size: 18px; margin-bottom: 4px; }
.email { font-size: 13px; opacity: 0.8; }

.avatar-config {
  background: white; border-radius: 20px; padding: 24px;
  box-shadow: 0 2px 16px rgba(168, 85, 247, 0.1);
}
.avatar-config h3 { color: #7c3aed; font-size: 16px; margin-bottom: 16px; }

.config-group { margin-bottom: 18px; }
.config-group label { display: block; font-size: 14px; font-weight: 600; color: #6b21a8; margin-bottom: 8px; }

.option-row { display: flex; flex-wrap: wrap; gap: 8px; }
.opt-btn {
  padding: 8px 16px; border: 2px solid #e9d5ff; background: white;
  border-radius: 20px; font-size: 13px; cursor: pointer; transition: all 0.2s;
  color: #6b21a8;
}
.opt-btn.active {
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  color: white; border-color: transparent;
}

.btn-primary {
  margin-top: 8px; width: 100%; padding: 14px;
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  color: white; border: none; border-radius: 14px;
  font-size: 16px; font-weight: 600; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; }
</style>
