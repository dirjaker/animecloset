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
  background: linear-gradient(135deg, #fce7f3, #ede9fe, #e0e7ff);
}

.login-card {
  background: white;
  border-radius: 24px;
  padding: 40px 32px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 8px 32px rgba(168, 85, 247, 0.15);
  text-align: center;
}

.title { font-size: 28px; color: #a855f7; margin-bottom: 4px; }
.subtitle { color: #888; margin-bottom: 28px; font-size: 14px; }

.form { display: flex; flex-direction: column; gap: 14px; }

.input {
  padding: 14px 16px;
  border: 2px solid #f0e4ff;
  border-radius: 14px;
  font-size: 15px;
  outline: none;
  transition: border 0.2s;
}

.input:focus { border-color: #c084fc; }

.btn-primary {
  padding: 14px;
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.error { color: #ef4444; font-size: 13px; }

.switch-text { margin-top: 20px; font-size: 13px; color: #888; }

.link { color: #a855f7; cursor: pointer; font-weight: 500; }
</style>
