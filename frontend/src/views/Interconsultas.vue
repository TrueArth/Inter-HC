<template>
  <div class="space-y-6">
    <Card>
      <template #header>
        <h2 class="text-xl font-semibold">Nova solicitação de interconsulta</h2>
      </template>

      <form class="space-y-4" @submit.prevent="enviar">
        <div class="form-group">
          <label for="pacienteCns" class="form-label">CNS do paciente</label>
          <input
            id="pacienteCns"
            v-model="pacienteCns"
            type="text"
            inputmode="numeric"
            maxlength="15"
            placeholder="15 dígitos"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="especialidadeId" class="form-label">Código da especialidade (AGHU)</label>
          <input
            id="especialidadeId"
            v-model.number="especialidadeId"
            type="number"
            min="1"
            class="form-control"
          />
        </div>

        <fieldset>
          <legend class="form-label mb-2">Sintomas (catálogo MVP)</legend>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <label
              v-for="sintoma in SINTOMAS_CATALOGO_MVP"
              :key="sintoma.id"
              class="flex items-center space-x-2 text-sm cursor-pointer"
            >
              <input
                v-model="sintomasSelecionadosIds"
                type="checkbox"
                :value="sintoma.id"
                class="rounded border-gray-300"
              />
              <span>{{ sintoma.id }} — {{ sintoma.nome }}</span>
            </label>
          </div>
        </fieldset>

        <Button type="submit" variant="primary" :loading="interconsultaStore.submitting">
          Solicitar interconsulta
        </Button>
      </form>
    </Card>

    <Card>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Pedidos ativos</h2>
          <Button variant="info" size="sm" :loading="interconsultaStore.loading" @click="recarregar">
            Atualizar
          </Button>
        </div>
      </template>

      <p v-if="interconsultaStore.loading && pedidos.length === 0" class="text-sm text-gray-500">
        Carregando pedidos...
      </p>
      <p v-else-if="pedidos.length === 0" class="text-sm text-gray-500">
        Nenhum pedido de interconsulta encontrado.
      </p>

      <table v-else class="min-w-full divide-y divide-gray-200 mt-2">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CNS</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Especialidade</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gravidade</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criado em</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>  
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tempo de espera</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="pedido in pedidos" :key="pedido.id">
            <td class="px-4 py-3 text-sm">{{ pedido.id }}</td>
            <td class="px-4 py-3 text-sm font-mono">{{ mascararCns(pedido.paciente_cns) }}</td>
            <td class="px-4 py-3 text-sm">{{ pedido.especialidade_id }}</td>
            <td class="px-4 py-3 text-sm">
              <span :class="gravidadeClass(pedido.gravidade)" class="inline-flex px-2 py-0.5 rounded text-xs font-semibold">
                {{ pedido.gravidade }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">{{ pedido.status }}</td>
            <td class="px-4 py-3 text-sm">{{ formatarData(pedido.criado_em) }}</td>
            <td class="px-4 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
            {{ pedido.score_prioridade }} pts
          </td>
          <td class="px-4 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
            {{ pedido.dias_na_fila }} dias
          </td>
          </tr>
        </tbody>
      </table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import {
  SINTOMAS_CATALOGO_MVP,
  mascararCns,
  validarFormularioInterconsulta,
  useInterconsultaStore,
} from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

const pacienteCns = ref('');
const especialidadeId = ref(1);
const sintomasSelecionadosIds = ref<number[]>([]);

const pedidos = computed(() => interconsultaStore.pedidos);

const sintomasSelecionados = computed(() =>
  SINTOMAS_CATALOGO_MVP.filter((s) => sintomasSelecionadosIds.value.includes(s.id)),
);

function gravidadeClass(gravidade: string): string {
  switch (gravidade) {
    case 'VERMELHO':
      return 'bg-red-100 text-red-800';
    case 'AMARELO':
      return 'bg-amber-100 text-amber-800';
    case 'VERDE':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

function formatarData(value?: string | null): string {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('pt-BR');
}

function limparFormulario(): void {
  pacienteCns.value = '';
  especialidadeId.value = 1;
  sintomasSelecionadosIds.value = [];
}

async function recarregar(): Promise<void> {
  try {
    await interconsultaStore.listarPedidos();
  } catch {
    toast.error(interconsultaStore.error ?? 'Falha ao carregar pedidos.');
  }
}

async function enviar(): Promise<void> {
  const erroValidacao = validarFormularioInterconsulta(
    pacienteCns.value,
    especialidadeId.value,
    sintomasSelecionados.value,
  );
  if (erroValidacao) {
    toast.error(erroValidacao);
    return;
  }

  const cnsDigits = pacienteCns.value.replace(/\D/g, '');

  try {
    const criado = await interconsultaStore.criarPedido({
      paciente_cns: cnsDigits,
      medico_solicitante_crm: '-',
      especialidade_id: especialidadeId.value,
      sintomas_json: sintomasSelecionados.value.map((s) => ({ id: s.id, nome: s.nome })),
    });
    toast.success(`Pedido criado com gravidade ${criado.gravidade}.`);
    limparFormulario();
    await recarregar();
  } catch {
    const detail =
      (interconsultaStore.error as string | null) ??
      'Não foi possível criar o pedido. Verifique se está autenticado e se o backend está em execução.';
    toast.error(detail);
  }
}

onMounted(() => {
  recarregar();
});
</script>
