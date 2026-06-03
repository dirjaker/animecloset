<template>
  <div class="recommend-page">
    <h2>✨ 智能推荐</h2>

    <div class="form-card">
      <div class="field">
        <label>日期</label>
        <input type="date" v-model="date" class="input" />
      </div>

      <div class="field">
        <label>场合</label>
        <div class="occasion-grid">
          <button
            v-for="o in occasions"
            :key="o.value"
            :class="['occasion-btn', { active: occasion === o.value }]"
            @click="occasion = o.value"
          >{{ o.icon }} {{ o.label }}</button>
        </div>
      </div>

      <div class="field">
        <label>额外要求</label>
        <textarea v-model="extra" class="input textarea" placeholder="例如：今天想穿得可爱一点~" rows="3"></textarea>
      </div>

      <button class="btn-primary" @click="getRecommend" :disabled="loading">
        {{ loading ? '推荐中...' : '🔮 获取推荐' }}
      </button>
    </div>

    <div v-if="loading" class="loading-area">
      <div class="big-spinner"></div>
      <p>AI 正在为你搭配中...</p>
    </div>

    <div v-if="result" class="result-card">
      <h3>📋 推荐方案</h3>
      <p v-if="result.reason" class="reason">{{ result.reason }}</p>
      <p v-if="result.explanation" class="reason">{{ result.explanation }}</p>

      <div class="rec-grid">
        <div v-for="(item, i) in (result.recommendations || result.garments || result.items || [])" :key="i" class="rec-card">
          <div class="rec-img-wrap">
            <img :src="item.image_url || item.thumbnail_url" class="rec-img" />
          </div>
          <div class="rec-info">
            <span class="cat-badge">{{ item.category }}</span>
            <p v-if="item.reason" class="item-reason">{{ item.reason }}</p>
            <div class="tags" v-if="item.tags?.length">
              <span v-for="t in item.tags" :key="t" class="tag">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <button v-if="(result.recommendations || result.garments || result.items || []).length" class="btn-save" @click="saveOutfit">
        💾 保存这套穿搭
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/index.js'

const today = new Date().toISOString().split('T')[0]
const date = ref(today)
const occasion = ref('')
const extra = ref('')
const loading = ref(false)
const result = ref(null)
const error = ref('')

const occasions = [
  { value: 'daily', label: '日常', icon: '🏠' },
  { value: 'work', label: '工作', icon: '💼' },
  { value: 'date', label: '约会', icon: '💕' },
  { value: 'party', label: '聚会', icon: '🎉' },
  { value: 'sport', label: '运动', icon: '🏃' },
  { value: 'formal', label: '正式', icon: '👔' },
]

async function getRecommend() {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const { data } = await api.post('/recommend', {
      date: date.value,
      occasion: occasion.value,
      extra_requirements: extra.value,
    })
    result.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || '推荐失败，请重试'
  } finally {
    loading.value = false
  }
}

async function saveOutfit() {
  const items = result.value?.recommendations || result.value?.garments || result.value?.items || []
  const garmentIds = items.map(g => g.id).filter(Boolean)
  if (!garmentIds.length) return
  try {
    await api.post('/outfits', { date: date.value, garment_ids: garmentIds })
    alert('穿搭已保存！')
  } catch { alert('保存失败') }
}
</script>

<style scoped>
.recommend-page h2 { font-size: 20px; color: #7c3aed; margin-bottom: 16px; }

.form-card {
  background: white; border-radius: 20px; padding: 24px;
  box-shadow: 0 2px 16px rgba(168, 85, 247, 0.1);
  display: flex; flex-direction: column; gap: 16px;
}

.field label { display: block; font-size: 14px; font-weight: 600; color: #6b21a8; margin-bottom: 8px; }

.input {
  width: 100%; padding: 12px 14px; border: 2px solid #f0e4ff;
  border-radius: 12px; font-size: 14px; outline: none; transition: border 0.2s;
}
.input:focus { border-color: #c084fc; }
.textarea { resize: vertical; font-family: inherit; }

.occasion-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.occasion-btn {
  padding: 8px 14px; border: 2px solid #e9d5ff; background: white;
  border-radius: 20px; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.occasion-btn.active {
  background: linear-gradient(135deg, #e879f9, #a78bfa);
  color: white; border-color: transparent;
}

.btn-primary {
  padding: 14px; background: linear-gradient(135deg, #e879f9, #a78bfa);
  color: white; border: none; border-radius: 14px;
  font-size: 16px; font-weight: 600; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; }

.loading-area { text-align: center; padding: 40px; }
.big-spinner {
  width: 48px; height: 48px; border: 4px solid #e9d5ff;
  border-top-color: #a855f7; border-radius: 50%;
  animation: spin 0.8s linear infinite; margin: 0 auto 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.result-card {
  margin-top: 20px; background: white; border-radius: 20px; padding: 24px;
  box-shadow: 0 2px 16px rgba(168, 85, 247, 0.1);
}
.result-card h3 { color: #7c3aed; margin-bottom: 8px; }
.reason { color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 16px; }

.rec-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
@media (min-width: 600px) { .rec-grid { grid-template-columns: repeat(3, 1fr); } }

.rec-card {
  border-radius: 14px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.rec-img-wrap { aspect-ratio: 1; background: #f5f0ff; }
.rec-img { width: 100%; height: 100%; object-fit: cover; }
.rec-info { padding: 8px; }
.cat-badge {
  display: inline-block; background: #f3e8ff; color: #7c3aed;
  padding: 2px 10px; border-radius: 10px; font-size: 12px;
}
.item-reason { font-size: 12px; color: #888; margin-top: 4px; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.tag { background: #fce7f3; color: #db2777; padding: 2px 8px; border-radius: 8px; font-size: 11px; }

.btn-save {
  margin-top: 16px; width: 100%; padding: 14px;
  background: linear-gradient(135deg, #34d399, #2dd4bf);
  color: white; border: none; border-radius: 14px;
  font-size: 15px; font-weight: 600; cursor: pointer;
}

.error { color: #ef4444; text-align: center; margin-top: 12px; }
</style>
