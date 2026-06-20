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
          <label for="especialidadeId" class="form-label">Especialidade (AGHU)</label>
          <select
            id="especialidadeId"
            v-model.number="especialidadeId"
            class="form-control bg-white cursor-pointer"
          >
            <option v-for="esp in ESPECIALIDADES_CATALOGO" :key="esp.id" :value="esp.id">
              {{ esp.nome }}
            </option>
          </select>
        </div>

        <div class="form-group relative">
          <label for="sintomaBusca" class="form-label">Buscar Sintomas</label>
          <input
            id="sintomaBusca"
            v-model="termoBusca"
            type="text"
            placeholder="Digite para buscar sintomas..."
            class="form-control"
            @focus="showSuggestions = true"
            @blur="onBlurInput"
          />
          
          <!-- Menu de Autocomplete -->
          <div 
            v-if="showSuggestions && sintomasSugeridos.length > 0" 
            class="absolute left-0 right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto z-50 divide-y divide-gray-100"
          >
            <div
              v-for="sintoma in sintomasSugeridos"
              :key="sintoma.id"
              class="px-4 py-2 hover:bg-blue-50 cursor-pointer text-sm text-gray-700 transition"
              @mousedown="adicionarSintoma(sintoma)"
            >
              {{ sintoma.nome }}
            </div>
          </div>
        </div>

        <!-- Tags de Sintomas Selecionados -->
        <div v-if="sintomasSelecionados.length > 0" class="space-y-2">
          <label class="form-label">Sintomas Selecionados</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="sintoma in sintomasSelecionados"
              :key="sintoma.id"
              class="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full border border-blue-200"
            >
              {{ sintoma.nome }}
              <button
                type="button"
                class="text-blue-500 hover:text-blue-800 focus:outline-none text-xs font-bold w-4 h-4 rounded-full hover:bg-blue-200 flex items-center justify-center"
                @click="removerSintoma(sintoma.id)"
              >
                &times;
              </button>
            </span>
          </div>
        </div>

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
  ESPECIALIDADES_CATALOGO,
  SINTOMAS_CATALOGO_MVP,
  validarFormularioInterconsulta,
  useInterconsultaStore,
  SintomaCatalogoItem,
} from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

const pacienteCns = ref('');
const especialidadeId = ref(1);
const sintomasSelecionados = ref<SintomaCatalogoItem[]>([]);
const termoBusca = ref('');
const showSuggestions = ref(false);

const sintomasSugeridos = computed(() => {
  const query = termoBusca.value.trim().toLowerCase();
  const selecionadosIds = sintomasSelecionados.value.map((s) => s.id);
  
  return SINTOMAS_CATALOGO_MVP.filter((s) => {
    const contemQuery = s.nome.toLowerCase().includes(query);
    const naoSelecionado = !selecionadosIds.includes(s.id);
    return contemQuery && naoSelecionado;
  });
});

function adicionarSintoma(sintoma: SintomaCatalogoItem) {
  sintomasSelecionados.value.push(sintoma);
  termoBusca.value = '';
  showSuggestions.value = false;
}

function removerSintoma(id: number) {
  sintomasSelecionados.value = sintomasSelecionados.value.filter((s) => s.id !== id);
}

function onBlurInput() {
  // Delay para dar tempo de processar o mousedown da sugestão
  setTimeout(() => {
    showSuggestions.value = false;
  }, 200);
}

function limparFormulario(): void {
  pacienteCns.value = '';
  especialidadeId.value = 1;
  sintomasSelecionados.value = [];
  termoBusca.value = '';
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
