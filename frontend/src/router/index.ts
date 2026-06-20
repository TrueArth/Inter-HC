import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Admin from '../views/Admin.vue';

import Pacientes from '../views/Pacientes.vue';
import Interconsultas from '../views/Interconsultas.vue';
import CentralMarcacao from '../views/CentralMarcacao.vue';


const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/pacientes',
    name: 'Pacientes',
    component: Pacientes,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/interconsultas',

    name: 'Interconsultas',
    component: Interconsultas,
    meta: { requiresAuth: true, requiresMedico: true },
  },
  {
    path: '/central-marcacao',
    name: 'Central de Marcação',
    component: CentralMarcacao,
    meta: { requiresAuth: true, requiresRegulador: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkActiveClass: 'bg-paper-active-link',
  linkExactActiveClass: 'bg-paper-active-link',
});

router.beforeEach((to, _from, next: NavigationGuardNext) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Home' });
  } else if (to.meta.requiresMedico && !(authStore.isAdmin || authStore.isMedico)) {
    next({ name: 'Home' });
  } else if (to.meta.requiresRegulador && !(authStore.isAdmin || authStore.isRegulador)) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
