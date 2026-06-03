import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../stores/auth.js'

const routes = [
  { path: '/', redirect: '/wardrobe' },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { guest: true } },
  { path: '/wardrobe', component: () => import('../views/WardrobeView.vue'), meta: { auth: true } },
  { path: '/recommend', component: () => import('../views/RecommendView.vue'), meta: { auth: true } },
  { path: '/calendar', component: () => import('../views/CalendarView.vue'), meta: { auth: true } },
  { path: '/profile', component: () => import('../views/ProfileView.vue'), meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.auth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && authStore.isLoggedIn) {
    next('/wardrobe')
  } else {
    next()
  }
})

export default router
