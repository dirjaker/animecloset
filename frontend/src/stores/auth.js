import { reactive } from 'vue'

export const authStore = reactive({
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),

  setAuth(token, user) {
    this.token = token
    this.user = user
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },

  logout() {
    this.token = ''
    this.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  get isLoggedIn() {
    return !!this.token
  }
})
