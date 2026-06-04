<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="title">🌸 AnimeCloset</h1>
      <p class="subtitle">{{ isRegister ? '创建账号' : '欢迎回来' }}</p>

      <form @submit.prevent="handleSubmit" class="form">
        <input v-if="isRegister" v-model="nickname" type="text" placeholder="昵称" class="input" required />
        <input v-model="email" type="email" placeholder="邮箱" class="input" required />
        <input v-model="password" type="password" placeholder="密码" class="input" required minlength="6" />

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '请稍候...' : (isRegister ? '注册' : '登录') }}
        </button>
      </form>

      <p class="switch-text">
        {{ isRegister ? '已有账号？' : '没有账号？' }}
        <a @click="isRegister = !isRegister" class="link">{{ isRegister ? '去登录' : '去注册' }}</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/index.js'
import { authStore } from '../stores/auth.js'

const router = useRouter()
const isRegister = ref(false)
const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    if (isRegister.value) {
      await api.post('/auth/register', { email: email.value, password: password.value, nickname: nickname.value })
    }
    const { data } = await api.post('/auth/login', { email: email.value, password: password.value })
    authStore.setAuth(data.access_token || data.token, data.user || { email: email.value })
    router.push('/wardrobe')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF8F0;
  background-image:
    radial-gradient(circle at 30% 40%, rgba(212, 165, 116, 0.12) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(91, 124, 80, 0.08) 0%, transparent 50%);
}

.login-card {
  background: #FFF5EB;
  border: 2px solid #D4A574;
  border-radius: 20px;
  padding: 40px 32px;
  width: 100%;
  max-width: 380px;
  box-shadow:
    0 8px 32px rgba(139, 105, 20, 0.12),
    0 1px 0 rgba(255, 255, 255, 0.8) inset;
  text-align: center;
}

.title { font-size: 28px; color: #8B6914; margin-bottom: 4px; }
.subtitle { color: #8B7355; margin-bottom: 28px; font-size: 14px; }

.form { display: flex; flex-direction: column; gap: 14px; }

.input {
  padding: 14px 16px;
  border: 2px solid #E8D5B7;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border 0.2s;
  background: #FFFAF5;
  color: #4A3728;
}

.input:focus { border-color: #C17A3A; }
.input::placeholder { color: #B8A080; }

.btn-primary {
  padding: 14px;
  background: linear-gradient(135deg, #C17A3A, #8B6914);
  color: #FFF8F0;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(139, 105, 20, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #D4893A, #9B7924);
  transform: translateY(-1px);
}

.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.error { color: #C44D2A; font-size: 13px; }

.switch-text { margin-top: 20px; font-size: 13px; color: #8B7355; }

.link { color: #5B7C50; cursor: pointer; font-weight: 500; }
.link:hover { color: #4A6B3F; text-decoration: underline; }
</style>
