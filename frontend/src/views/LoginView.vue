<template>
  <div class="login-page">
    <!-- Animated floating orbs background -->
    <div class="login-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="orb orb-4"></div>
    </div>

    <!-- Glass card -->
    <div class="login-center">
      <div class="login-card">
        <div class="brand-row">
          <div class="brand-seal">
            <n-icon :component="ShirtOutline" :size="26" color="#FFFFFF" />
          </div>
          <h1 class="brand-name">Vestio</h1>
        </div>
        <p class="brand-sub">{{ isRegister ? '创建你的穿搭衣橱' : '穿衣有道，风格自成' }}</p>

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
    authStore.setAuth(data.access_token, { id: data.user_id, nickname: data.nickname })
    router.push('/wardrobe')
  } catch (e) {
    error.value = e.response?.data?.detail || (isRegister.value ? '注册失败' : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Page ── */
.login-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #F0EBE3;
}

/* ── Floating orbs background ── */
.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}

/* 玫瑰粉 — 左上 */
.orb-1 {
  width: 500px;
  height: 500px;
  background: #D4A0A0;
  top: -10%;
  left: -5%;
  animation: float1 18s infinite alternate;
}

/* 香槟金 — 右上 */
.orb-2 {
  width: 400px;
  height: 400px;
  background: #D4C5A0;
  top: -5%;
  right: -8%;
  animation: float2 22s infinite alternate;
}

/* 暖杏色 — 右下 */
.orb-3 {
  width: 450px;
  height: 450px;
  background: #D9B896;
  bottom: -10%;
  right: 5%;
  animation: float3 20s infinite alternate;
}

/* 淡紫灰 — 左下 */
.orb-4 {
  width: 350px;
  height: 350px;
  background: #C5B8D4;
  bottom: 5%;
  left: 10%;
  animation: float4 25s infinite alternate;
}

@keyframes float1 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(80px, 60px) scale(1.1); }
}

@keyframes float2 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-60px, 80px) scale(1.15); }
}

@keyframes float3 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-50px, -70px) scale(1.08); }
}

@keyframes float4 {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(70px, -40px) scale(1.12); }
}

/* ── Glass card ── */
.login-center {
  position: relative;
  z-index: 10;
}

.login-card {
  width: 400px;
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 44px 40px 36px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.6) inset;
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
  background: rgba(180, 130, 100, 0.75);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(180, 130, 100, 0.25);
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
  border-bottom: 1px solid rgba(160, 140, 120, 0.2);
  background: rgba(255, 255, 255, 0.25);
  padding: 10px 12px;
  font-size: 15px;
  color: #2E2A23;
  outline: none;
  transition: all 0.3s ease;
  font-family: inherit;
  border-radius: 6px 6px 0 0;
}

.line-input::placeholder {
  color: #B8A898;
  font-size: 14px;
}

.line-input:focus {
  border-bottom-color: #A0815A;
  border-bottom-width: 2px;
  padding-bottom: 9px;
  background: rgba(255, 255, 255, 0.35);
}

.error-msg {
  font-size: 13px;
  color: #C27C4E;
  margin-bottom: 16px;
  padding: 8px 14px;
  background: rgba(194, 124, 78, 0.08);
  border-radius: 6px;
  border-left: 2px solid #C27C4E;
  backdrop-filter: blur(8px);
}

.login-btn {
  width: 100%;
  height: 46px;
  background: rgba(180, 130, 100, 0.7);
  backdrop-filter: blur(12px);
  color: #FFFFFF;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 4px;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 4px;
  box-shadow: 0 2px 12px rgba(180, 130, 100, 0.2);
}

.login-btn:hover {
  background: rgba(180, 130, 100, 0.85);
  box-shadow: 0 4px 20px rgba(180, 130, 100, 0.3);
  transform: translateY(-1px);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
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
  transition: color 0.2s ease;
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

  .orb {
    filter: blur(60px);
    opacity: 0.5;
  }
}
</style>
