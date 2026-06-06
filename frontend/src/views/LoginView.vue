<template>
  <div class="login-page">
    <!-- Warm gradient background (simulates a landscape photo) -->
    <div class="login-bg"></div>

    <!-- Centered glass card -->
    <div class="login-center">
      <div class="login-card">
        <div class="brand-row">
          <div class="brand-seal">
            <n-icon :component="ShirtOutline" :size="26" color="#FFFFFF" />
          </div>
          <h1 class="brand-name">衫 间</h1>
        </div>
        <p class="brand-sub">{{ isRegister ? '创建你的穿搭衣橱' : '衣衫之间，自有天地' }}</p>

        <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <div v-if="isRegister" class="form-field">
            <input v-model="form.nickname" class="line-input" placeholder="昵称" />
          </div>
          <div class="form-field">
            <input v-model="form.email" class="line-input" placeholder="邮箱" />
          </div>
          <div class="form-field">
            <input v-model="form.password" type="password" class="line-input" placeholder="密码" />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button type="button" class="login-btn" :disabled="loading" @click="handleSubmit">
            {{ loading ? '请稍候...' : (isRegister ? '注 册' : '登 录') }}
          </button>
        </n-form>

        <div class="login-footer">
          <span class="footer-text">{{ isRegister ? '已有账号？' : '没有账号？' }}</span>
          <a class="footer-link" @click="isRegister = !isRegister">
            {{ isRegister ? '去登录' : '去注册' }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ShirtOutline } from '@vicons/ionicons5'
import api from '../api/index.js'
import { authStore } from '../stores/auth.js'

const router = useRouter()
const isRegister = ref(false)
const loading = ref(false)
const error = ref('')

const form = reactive({
  email: '',
  password: '',
  nickname: '',
})

const rules = {
  email: { required: true, message: '请输入邮箱', trigger: 'blur' },
  password: { required: true, min: 6, message: '密码至少6位', trigger: 'blur' },
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    if (isRegister.value) {
      await api.post('/auth/register', {
        email: form.email,
        password: form.password,
        nickname: form.nickname || form.email.split('@')[0],
      })
    }
    const { data } = await api.post('/auth/login', {
      email: form.email,
      password: form.password,
    })
    authStore.setToken(data.access_token)
    authStore.setUser({ id: data.user_id, nickname: data.nickname })
    router.push('/wardrobe')
  } catch (e) {
    error.value = e.response?.data?.detail || (isRegister.value ? '注册失败' : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ── Background gradient (warm landscape simulation) ── */
.login-bg {
  position: absolute;
  inset: 0;
  background:
    /* Mountain silhouette in back */
    radial-gradient(ellipse 120% 60% at 50% 100%, #8B7355 0%, transparent 70%),
    /* Warm horizon glow */
    radial-gradient(ellipse 80% 40% at 50% 70%, #C4A882 0%, transparent 60%),
    /* Sky gradient */
    linear-gradient(175deg, #E8DFD0 0%, #D4C5A9 30%, #C4A882 55%, #A0815A 85%, #6B5535 100%);
  z-index: 0;
}

/* Subtle grain / texture overlay */
.login-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle 2px at 20% 30%, rgba(255, 255, 255, 0.03) 0%, transparent 100%),
    radial-gradient(circle 1px at 80% 70%, rgba(255, 255, 255, 0.05) 0%, transparent 100%),
    radial-gradient(circle 3px at 50% 50%, rgba(160, 129, 90, 0.04) 0%, transparent 100%);
  z-index: 1;
  pointer-events: none;
}

/* ── Centered card ── */
.login-center {
  position: relative;
  z-index: 10;
}

.login-card {
  width: 400px;
  background: rgba(255, 253, 248, 0.55);
  backdrop-filter: blur(24px) saturate(140%);
  -webkit-backdrop-filter: blur(24px) saturate(140%);
  border: 1px solid rgba(255, 253, 248, 0.5);
  border-radius: 12px;
  padding: 44px 40px 36px;
  box-shadow: 0 8px 40px rgba(46, 42, 35, 0.12), 0 2px 8px rgba(46, 42, 35, 0.06);
}

/* ── Brand ── */
.brand-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.brand-seal {
  width: 48px;
  height: 48px;
  background: #A0815A;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(160, 129, 90, 0.3);
}

.brand-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 700;
  color: #2E2A23;
  letter-spacing: 6px;
  margin: 0;
}

.brand-sub {
  text-align: center;
  font-size: 13px;
  color: #8C8478;
  margin-bottom: 32px;
  letter-spacing: 1px;
}

/* ── Form ── */
.form-field {
  margin-bottom: 22px;
}

.line-input {
  width: 100%;
  border: none;
  border-bottom: 1px solid rgba(160, 129, 90, 0.25);
  background: transparent;
  padding: 10px 4px;
  font-size: 15px;
  color: #2E2A23;
  outline: none;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.line-input::placeholder {
  color: #B8A898;
  font-size: 14px;
}

.line-input:focus {
  border-bottom-color: #A0815A;
  border-bottom-width: 2px;
  padding-bottom: 9px;
}

.error-msg {
  font-size: 13px;
  color: #C27C4E;
  margin-bottom: 16px;
  padding: 8px 14px;
  background: rgba(194, 124, 78, 0.1);
  border-radius: 6px;
  border-left: 2px solid #C27C4E;
}

.login-btn {
  width: 100%;
  height: 46px;
  background: #A0815A;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 4px;
}

.login-btn:hover {
  background: #B8956E;
  box-shadow: 0 4px 16px rgba(160, 129, 90, 0.25);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  margin-top: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.footer-text {
  font-size: 13px;
  color: #8C8478;
}

.footer-link {
  font-size: 13px;
  color: #A0815A;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
}

.footer-link:hover {
  color: #C27C4E;
}

/* ── Mobile ── */
@media (max-width: 480px) {
  .login-card {
    width: 90vw;
    padding: 36px 28px 28px;
  }

  .brand-name {
    font-size: 24px;
    letter-spacing: 4px;
  }
}
</style>
