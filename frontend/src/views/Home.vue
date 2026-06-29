<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-8 rounded-2xl shadow-md border border-blue-800">
      <h1 class="text-3xl font-extrabold flex items-center gap-2">
        <span>Olá, {{ displayName }}!</span>
      </h1>
      <p class="mt-2 text-blue-100 max-w-xl">
        Bem-vindo ao Portal InterHC do Hospital das Clínicas da UFPE. Utilize os atalhos abaixo para acessar as funcionalidades do sistema de acordo com o seu perfil.
      </p>
    </div>

    <!-- Quick Actions Cards -->
    <div class="space-y-4">
      <h2 class="text-xl font-bold text-gray-800">Ações Rápidas</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Interconsultas Card (Doctor/Admin) -->
        <div 
          v-if="authStore.isAdmin || authStore.isMedico"
          @click="irPara('/interconsultas')"
          class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div class="bg-blue-50 text-blue-600 p-3 rounded-lg w-fit group-hover:bg-blue-100 transition">
              <ClipboardDocumentListIcon class="h-6 w-6" />
            </div>
            <h3 class="text-lg font-bold text-gray-800 mt-4 group-hover:text-blue-700 transition">InterHC</h3>
            <p class="text-sm text-gray-500 mt-1">Solicite novas interconsultas médicas e acompanhe a fila de prioridades clínicas.</p>
          </div>
          <div class="mt-6 flex items-center text-xs font-bold text-blue-600 group-hover:translate-x-1 transition duration-200">
            Acessar Painel <ArrowRightIcon class="h-4 w-4 ml-1" />
          </div>
        </div>

        <!-- Central de Marcação Card (Regulator/Admin) -->
        <div 
          v-if="authStore.isAdmin || authStore.isRegulador"
          @click="irPara('/central-marcacao')"
          class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div class="bg-blue-50 text-blue-600 p-3 rounded-lg w-fit group-hover:bg-blue-100 transition">
              <QueueListIcon class="h-6 w-6" />
            </div>
            <h3 class="text-lg font-bold text-gray-800 mt-4 group-hover:text-blue-700 transition">Central de Marcação</h3>
            <p class="text-sm text-gray-500 mt-1">Gerencie a fila regulada, realize agendamentos manuais e atualize o censo de consultas.</p>
          </div>
          <div class="mt-6 flex items-center text-xs font-bold text-blue-600 group-hover:translate-x-1 transition duration-200">
            Acessar Central <ArrowRightIcon class="h-4 w-4 ml-1" />
          </div>
        </div>



        <!-- Admin Card (Admin) -->
        <div 
          v-if="authStore.isAdmin"
          @click="irPara('/admin')"
          class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div class="bg-blue-50 text-blue-600 p-3 rounded-lg w-fit group-hover:bg-blue-100 transition">
              <UserGroupIcon class="h-6 w-6" />
            </div>
            <h3 class="text-lg font-bold text-gray-800 mt-4 group-hover:text-blue-700 transition">Administrador</h3>
            <p class="text-sm text-gray-500 mt-1">Gerencie credenciais locais de acesso, perfis de usuários e acesse o painel estatístico.</p>
          </div>
          <div class="mt-6 flex items-center text-xs font-bold text-blue-600 group-hover:translate-x-1 transition duration-200">
            Configurações <ArrowRightIcon class="h-4 w-4 ml-1" />
          </div>
        </div>
      </div>
    </div>

    <!-- User Profile Editing (Meu Perfil) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <Card class="lg:col-span-2 shadow-sm border border-gray-200">
        <template #header>
          <div class="pb-2">
            <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
              <UserIcon class="h-5 w-5 text-blue-600" />
              Meu Perfil
            </h2>
            <p class="text-xs text-gray-500 mt-0.5">Atualize seus dados cadastrais e senha de acesso local.</p>
          </div>
        </template>

        <form @submit.prevent="atualizarPerfil" class="space-y-4 mt-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="form-label">Nome Completo</label>
              <input 
                type="text" 
                v-model="perfilForm.display_name" 
                class="form-control" 
                required 
                placeholder="Ex: Dr. Carlos Silva"
              />
            </div>
            <div class="form-group">
              <label class="form-label">E-mail</label>
              <input 
                type="email" 
                v-model="perfilForm.email" 
                class="form-control" 
                required 
                placeholder="Ex: carlos@ufpe.br"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="form-label">Nova Senha (opcional)</label>
              <input 
                type="password" 
                v-model="perfilForm.password" 
                class="form-control" 
                placeholder="Preencha apenas se quiser alterar"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Cargo / Perfil</label>
              <input 
                type="text" 
                :value="cargoLabel" 
                class="form-control bg-gray-50 text-gray-500 border-gray-200" 
                disabled
              />
            </div>
          </div>

          <div class="flex justify-end pt-2">
            <Button variant="primary" type="submit" :loading="salvando">
              Salvar Alterações
            </Button>
          </div>

          <!-- Alert Messages -->
          <div v-if="erroMsg" class="p-3 bg-red-50 text-red-700 text-sm font-semibold rounded-lg">
            {{ erroMsg }}
          </div>
          <div v-if="sucessoMsg" class="p-3 bg-green-50 text-green-700 text-sm font-semibold rounded-lg flex items-center gap-1">
            <CheckCircleIcon class="h-5 w-5" />
            {{ sucessoMsg }}
          </div>
        </form>
      </Card>

      <!-- User Badge Summary Info -->
      <Card class="shadow-sm border border-gray-200 h-fit bg-gradient-to-br from-gray-50 to-blue-50/20">
        <div class="text-center py-6">
          <div class="inline-flex justify-center items-center h-16 w-16 rounded-full bg-blue-100 text-blue-700 font-extrabold text-2xl border-2 border-blue-200">
            {{ displayNameInitials }}
          </div>
          <h3 class="text-lg font-bold text-gray-800 mt-4">{{ displayName }}</h3>
          <p class="text-xs text-gray-400 font-mono mt-0.5">@{{ authStore.user?.username }}</p>
          
          <div class="mt-6 border-t border-gray-200/60 pt-4 text-left space-y-2 text-sm text-gray-600">
            <div class="flex justify-between">
              <span class="text-gray-400">Perfil:</span>
              <span class="font-semibold uppercase text-xs px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 font-bold">
                {{ authStore.user?.role || 'Usuário' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">E-mail:</span>
              <span class="font-medium truncate max-w-[180px]">{{ authStore.user?.email || 'Sem e-mail' }}</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  ClipboardDocumentListIcon, 
  QueueListIcon, 
  UserGroupIcon,
  UserIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline';

const router = useRouter();
const authStore = useAuthStore();

const salvando = ref(false);
const erroMsg = ref('');
const sucessoMsg = ref('');

const perfilForm = ref({
  display_name: '',
  email: '',
  password: ''
});

onMounted(() => {
  if (authStore.user) {
    perfilForm.value.display_name = authStore.user.displayName?.[0] || authStore.user.username;
    perfilForm.value.email = authStore.user.email || '';
  }
});

const displayName = computed(() => {
  return authStore.user?.displayName?.[0] || authStore.user?.username || 'Usuário';
});

const displayNameInitials = computed(() => {
  const name = displayName.value;
  if (!name) return 'U';
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
});

const cargoLabel = computed(() => {
  const role = authStore.user?.role;
  if (role === 'admin') return 'Administrador do Sistema';
  if (role === 'medico') return 'Médico Regulado';
  if (role === 'regulador') return 'Central de Regulação';
  return 'Usuário Comum';
});

const irPara = (rota: string) => {
  router.push(rota);
};

const atualizarPerfil = async () => {
  erroMsg.value = '';
  sucessoMsg.value = '';
  salvando.value = true;
  
  try {
    const payload = {
      display_name: perfilForm.value.display_name,
      email: perfilForm.value.email,
      password: perfilForm.value.password || undefined
    };

    await api.put('/api/users/profile', payload);
    
    // Atualiza os dados locais do usuário chamando fetchUser no store
    await authStore.fetchUser();
    
    sucessoMsg.value = 'Perfil atualizado com sucesso!';
    perfilForm.value.password = ''; // Limpa a senha
  } catch (error: any) {
    console.error("Erro ao atualizar perfil:", error);
    erroMsg.value = error.response?.data?.detail || 'Ocorreu um erro ao atualizar os seus dados.';
  } finally {
    salvando.value = false;
  }
};
</script>
