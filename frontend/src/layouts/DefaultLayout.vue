<template>
  <div class="relative h-screen overflow-hidden md:flex">
    <!-- Mobile Menu -->
    <div class="bg-paper-sidebar text-gray-100 flex justify-between md:hidden shrink-0">
      <router-link to="/" class="block p-4 text-white font-bold">InterHC</router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-4 focus:outline-none focus:bg-paper-active-link">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar -->
    <aside :class="{ '-translate-x-full': !sidebarOpen }" class="bg-paper-sidebar text-gray-100 w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition duration-200 ease-in-out z-20 h-full shrink-0">
      <div @click="() => router.push('/')" class="cursor-pointer text-white flex items-center space-x-2 px-4">
        <CubeTransparentIcon class="h-8 w-8"/>
        <span class="text-2xl font-extrabold">InterHC</span>
      </div>
      <div class="px-4 my-6">
        <div class="border-t border-white border-opacity-20"></div>
      </div>

      <nav>
        <router-link to="/" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <HomeIcon class="h-6 w-6"/>
          <span>Home</span>
        </router-link>





            <router-link
              v-if="authStore.isAuthenticated && (authStore.isAdmin || authStore.isMedico)"
              to="/interconsultas"
              class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
            >
              <ClipboardDocumentListIcon class="h-6 w-6" />
              <span>Interconsultas</span>
            </router-link>
            <router-link
              v-if="authStore.isAuthenticated && (authStore.isAdmin || authStore.isRegulador)"
              to="/central-marcacao"
              class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
            >
              <QueueListIcon class="h-6 w-6" />
              <span>Central de Marcação</span>
            </router-link>
        <router-link v-if="authStore.isAdmin" to="/admin" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <ShieldCheckIcon class="h-6 w-6"/>
          <span>Admin</span>
        </router-link>


      </nav>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col bg-paper-bg overflow-y-auto h-full">
      <header class="flex justify-between items-center p-6 bg-white/80 backdrop-blur-md border-b border-gray-300 sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-semibold text-paper-text">{{ $route.name }}</h1>
        </div>
        <div>
          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-4 md:py-6">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Floating Undo Banner -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-10 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform translate-y-10 opacity-0 scale-95"
    >
      <div 
        v-if="interconsultaStore.activeUndoAction"
        class="fixed bottom-6 right-6 z-50 bg-gray-900/95 backdrop-blur text-white rounded-2xl shadow-2xl p-4 flex items-center justify-between gap-6 border border-gray-800 min-w-[320px] font-sans"
      >
        <div class="flex items-center gap-3">
          <div class="relative flex items-center justify-center w-8 h-8">
            <svg class="w-8 h-8 transform -rotate-90">
              <circle
                class="text-gray-700"
                stroke-width="3"
                stroke="currentColor"
                fill="transparent"
                r="12"
                cx="16"
                cy="16"
              />
              <circle
                class="text-blue-500 transition-all duration-1000 ease-linear"
                stroke-width="3"
                :stroke-dasharray="2 * Math.PI * 12"
                :stroke-dashoffset="((30 - interconsultaStore.activeUndoAction.secondsLeft) / 30) * (2 * Math.PI * 12)"
                stroke-linecap="round"
                stroke="currentColor"
                fill="transparent"
                r="12"
                cx="16"
                cy="16"
              />
            </svg>
            <span class="absolute text-[10px] font-bold">{{ interconsultaStore.activeUndoAction.secondsLeft }}</span>
          </div>
          <div>
            <p class="text-xs text-gray-400 font-semibold">Ação pendente...</p>
            <p class="text-sm font-bold">{{ interconsultaStore.activeUndoAction.name }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button 
            @click="confirmarAcao"
            class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow transition focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-gray-900"
          >
            Confirmar
          </button>
          <button 
            @click="desfazerAcao"
            class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold rounded-lg shadow transition focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-900"
          >
            Desfazer
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  HomeIcon,
  ShieldCheckIcon,
  CubeTransparentIcon,
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  ClipboardDocumentListIcon,
  QueueListIcon,
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { useInterconsultaStore } from '../stores/interconsulta';

const sidebarOpen = ref(false);
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const interconsultaStore = useInterconsultaStore();

// Close sidebar on route change
watch(() => route.path, () => {
  sidebarOpen.value = false;
});

function confirmarAcao() {
  console.log("Confirmar clicado no banner");
  interconsultaStore.triggerConfirm();
}

function desfazerAcao() {
  console.log("Desfazer clicado no banner");
  interconsultaStore.triggerUndo();
}
</script>