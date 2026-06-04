import axios from 'axios'

const api = axios.create({
  baseURL: `${window.location.protocol}//${window.location.hostname}:8000/api`,
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// Stats API
export const getWardrobeStats = () => api.get('/stats/wardrobe')
export const getWearRanking = (limit = 10) => api.get(`/stats/wear-ranking?limit=${limit}`)
export const getColdPalace = (days = 30) => api.get(`/stats/cold-palace?days=${days}`)
