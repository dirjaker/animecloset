import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../stores/auth.js'
import WardrobeView from '../views/WardrobeView.vue'

const routes = [
  { path: '/', redirect: '/wardrobe' },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/wardrobe', component: WardrobeView, meta: { auth: true } },
  { path: '/recommend', component: () => import('../views/RecommendView.vue'), meta: { auth: true } },
  { path: '/calendar', component: () => import('../views/CalendarView.vue'), meta: { auth: true } },
  { path: '/profile', component: () => import('../views/ProfileView.vue'), meta: { auth: true } },
  { path: '/builder', component: () => import('../views/OutfitBuilder.vue'), meta: { auth: true } },
  { path: '/packing', component: () => import('../views/PackingView.vue'), meta: { auth: true } },
  { path: '/stats', component: () => import('../views/StatsView.vue'), meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Only guard authenticated routes — guest routes are free
router.beforeEach((to, from, next) => {
  if (to.meta.auth && !authStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
