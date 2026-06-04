<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon-ring">
          <n-icon :component="ShirtOutline" :size="32" color="#D4884A" />
        </div>
        <h1>AnimeCloset</h1>
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
  background: #F8F6F3;
  padding: 20px;
}

.login-card {
  background: #FFFFFF;
  border-radius: 20px;
  padding: 48px 36px 36px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 6px 16px rgba(0,0,0,0.03);
  border: 1px solid #F0EFEC;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-icon-ring {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #FDF4EC;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 26px;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}

.login-header p {
  font-size: 14px;
  color: #6B7280;
}

.login-btn {
  border-radius: 12px;
  height: 44px;
  font-weight: 600;
  background: linear-gradient(135deg, #D4884A, #E8A060) !important;
  border: none !important;
  transition: all 0.2s ease;
}

.login-btn:hover {
  background: linear-gradient(135deg, #E8A060, #F0B878) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(212, 136, 74, 0.3);
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
  color: #6B7280;
}
</style>
