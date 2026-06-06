<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon-ring">
          <n-icon :component="ShirtOutline" :size="28" color="#FFFFFF" />
        </div>
        <h1>衣 楷</h1>
        <p>{{ isRegister ? '创建你的智能衣橱' : '欢迎回来' }}</p>
      </div>

      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
        <n-form-item v-if="isRegister" path="nickname" label="昵称">
          <n-input v-model:value="form.nickname" placeholder="输入昵称" size="large" />
        </n-form-item>

        <n-form-item path="email" label="邮箱">
          <n-input v-model:value="form.email" placeholder="输入邮箱" size="large" />
        </n-form-item>

        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="form.password"
            type="password"
            placeholder="输入密码"
            show-password-on="click"
            size="large"
          />
        </n-form-item>

        <n-alert v-if="error" type="error" :bordered="false" closable @close="error = ''" style="margin-bottom: 16px">
          {{ error }}
        </n-alert>

        <n-button
          type="primary"
          block
          :loading="loading"
          attr-type="submit"
          size="large"
          class="login-btn"
        >
          {{ isRegister ? '注册' : '登录' }}
        </n-button>
      </n-form>

      <div class="login-footer">
        <span class="login-footer-text">{{ isRegister ? '已有账号？' : '没有账号？' }}</span>
        <n-button text type="primary" @click="isRegister = !isRegister" size="small">
          {{ isRegister ? '去登录' : '去注册' }}
        </n-button>
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
  align-items: center;
  justify-content: center;
  background: #F6F3EE;
  background-image: radial-gradient(circle at 50% 50%, rgba(91, 125, 106, 0.05) 0%, transparent 70%);
  padding: 20px;
}

.login-card {
  background: #FFFDF9;
  border-radius: 8px;
  padding: 48px 36px 36px;
  width: 100%;
  max-width: 380px;
  border: 1px solid #E8E3DA;
  box-shadow: 0 1px 4px rgba(44, 42, 37, 0.06);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-icon-ring {
  width: 56px;
  height: 56px;
  border-radius: 4px;
  background: #5B7D6A;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.login-header h1 {
  font-family: 'Noto Serif SC', serif;
  font-size: 24px;
  font-weight: 700;
  color: #2C2A25;
  margin-bottom: 6px;
  letter-spacing: 4px;
}

.login-header p {
  font-size: 14px;
  color: #8A8578;
}

.login-btn {
  border-radius: 8px;
  height: 44px;
  font-weight: 600;
  font-family: 'Noto Serif SC', serif;
  background: #5B7D6A !important;
  border-color: #5B7D6A !important;
  transition: all 0.2s ease;
}

.login-btn:hover {
  background: #6B8D7A !important;
  border-color: #6B8D7A !important;
}

.login-footer {
  text-align: center;
  margin-top: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.login-footer-text {
  font-size: 14px;
  color: #8A8578;
}
</style>
