<template>
  <div class="space-y-6">
    <!-- Métricas do Dashboard -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card class="bg-gradient-to-br from-white to-gray-50/50 hover:shadow-md transition duration-300">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-gray-500 uppercase">Fila Total</p>
            <h3 class="text-3xl font-extrabold text-gray-800 mt-1">{{ totalPedidos }}</h3>
          </div>
          <div class="p-3 bg-blue-50 text-blue-600 rounded-full">
            <QueueListIcon class="h-6 w-6" />
          </div>
        </div>
      </Card>

      <Card class="bg-gradient-to-br from-white to-red-50/20 hover:shadow-md transition duration-300">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-red-500 uppercase">Alta Prioridade</p>
            <h3 class="text-3xl font-extrabold text-red-700 mt-1">{{ totalVermelhos }}</h3>
          </div>
          <div class="p-3 bg-red-50 text-red-600 rounded-full">
            <ExclamationTriangleIcon class="h-6 w-6" />
          </div>
        </div>
      </Card>

      <Card class="bg-gradient-to-br from-white to-green-50/20 hover:shadow-md transition duration-300">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-green-500 uppercase">Agendados</p>
            <h3 class="text-3xl font-extrabold text-green-700 mt-1">{{ totalAgendados }}</h3>
          </div>
          <div class="p-3 bg-green-50 text-green-600 rounded-full">
            <CheckCircleIcon class="h-6 w-6" />
          </div>
        </div>
      </Card>

      <Card class="bg-gradient-to-br from-white to-amber-50/20 hover:shadow-md transition duration-300">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-amber-500 uppercase">Erros de Integração</p>
            <h3 class="text-3xl font-extrabold text-amber-700 mt-1">{{ totalErros }}</h3>
          </div>
          <div class="p-3 bg-amber-50 text-amber-600 rounded-full">
            <ArrowPathIcon class="h-6 w-6" />
          </div>
        </div>
      </Card>
    </div>

    <!-- Tabela da Fila -->
    <Card>
      <template #header>
        <div class="flex justify-between items-center pb-2">
          <div>
            <h2 class="text-xl font-bold text-gray-800">Fila Digital de Regulação</h2>
            <p class="text-xs text-gray-400">Classificação pelo Motor de Regras clínica, ordenada por risco</p>
          </div>
          <Button variant="info" size="sm" :loading="interconsultaStore.loading" @click="recarregar">
            <template #icon>
              <ArrowPathIcon class="h-4 w-4" />
            </template>
            Atualizar Fila
          </Button>
        </div>
      </template>

      <!-- Abas de Navegação -->
      <div class="flex border-b border-gray-100 mb-4">
        <button 
          class="py-2.5 px-4 font-semibold text-sm transition-all duration-200 border-b-2 flex items-center gap-2 focus:outline-none"
          :class="activeTab === 'pendentes' ? 'border-blue-600 text-blue-600 font-bold' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          @click="activeTab = 'pendentes'"
        >
          <ClockIcon class="h-4 w-4" />
          Aguardando Agendamento
          <span 
            class="ml-1 px-2 py-0.5 text-xs rounded-full font-bold"
            :class="activeTab === 'pendentes' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'"
          >
            {{ pedidosPendentes.length }}
          </span>
        </button>
        <button 
          class="py-2.5 px-4 font-semibold text-sm transition-all duration-200 border-b-2 flex items-center gap-2 focus:outline-none"
          :class="activeTab === 'agendados' ? 'border-blue-600 text-blue-600 font-bold' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          @click="activeTab = 'agendados'"
        >
          <CheckCircleIcon class="h-4 w-4" />
          Enfileirados Agendados
          <span 
            class="ml-1 px-2 py-0.5 text-xs rounded-full font-bold"
            :class="activeTab === 'agendados' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'"
          >
            {{ pedidosAgendados.length }}
          </span>
        </button>
      </div>

      <p v-if="interconsultaStore.loading && pedidosExibidos.length === 0" class="text-sm text-gray-500 py-6 text-center">
        Carregando a fila de regulação...
      </p>
      <p v-else-if="pedidosExibidos.length === 0" class="text-sm text-gray-500 py-6 text-center">
        {{ activeTab === 'pendentes' ? 'Nenhum pedido de interconsulta aguardando regulação.' : 'Nenhum pedido de interconsulta agendado ainda.' }}
      </p>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 mt-2">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">CNS do Paciente</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Especialidade (AGHU)</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Gravidade Clínica</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Pontuação</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tempo de Espera</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status Integração</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Criado Em</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr 
              v-for="pedido in pedidosExibidos" 
              :key="pedido.id"
              class="hover:bg-gray-50/50 transition cursor-pointer"
              @click="selecionarPedido(pedido)"
            >
              <td class="px-4 py-3 text-sm font-medium text-gray-900">#{{ pedido.id }}</td>
              <td class="px-4 py-3 text-sm font-mono text-gray-700 font-semibold">{{ pedido.paciente_cns }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">Especialidade {{ pedido.especialidade_id }}</td>
              <td class="px-4 py-3 text-sm">
                <span :class="gravidadeClass(pedido.gravidade)" class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider">
                  {{ pedido.gravidade }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm font-semibold text-gray-900">
                {{ pedido.score_prioridade ?? 0 }} pts
              </td>
              <td class="px-4 py-3 text-sm text-red-600 font-medium">
                {{ pedido.dias_na_fila ?? 0 }} dias
              </td>
              <td class="px-4 py-3 text-sm">
                <span :class="statusClass(pedido.status)" class="inline-flex px-2 py-0.5 rounded text-xs font-medium uppercase">
                  {{ pedido.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500">{{ formatarData(pedido.criado_em) }}</td>
              <td class="px-4 py-3 text-sm text-center flex items-center justify-center space-x-2" @click.stop>
                <button
                  title="Visualizar Detalhes"
                  class="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition"
                  @click="selecionarPedido(pedido)"
                >
                  <EyeIcon class="h-5 w-5" />
                </button>
                <button
                  v-if="pedido.status !== 'AGENDADO'"
                  title="Marcar como Agendado"
                  class="p-1.5 text-green-600 hover:bg-green-50 rounded transition"
                  @click="confirmarAgendamento(pedido)"
                >
                  <CheckIcon class="h-5 w-5" />
                </button>
                <button
                  v-if="pedido.status === 'ERRO'"
                  title="Re-enviar para o AGHU"
                  class="p-1.5 text-amber-600 hover:bg-amber-50 rounded transition animate-pulse"
                  @click="reprocessar(pedido)"
                >
                  <ArrowPathIcon class="h-5 w-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Drawer/Modal de Detalhes da Regulação -->
    <div 
      v-if="pedidoSelecionado" 
      class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex justify-end transition-opacity duration-300"
      @click="fecharDetalhes"
    >
      <div 
        class="bg-white w-full max-w-md h-full shadow-2xl p-6 overflow-y-auto flex flex-col justify-between"
        @click.stop
      >
        <div class="space-y-6">
          <div class="flex justify-between items-center border-b pb-4">
            <h3 class="text-lg font-bold text-gray-800">Detalhes da Solicitação #{{ pedidoSelecionado.id }}</h3>
            <button class="text-gray-400 hover:text-gray-600 text-2xl" @click="fecharDetalhes">&times;</button>
          </div>

          <!-- Informações Principais -->
          <div class="bg-gray-50 rounded-lg p-4 space-y-3">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">CNS do Paciente (Decifrado)</p>
              <p class="text-base font-mono font-bold text-gray-800 mt-0.5 select-all">{{ pedidoSelecionado.paciente_cns }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">Especialidade ID</p>
                <p class="text-sm font-semibold text-gray-800 mt-0.5">{{ pedidoSelecionado.especialidade_id }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">CRM Solicitante</p>
                <p class="text-sm font-semibold text-gray-800 mt-0.5">{{ pedidoSelecionado.medico_solicitante_crm }}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">Criado Em</p>
                <p class="text-xs text-gray-600 mt-0.5">{{ formatarData(pedidoSelecionado.criado_em) }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">Última Atualização</p>
                <p class="text-xs text-gray-600 mt-0.5">{{ formatarData(pedidoSelecionado.atualizado_em) }}</p>
              </div>
            </div>
          </div>

          <!-- Gravidade e Status -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase mb-1">Gravidade Clínica</p>
              <span :class="gravidadeClass(pedidoSelecionado.gravidade)" class="inline-flex px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                {{ pedidoSelecionado.gravidade }}
              </span>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase mb-1">Status de Integração</p>
              <span :class="statusClass(pedidoSelecionado.status)" class="inline-flex px-3 py-1 rounded text-xs font-medium uppercase">
                {{ pedidoSelecionado.status }}
              </span>
            </div>
          </div>

          <!-- Pontuação e Tempo de Espera -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase mb-1">Pontuação</p>
              <p class="text-sm font-bold text-gray-800">{{ pedidoSelecionado.score_prioridade ?? 0 }} pts</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase mb-1">Tempo de Espera</p>
              <p class="text-sm font-bold text-red-600">{{ pedidoSelecionado.dias_na_fila ?? 0 }} dias</p>
            </div>
          </div>

          <!-- Sintomas Informados -->
          <div>
            <p class="text-xs font-semibold text-gray-400 uppercase mb-2">Sintomas Justificativos</p>
            <div v-if="obterSintomas(pedidoSelecionado).length === 0" class="text-sm text-gray-500 italic">
              Nenhum sintoma estruturado informado.
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <span 
                v-for="sintoma in obterSintomas(pedidoSelecionado)" 
                :key="sintoma.id"
                class="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-100 font-medium"
              >
                {{ sintoma.id }} — {{ sintoma.nome }}
              </span>
            </div>
          </div>
        </div>

        <!-- Ações no Drawer -->
        <div class="border-t pt-4 space-y-2 mt-6">
          <Button 
            v-if="pedidoSelecionado.status !== 'AGENDADO'"
            variant="success" 
            class="w-full"
            :loading="executingAction"
            @click="confirmarAgendamento(pedidoSelecionado)"
          >
            <template #icon>
              <CheckIcon class="h-5 w-5" />
            </template>
            Marcar como Agendado
          </Button>

          <Button 
            v-if="pedidoSelecionado.status === 'ERRO'"
            variant="warning" 
            class="w-full"
            :loading="executingAction"
            @click="reprocessar(pedidoSelecionado)"
          >
            <template #icon>
              <ArrowPathIcon class="h-5 w-5" />
            </template>
            Re-enviar para o AGHU
          </Button>

          <Button 
            variant="default" 
            class="w-full hover:bg-gray-100" 
            @click="fecharDetalhes"
          >
            Fechar
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';
import {
  QueueListIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon,
  CheckIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import { useInterconsultaStore, InterconsultaPedido } from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

const pedidoSelecionado = ref<InterconsultaPedido | null>(null);
const executingAction = ref(false);

const activeTab = ref<'pendentes' | 'agendados'>('pendentes');

const pedidos = computed(() => interconsultaStore.pedidos);

const pedidosPendentes = computed(() => 
  pedidos.value.filter((p) => p.status === 'PENDENTE' || p.status === 'ENFILEIRADO' || p.status === 'ERRO')
);

const pedidosAgendados = computed(() => 
  pedidos.value.filter((p) => p.status === 'AGENDADO')
);

const pedidosExibidos = computed(() => 
  activeTab.value === 'pendentes' ? pedidosPendentes.value : pedidosAgendados.value
);

// Métricas baseadas na fila atual carregada
const totalPedidos = computed(() => pedidos.value.length);
const totalVermelhos = computed(() => pedidos.value.filter((p) => p.gravidade === 'VERMELHO').length);
const totalAgendados = computed(() => pedidos.value.filter((p) => p.status === 'AGENDADO').length);
const totalErros = computed(() => pedidos.value.filter((p) => p.status === 'ERRO').length);

function selecionarPedido(pedido: InterconsultaPedido) {
  pedidoSelecionado.value = pedido;
}

function fecharDetalhes() {
  pedidoSelecionado.value = null;
}

function obterSintomas(pedido: InterconsultaPedido): any[] {
  if (!pedido.sintomas_json) return [];
  if (typeof pedido.sintomas_json === 'string') {
    try {
      return JSON.parse(pedido.sintomas_json);
    } catch {
      return [];
    }
  }
  return pedido.sintomas_json;
}

function gravidadeClass(gravidade: string): string {
  switch (gravidade) {
    case 'VERMELHO':
      return 'bg-red-100 text-red-800 border border-red-200';
    case 'AMARELO':
      return 'bg-amber-100 text-amber-800 border border-amber-200';
    case 'VERDE':
      return 'bg-green-100 text-green-800 border border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200';
  }
}

function statusClass(status: string): string {
  switch (status) {
    case 'AGENDADO':
      return 'bg-green-50 text-green-700 border border-green-200';
    case 'ERRO':
      return 'bg-red-50 text-red-700 border border-red-200';
    case 'ENFILEIRADO':
      return 'bg-blue-50 text-blue-700 border border-blue-200';
    case 'PENDENTE':
    default:
      return 'bg-gray-50 text-gray-600 border border-gray-200';
  }
}

function formatarData(value?: string | null): string {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('pt-BR');
}

async function recarregar() {
  try {
    await interconsultaStore.listarPedidos();
  } catch {
    toast.error(interconsultaStore.error ?? 'Falha ao carregar a fila de regulação.');
  }
}

async function confirmarAgendamento(pedido: InterconsultaPedido) {
  executingAction.value = true;
  try {
    await interconsultaStore.atualizarStatusPedido(pedido.id, 'AGENDADO');
    toast.success(`Pedido #${pedido.id} marcado como agendado com sucesso.`);
    fecharDetalhes();
    await recarregar();
  } catch {
    toast.error(interconsultaStore.error ?? 'Não foi possível atualizar o status do pedido.');
  } finally {
    executingAction.value = false;
  }
}

async function reprocessar(pedido: InterconsultaPedido) {
  executingAction.value = true;
  try {
    await interconsultaStore.reprocessarPedido(pedido.id);
    toast.success(`Tentativa de envio re-enfileirada para o pedido #${pedido.id}.`);
    fecharDetalhes();
    await recarregar();
  } catch {
    toast.error(interconsultaStore.error ?? 'Falha ao disparar retry do pedido.');
  } finally {
    executingAction.value = false;
  }
}

onMounted(() => {
  recarregar();
});
</script>
