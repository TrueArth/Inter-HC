<template>
  <div class="space-y-6" v-if="authStore.isAdmin">
    <!-- Header Area -->
    <div class="flex justify-between items-center bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <UserGroupIcon v-if="abaAtiva === 'usuarios'" class="h-8 w-8 text-blue-600" />
          <ChartBarIcon v-else class="h-8 w-8 text-blue-600" />
          {{ abaAtiva === 'usuarios' ? 'Gestão de Usuários' : 'Estatísticas de Regulação' }}
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          {{ abaAtiva === 'usuarios' ? 'Crie novos usuários e gerencie perfis de acesso localmente.' : 'Acompanhe indicadores clínicos e auditoria de solicitações.' }}
        </p>
      </div>
      <div>
        <Button v-if="abaAtiva === 'usuarios'" variant="primary" @click="abrirModalCriar">
          <template #icon>
            <UserPlusIcon class="h-5 w-5" />
          </template>
          Novo Usuário
        </Button>
        <Button v-else variant="default" @click="carregarEstatisticas" :loading="loadingStats">
          Atualizar Dados
        </Button>
      </div>
    </div>

    <!-- Tab Selector -->
    <div class="flex gap-6 border-b border-gray-200">
      <button 
        @click="alterarAba('usuarios')" 
        :class="abaAtiva === 'usuarios' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Gerenciar Usuários
      </button>
      <button 
        @click="alterarAba('estatisticas')" 
        :class="abaAtiva === 'estatisticas' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Estatísticas de Regulação
      </button>
    </div>

    <!-- Tab 1: Gerenciar Usuários -->
    <div v-show="abaAtiva === 'usuarios'" class="space-y-6">
      <!-- Users Table Card -->
      <Card>
        <template #header>
          <div class="pb-2">
            <h2 class="text-lg font-semibold text-gray-700">Usuários Ativos no Sistema</h2>
            <p class="text-xs text-gray-400">Lista de credenciais locais cadastradas e seus cargos associados.</p>
          </div>
        </template>

        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p class="text-sm text-gray-500 mt-2">Carregando usuários...</p>
        </div>

        <div v-else-if="users.length === 0" class="text-center py-12">
          <UserGroupIcon class="h-12 w-12 text-gray-300 mx-auto" />
          <p class="text-sm text-gray-500 mt-2">Nenhum usuário local cadastrado.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 mt-2">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Username</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nome Completo</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">E-mail</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Perfil / Cargo</th>
                <th class="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50/50 transition">
                <td class="px-6 py-4 text-sm font-semibold text-gray-900 font-mono">@{{ u.username }}</td>
                <td class="px-6 py-4 text-sm text-gray-600">{{ u.display_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ u.email || 'N/A' }}</td>
                <td class="px-6 py-4 text-sm">
                  <span :class="roleClass(u.role)" class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider">
                    {{ roleLabel(u.role) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-center flex justify-center gap-2">
                  <button 
                    @click="abrirModalEditar(u)" 
                    class="p-2 rounded text-blue-600 hover:bg-blue-50 transition" 
                    title="Editar Usuário"
                  >
                    <PencilSquareIcon class="h-5 w-5" />
                  </button>
                  <button 
                    v-if="u.username !== 'admin'"
                    @click="confirmarInativar(u)" 
                    class="p-2 rounded text-red-600 hover:bg-red-50 transition" 
                    title="Desativar Usuário"
                  >
                    <TrashIcon class="h-5 w-5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- Tab 2: Estatísticas de Regulação -->
    <div v-show="abaAtiva === 'estatisticas'" class="space-y-6">
      <div v-if="loadingStats" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p class="text-sm text-gray-500 mt-2">Processando dados e estatísticas...</p>
      </div>

      <div v-else-if="!stats" class="text-center py-12 bg-white rounded-xl border border-gray-200">
        <p class="text-sm text-gray-500">Erro ao carregar estatísticas do banco de dados.</p>
      </div>

      <div v-else class="space-y-6">
        <!-- Highlights Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Especialidade Mais Solicitada</p>
              <h3 class="text-2xl font-bold text-gray-800 mt-1">{{ stats.top_specialty.name }}</h3>
              <p class="text-xs text-blue-600 font-semibold mt-1">{{ stats.top_specialty.count }} solicitações</p>
            </div>
            <div class="bg-blue-50 text-blue-600 p-3 rounded-lg">
              <ChartBarIcon class="h-6 w-6" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total de Solicitações Ativas</p>
              <h3 class="text-2xl font-bold text-gray-800 mt-1">{{ totalSolicitacoes }}</h3>
              <p class="text-xs text-gray-400 mt-1">Aguardando regulação/agendadas</p>
            </div>
            <div class="bg-gray-50 text-gray-600 p-3 rounded-lg">
              <InboxIcon class="h-6 w-6" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total de Casos Indevidos</p>
              <h3 class="text-2xl font-bold text-red-600 mt-1">{{ totalIndevidas }}</h3>
              <p class="text-xs text-red-400 font-semibold mt-1">Casos de baixa complexidade (Verde)</p>
            </div>
            <div class="bg-red-50 text-red-600 p-3 rounded-lg">
              <ExclamationTriangleIcon class="h-6 w-6" />
            </div>
          </div>
        </div>

        <!-- Detail Metrics Lists -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Specialties Distribution -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Demanda por Especialidade</h3>
              <p class="text-xs text-gray-400 mt-0.5">Ranking de solicitações por especialidade.</p>
            </template>
            
            <div class="space-y-4 mt-4" v-if="stats.specialties_distribution.length > 0">
              <div v-for="item in stats.specialties_distribution" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-gray-700">{{ item.name }}</span>
                  <span class="font-bold text-blue-600">{{ item.count }}</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div 
                    class="bg-blue-600 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxSpecialtyCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Nenhum dado registrado.</p>
          </Card>

          <!-- Top Requesting Doctors -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Médicos Mais Solicitantes</h3>
              <p class="text-xs text-gray-400 mt-0.5">Volume total de solicitações enviadas.</p>
            </template>

            <div class="space-y-4 mt-4" v-if="stats.top_doctors.length > 0">
              <div v-for="item in stats.top_doctors" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-gray-700">{{ item.name }}</span>
                  <span class="font-bold text-gray-900">{{ item.count }}</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div 
                    class="bg-gray-600 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxDoctorCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Nenhum médico registrou pedidos.</p>
          </Card>

          <!-- Inappropriate Requests (VERDE) ranking -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-red-700 flex items-center gap-1">
                <ExclamationTriangleIcon class="h-5 w-5 text-red-500" />
                Casos Indevidos por Médico
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">Médicos com maior taxa de solicitações VERDE.</p>
            </template>

            <div class="space-y-4 mt-4" v-if="stats.inappropriate_doctors.length > 0">
              <div v-for="item in stats.inappropriate_doctors" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-red-700">{{ item.name }}</span>
                  <span class="font-bold text-red-600">{{ item.count }}</span>
                </div>
                <div class="w-full bg-red-50 rounded-full h-1.5">
                  <div 
                    class="bg-red-500 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxInappropriateCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Excelente! Nenhuma solicitação indevida registrada.</p>
          </Card>
        </div>
      </div>
    </div>

    <!-- Modal Criar -->
    <Modal :show="mostrarModalCriar" @close="mostrarModalCriar = false">
      <template #header>Cadastrar Novo Usuário</template>
      
      <form @submit.prevent="salvarNovoUsuario" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome de Usuário (login)</label>
          <input 
            type="text" 
            v-model="novoUser.username" 
            class="form-control" 
            required 
            placeholder="Ex: joao_medico"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">Senha</label>
          <input 
            type="password" 
            v-model="novoUser.password" 
            class="form-control" 
            required 
            placeholder="Mínimo 6 caracteres"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Nome de Exibição (Completo)</label>
          <input 
            type="text" 
            v-model="novoUser.display_name" 
            class="form-control" 
            required 
            placeholder="Ex: Dr. João da Silva"
          />
        </div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input 
            type="email" 
            v-model="novoUser.email" 
            class="form-control" 
            placeholder="Ex: joao@ufpe.br"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Perfil de Acesso</label>
          <select v-model="novoUser.role" class="form-control" required>
            <option value="medico">Médico Solicitante</option>
            <option value="regulador">Regulador (Central de Marcação)</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <p v-if="erroForm" class="text-xs text-red-500 font-semibold">{{ erroForm }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalCriar = false">Cancelar</Button>
        <Button variant="primary" :loading="salvando" @click="salvarNovoUsuario">Salvar</Button>
      </template>
    </Modal>

    <!-- Modal Editar -->
    <Modal :show="mostrarModalEditar" @close="mostrarModalEditar = false">
      <template #header>Editar Usuário: @{{ userEditando?.username }}</template>
      
      <form @submit.prevent="salvarEdicaoUsuario" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome de Exibição (Completo)</label>
          <input 
            type="text" 
            v-model="userEditandoForm.display_name" 
            class="form-control" 
            required 
            placeholder="Ex: Dr. João da Silva"
          />
        </div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input 
            type="email" 
            v-model="userEditandoForm.email" 
            class="form-control" 
            placeholder="Ex: joao@ufpe.br"
          />
        </div>

        <div class="form-group" v-if="userEditando?.username !== 'admin'">
          <label class="form-label">Perfil de Acesso</label>
          <select v-model="userEditandoForm.role" class="form-control" required>
            <option value="medico">Médico Solicitante</option>
            <option value="regulador">Regulador (Central de Marcação)</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <p v-if="erroForm" class="text-xs text-red-500 font-semibold">{{ erroForm }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalEditar = false">Cancelar</Button>
        <Button variant="primary" :loading="salvando" @click="salvarEdicaoUsuario">Salvar Alterações</Button>
      </template>
    </Modal>
  </div>
  <div v-else class="text-center py-12">
    <Card class="max-w-md mx-auto">
      <h1 class="text-2xl font-bold text-red-600">Acesso Negado</h1>
      <p class="mt-4 text-gray-500">Você não tem privilégios suficientes para acessar a área administrativa.</p>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  PencilSquareIcon, 
  TrashIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  InboxIcon
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const abaAtiva = ref('usuarios');
const users = ref<any[]>([]);
const stats = ref<any>(null);

const loading = ref(false);
const loadingStats = ref(false);
const salvando = ref(false);
const erroForm = ref('');

// Modais
const mostrarModalCriar = ref(false);
const mostrarModalEditar = ref(false);

// Forms
const novoUser = ref({
  username: '',
  password: '',
  display_name: '',
  email: '',
  role: 'medico'
});

const userEditando = ref<any>(null);
const userEditandoForm = ref({
  display_name: '',
  email: '',
  role: 'medico'
});

const carregarUsuarios = async () => {
  if (!authStore.isAdmin) return;
  loading.value = true;
  try {
    const { data } = await api.get('/api/admin/users');
    users.value = data;
  } catch (error: any) {
    console.error("Erro ao carregar usuários:", error);
  } finally {
    loading.value = false;
  }
};

const carregarEstatisticas = async () => {
  if (!authStore.isAdmin) return;
  loadingStats.value = true;
  try {
    const { data } = await api.get('/api/admin/statistics');
    stats.value = data;
  } catch (error: any) {
    console.error("Erro ao carregar estatísticas:", error);
  } finally {
    loadingStats.value = false;
  }
};

const alterarAba = (aba: string) => {
  abaAtiva.value = aba;
  if (aba === 'usuarios') {
    carregarUsuarios();
  } else if (aba === 'estatisticas') {
    carregarEstatisticas();
  }
};

onMounted(() => {
  carregarUsuarios();
});

// Computed Stats Properties
const totalSolicitacoes = computed(() => {
  if (!stats.value) return 0;
  return stats.value.specialties_distribution.reduce((acc: number, item: any) => acc + item.count, 0);
});

const totalIndevidas = computed(() => {
  if (!stats.value) return 0;
  return stats.value.inappropriate_doctors.reduce((acc: number, item: any) => acc + item.count, 0);
});

const maxSpecialtyCount = computed(() => {
  if (!stats.value || stats.value.specialties_distribution.length === 0) return 1;
  return Math.max(...stats.value.specialties_distribution.map((item: any) => item.count));
});

const maxDoctorCount = computed(() => {
  if (!stats.value || stats.value.top_doctors.length === 0) return 1;
  return Math.max(...stats.value.top_doctors.map((item: any) => item.count));
});

const maxInappropriateCount = computed(() => {
  if (!stats.value || stats.value.inappropriate_doctors.length === 0) return 1;
  return Math.max(...stats.value.inappropriate_doctors.map((item: any) => item.count));
});

const roleLabel = (role: string) => {
  if (role === 'admin') return 'Administrador';
  if (role === 'medico') return 'Médico';
  if (role === 'regulador') return 'Regulador';
  return role;
};

const roleClass = (role: string) => {
  if (role === 'admin') return 'bg-purple-100 text-purple-700';
  if (role === 'medico') return 'bg-green-100 text-green-700';
  if (role === 'regulador') return 'bg-blue-100 text-blue-700';
  return 'bg-gray-100 text-gray-700';
};

const abrirModalCriar = () => {
  novoUser.value = {
    username: '',
    password: '',
    display_name: '',
    email: '',
    role: 'medico'
  };
  erroForm.value = '';
  mostrarModalCriar.value = true;
};

const salvarNovoUsuario = async () => {
  erroForm.value = '';
  salvando.value = true;
  try {
    await api.post('/api/admin/users', novoUser.value);
    mostrarModalCriar.value = false;
    await carregarUsuarios();
  } catch (error: any) {
    erroForm.value = error.response?.data?.detail || "Erro ao salvar usuário. Verifique se o username já existe.";
  } finally {
    salvando.value = false;
  }
};

const abrirModalEditar = (u: any) => {
  userEditando.value = u;
  userEditandoForm.value = {
    display_name: u.display_name,
    email: u.email || '',
    role: u.role
  };
  erroForm.value = '';
  mostrarModalEditar.value = true;
};

const salvarEdicaoUsuario = async () => {
  erroForm.value = '';
  salvando.value = true;
  try {
    await api.put(`/api/admin/users/${userEditando.value.id}`, userEditandoForm.value);
    mostrarModalEditar.value = false;
    await carregarUsuarios();
  } catch (error: any) {
    erroForm.value = error.response?.data?.detail || "Erro ao salvar alterações.";
  } finally {
    salvando.value = false;
  }
};

const confirmarInativar = async (u: any) => {
  if (confirm(`Tem certeza que deseja inativar/desativar o usuário @${u.username}?`)) {
    try {
      await api.delete(`/api/admin/users/${u.id}`);
      await carregarUsuarios();
    } catch (error: any) {
      alert("Erro ao inativar usuário.");
    }
  }
};
</script>