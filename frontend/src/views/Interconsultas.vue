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

  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useToast } from 'vue-toastification';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import {
  SINTOMAS_CATALOGO_MVP,
  validarFormularioInterconsulta,
  useInterconsultaStore,
} from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

const pacienteCns = ref('');
const especialidadeId = ref(1);
const sintomasSelecionadosIds = ref<number[]>([]);

const sintomasSelecionados = computed(() =>
  SINTOMAS_CATALOGO_MVP.filter((s) => sintomasSelecionadosIds.value.includes(s.id)),
);

function limparFormulario(): void {
  pacienteCns.value = '';
  especialidadeId.value = 1;
  sintomasSelecionadosIds.value = [];
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
  } catch {
    const detail =
      (interconsultaStore.error as string | null) ??
      'Não foi possível criar o pedido. Verifique se está autenticado e se o backend está em execução.';
    toast.error(detail);
  }
}
</script>
