import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/habitaciones',
      name: 'habitaciones',
      component: () => import('../views/HabitacionesView.vue')
    },
    {
      path: '/reservar/:id',
      name: 'reservar',
      component: () => import('../views/ReservaView.vue')
    },
    {
      path: '/mis-reservas',
      name: 'mis-reservas',
      component: () => import('../views/MisReservasView.vue')
    },
    {
      path: '/contacto',
      name: 'contacto',
      component: () => import('../views/HomeView.vue') // temporal
    }
  ]
})

export default router
