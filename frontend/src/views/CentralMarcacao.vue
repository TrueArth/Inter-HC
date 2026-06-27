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

    <!-- Abas de Especialidades (Seleção de Fila Própria) -->
    <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-3">
      <div>
        <h4 class="text-sm font-bold text-gray-800">Filas de Regulação por Especialidade</h4>
        <p class="text-xs text-gray-400">Clique na especialidade para gerenciar sua fila de regulação individual</p>
      </div>
      
      <div class="flex flex-wrap gap-2 pt-1">
        <button
          v-for="esp in especialidadesComPedidos"
          :key="esp.id"
          type="button"
          class="px-4 py-2 text-xs font-bold rounded-lg transition duration-200 focus:outline-none flex items-center gap-2 border"
          :class="[
            especialidadeFiltro === esp.id 
              ? 'bg-blue-600 border-blue-600 text-white shadow-sm' 
              : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100 hover:text-gray-850'
          ]"
          @click="selecionarEspecialidadeFila(esp.id)"
        >
          {{ esp.nome }}
          <span 
            class="px-2 py-0.5 text-[10px] rounded-full font-extrabold transition-colors duration-200"
            :class="[
              especialidadeFiltro === esp.id 
                ? 'bg-blue-700 text-white' 
                : 'bg-gray-200 text-gray-700'
            ]"
          >
            {{ contarPedidosPorEspecialidade(esp.id) }}
          </span>
        </button>
      </div>
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
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Paciente / PREP</th>
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
              <td class="px-4 py-3 text-sm">
                <div class="font-mono text-gray-700 font-semibold">{{ pedido.paciente_prep }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ pedido.paciente_nome || 'Não identificado' }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ obterNomeEspecialidade(pedido.especialidade_id) }}</td>
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">Nome do Paciente</p>
                <p class="text-sm font-semibold text-gray-800 mt-0.5">{{ pedidoSelecionado.paciente_nome || 'Não identificado' }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">PREP do Paciente (Decifrado)</p>
                <p class="text-sm font-mono font-bold text-gray-800 mt-0.5 select-all">{{ pedidoSelecionado.paciente_prep }}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-semibold text-gray-400 uppercase">Especialidade</p>
                <p class="text-sm font-semibold text-gray-800 mt-0.5">{{ obterNomeEspecialidade(pedidoSelecionado.especialidade_id) }}</p>
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
            <div v-if="pedidoSelecionado.marcado_por" class="pt-2 border-t border-gray-100">
              <p class="text-xs font-semibold text-gray-400 uppercase">Marcado Por (Regulação)</p>
              <p class="text-sm font-semibold text-blue-700 mt-0.5">@{{ pedidoSelecionado.marcado_por }}</p>
            </div>
            <div v-if="pedidoSelecionado.data_consulta" class="pt-2 border-t border-gray-100">
              <p class="text-xs font-semibold text-gray-400 uppercase">Data da Consulta</p>
              <p class="text-sm font-semibold text-green-700 mt-0.5">{{ formatarDataSemHora(pedidoSelecionado.data_consulta) }}</p>
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
        </div>
      </div>
    </div>

    <!-- Modal Agendamento -->
    <Modal :show="mostrarModalAgendamento" @close="mostrarModalAgendamento = false">
      <template #header>Confirmar Data da Consulta</template>
      
      <div class="space-y-4 py-2">
        <p class="text-sm text-gray-500">
          Selecione a data agendada para a consulta. Horários não são registrados, apenas o dia da consulta.
        </p>

        <!-- Calendário Customizado -->
        <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
          <!-- Cabeçalho do Calendário -->
          <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
            <button 
              type="button" 
              class="p-1.5 hover:bg-gray-200 rounded-full transition text-gray-600 flex items-center justify-center focus:outline-none"
              @click="navegarMes(-1)"
            >
              <ChevronLeftIcon class="h-4 w-4" />
            </button>
            <span class="text-xs font-bold text-gray-700 uppercase tracking-wide">
              {{ nomesMeses[mesAtual] }} {{ anoAtual }}
            </span>
            <button 
              type="button" 
              class="p-1.5 hover:bg-gray-200 rounded-full transition text-gray-600 flex items-center justify-center focus:outline-none"
              @click="navegarMes(1)"
            >
              <ChevronRightIcon class="h-4 w-4" />
            </button>
          </div>

          <!-- Grade de Dias -->
          <div class="p-3">
            <div class="grid grid-cols-7 gap-1 text-center mb-2">
              <span 
                v-for="diaSem in diasDaSemana" 
                :key="diaSem" 
                class="text-xs font-bold text-gray-400 uppercase py-1"
              >
                {{ diaSem }}
              </span>
            </div>
            
            <div class="grid grid-cols-7 gap-1.5">
              <button
                v-for="(diaObj, idx) in diasNoCalendario"
                :key="idx"
                type="button"
                :disabled="diaObj.desabilitado || !diaObj.dia"
                class="w-full aspect-square flex items-center justify-center rounded-full text-xs font-semibold transition"
                :class="[
                  !diaObj.dia ? 'invisible pointer-events-none' : '',
                  diaObj.desabilitado ? 'text-gray-300 cursor-not-allowed bg-transparent' : 'text-gray-700 hover:bg-blue-50 cursor-pointer',
                  isHoje(diaObj.dataCompleta) && !isSelecionado(diaObj.dataCompleta) ? 'border border-blue-400 text-blue-600' : '',
                  isSelecionado(diaObj.dataCompleta) ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700 font-bold' : ''
                ]"
                @click="selecionarDataCalendario(diaObj)"
              >
                {{ diaObj.dia }}
              </button>
            </div>
          </div>
        </div>

        <!-- Data Selecionada por Extenso -->
        <div class="bg-blue-50/50 border border-blue-100 rounded-lg p-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-blue-600">
              <CheckCircleIcon class="h-5 w-5" />
            </span>
            <span class="text-xs font-semibold text-blue-800">Data de Marcação:</span>
          </div>
          <span class="text-xs font-bold text-blue-900 bg-white border border-blue-200 px-2.5 py-1 rounded shadow-sm">
            {{ dataFormatadaPorExtenso }}
          </span>
        </div>
      </div>

      <template #footer>
        <Button variant="default" @click="mostrarModalAgendamento = false">Cancelar</Button>
        <Button variant="success" :loading="executingAction" @click="salvarAgendamento">Confirmar Agendamento</Button>
      </template>
    </Modal>
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
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import { useInterconsultaStore, InterconsultaPedido } from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

function obterNomeEspecialidade(id: number): string {
  const esp = interconsultaStore.especialidades.find((x) => x.id === id);
  return esp ? esp.nome : `Especialidade ${id}`;
}

const pedidoSelecionado = ref<InterconsultaPedido | null>(null);
const executingAction = ref(false);

const mostrarModalAgendamento = ref(false);
const dataConsulta = ref('');
const pedidoSendoAgendado = ref<InterconsultaPedido | null>(null);

const activeTab = ref<'pendentes' | 'agendados'>('pendentes');

const especialidadeFiltro = ref<number | null>(null);

const especialidadesComPedidos = computed(() => {
  const todas = { id: null as any, nome: 'Todas' };
  const idsComPedidos = new Set(pedidos.value.map((p) => p.especialidade_id));
  const filtradas = interconsultaStore.especialidades.filter((esp) => idsComPedidos.has(esp.id));
  return [todas, ...filtradas];
});

function contarPedidosPorEspecialidade(especialidadeId: number | null): number {
  if (especialidadeId === null) {
    return pedidos.value.length;
  }
  return pedidos.value.filter((p) => p.especialidade_id === especialidadeId).length;
}

async function selecionarEspecialidadeFila(id: number | null) {
  especialidadeFiltro.value = id;
  await recarregar();
}

// Lógica do Calendário Customizado
const hojeObj = new Date();
const anoAtual = ref(hojeObj.getFullYear());
const mesAtual = ref(hojeObj.getMonth());

const nomesMeses = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

const diasDaSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

const diasNoCalendario = computed(() => {
  const primeiroDiaDoMes = new Date(anoAtual.value, mesAtual.value, 1);
  const diaDaSemanaInicial = primeiroDiaDoMes.getDay();
  
  const ultimoDiaDoMes = new Date(anoAtual.value, mesAtual.value + 1, 0);
  const totalDiasNoMes = ultimoDiaDoMes.getDate();
  
  const dias = [];
  
  // Preenche os dias vazios do início do mês
  for (let i = 0; i < diaDaSemanaInicial; i++) {
    dias.push({ dia: null, dataCompleta: null, desabilitado: true });
  }
  
  // Preenche os dias do mês atual
  for (let d = 1; d <= totalDiasNoMes; d++) {
    const dataCompleta = new Date(anoAtual.value, mesAtual.value, d);
    
    const dataComparacao = new Date(anoAtual.value, mesAtual.value, d);
    const dataHojeSemHora = new Date();
    dataHojeSemHora.setHours(0, 0, 0, 0);
    
    const desabilitado = dataComparacao < dataHojeSemHora;
    
    dias.push({
      dia: d,
      dataCompleta,
      desabilitado
    });
  }
  
  return dias;
});

function navegarMes(direcao: number) {
  mesAtual.value += direcao;
  if (mesAtual.value < 0) {
    mesAtual.value = 11;
    anoAtual.value -= 1;
  } else if (mesAtual.value > 11) {
    mesAtual.value = 0;
    anoAtual.value += 1;
  }
}

function selecionarDataCalendario(diaObj: any) {
  if (!diaObj.dia || diaObj.desabilitado || !diaObj.dataCompleta) return;
  
  const yyyy = diaObj.dataCompleta.getFullYear();
  const mm = String(diaObj.dataCompleta.getMonth() + 1).padStart(2, '0');
  const dd = String(diaObj.dataCompleta.getDate()).padStart(2, '0');
  
  dataConsulta.value = `${yyyy}-${mm}-${dd}`;
}

function isHoje(data?: Date | null): boolean {
  if (!data) return false;
  const hoje = new Date();
  return data.getDate() === hoje.getDate() &&
         data.getMonth() === hoje.getMonth() &&
         data.getFullYear() === hoje.getFullYear();
}

function isSelecionado(data?: Date | null): boolean {
  if (!data || !dataConsulta.value) return false;
  const partes = dataConsulta.value.split('-');
  if (partes.length !== 3) return false;
  return data.getDate() === parseInt(partes[2]) &&
         data.getMonth() === parseInt(partes[1]) - 1 &&
         data.getFullYear() === parseInt(partes[0]);
}

const dataFormatadaPorExtenso = computed(() => {
  if (!dataConsulta.value) return 'Nenhuma data selecionada';
  const partes = dataConsulta.value.split('-');
  const dateObj = new Date(parseInt(partes[0]), parseInt(partes[1]) - 1, parseInt(partes[2]));
  return dateObj.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
});

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

function formatarDataSemHora(value?: string | null): string {
  if (!value) {
    return '—';
  }
  const partes = value.split('T')[0].split('-');
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const dia = String(date.getDate()).padStart(2, '0');
  const mes = String(date.getMonth() + 1).padStart(2, '0');
  const ano = date.getFullYear();
  return `${dia}/${mes}/${ano}`;
}

async function recarregar() {
  try {
    await interconsultaStore.listarPedidos(especialidadeFiltro.value);
  } catch {
    toast.error(interconsultaStore.error ?? 'Falha ao carregar a fila de regulação.');
  }
}

function confirmarAgendamento(pedido: InterconsultaPedido) {
  pedidoSendoAgendado.value = pedido;
  
  const hoje = new Date();
  anoAtual.value = hoje.getFullYear();
  mesAtual.value = hoje.getMonth();
  
  const yyyy = hoje.getFullYear();
  const mm = String(hoje.getMonth() + 1).padStart(2, '0');
  const dd = String(hoje.getDate()).padStart(2, '0');
  dataConsulta.value = `${yyyy}-${mm}-${dd}`;
  
  mostrarModalAgendamento.value = true;
}

async function salvarAgendamento() {
  if (!pedidoSendoAgendado.value) return;
  if (!dataConsulta.value) {
    toast.error("Por favor, selecione a data da consulta.");
    return;
  }
  executingAction.value = true;
  try {
    // Envia a data com hora zerada/meio-dia UTC de forma segura contra timezones
    const formattedDate = `${dataConsulta.value}T12:00:00Z`;
    await interconsultaStore.atualizarStatusPedido(pedidoSendoAgendado.value.id, 'AGENDADO', formattedDate);
    toast.success(`Pedido #${pedidoSendoAgendado.value.id} marcado como agendado com sucesso.`);
    mostrarModalAgendamento.value = false;
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
  interconsultaStore.listarEspecialidades();
});
</script>
