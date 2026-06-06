<template>
  <div class="login-page">
    <!-- Left panel -->
    <div class="login-left">
      <div class="left-content">
        <h1 class="left-title">
          每日穿搭<br />从衣橱开始
        </h1>
      </div>
    </div>

    <!-- Right panel -->
    <div class="login-right">
      <div class="login-card">
        <div class="login-header">
          <div class="login-seal">
            <n-icon :component="ShirtOutline" :size="28" color="#FFFFFF" />
          </div>
          <h1 class="login-title">衣 楷</h1>
          <p class="login-subtitle">{{ isRegister ? '创建你的智能衣橱' : '欢迎回来' }}</p>
        </div>

        <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <div v-if="isRegister" class="form-field">
            <label class="field-label">昵称</label>
            <input v-model="form.nickname" class="line-input" placeholder="输入昵称" />
          </div>

          <div class="form-field">
            <label class="field-label">邮箱</label>
            <input v-model="form.email" class="line-input" placeholder="输入邮箱" />
          </div>

          <div class="form-field">
            <label class="field-label">密码</label>
            <input v-model="form.password" type="password" class="line-input" placeholder="输入密码" />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button type="button" class="login-btn" :disabled="loading" @click="handleSubmit">
            {{ loading ? '请稍候...' : (isRegister ? '注册' : '登录') }}
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
      await api.post('/auth/register', { email: form.email, password: form.password, nickname: form.nickname })
    }
    const { data } = await api.post('/auth/login', { email: form.email, password: form.password })
    authStore.setAuth(data.access_token || data.token, data.user || { email: form.email })
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
}

.login-left {
  width: 40%;
  background: #D4C5A9;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-content {
  padding: 48px;
}

.left-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 36px;
  font-weight: 700;
  color: #2E2A23;
  line-height: 1.6;
  letter-spacing: 2px;
}

.login-right {
  width: 60%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F0E8;
  padding: 40px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: rgba(255, 253, 248, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid #E0D8CC;
  border-radius: 8px;
  padding: 40px 32px 32px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-seal {
  width: 56px;
  height: 56px;
  background: #A0815A;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.login-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 22px;
  font-weight: 700;
  color: #2E2A23;
  letter-spacing: 4px;
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: #8C8478;
}

.form-field {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 12px;
  color: #8C8478;
  margin-bottom: 6px;
}

.line-input {
  width: 100%;
  border: none;
  border-bottom: 1px solid #E0D8CC;
  background: transparent;
  padding: 8px 0;
  font-size: 15px;
  color: #2E2A23;
  outline: none;
  transition: border-color 0.2s ease;
  font-family: inherit;
}

.line-input:focus {
  border-bottom-color: #A0815A;
  border-bottom-width: 2px;
}

.line-input::placeholder {
  color: #C0B8A8;
}

.error-msg {
  font-size: 13px;
  color: #C27C4E;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: rgba(194, 124, 78, 0.08);
  border-radius: 6px;
}

.login-btn {
  width: 100%;
  height: 44px;
  background: #A0815A;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-top: 8px;
}

.login-btn:hover {
  background: #B8956E;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
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
}

.footer-link:hover {
  color: #C27C4E;
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-left {
    width: 100%;
    height: 30vh;
  }

  .left-title {
    font-size: 24px;
  }

  .login-right {
    width: 100%;
    flex: 1;
    padding: 24px;
  }
}
</style>
