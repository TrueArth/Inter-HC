<template>
  <div class="space-y-6" v-if="authStore.isAdmin">
    <!-- Header Area -->
    <div class="flex justify-between items-center bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <UserGroupIcon class="h-8 w-8 text-blue-600" />
          Gestão de Usuários
        </h1>
        <p class="text-sm text-gray-500 mt-1">Crie novos usuários e gerencie perfis de acesso localmente.</p>
      </div>
      <Button variant="primary" @click="abrirModalCriar">
        <template #icon>
          <UserPlusIcon class="h-5 w-5" />
        </template>
        Novo Usuário
      </Button>
    </div>

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
import { ref, onMounted } from 'vue';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  PencilSquareIcon, 
  TrashIcon 
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const users = ref<any[]>([]);
const loading = ref(false);
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

onMounted(() => {
  carregarUsuarios();
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