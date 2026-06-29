<template>
  <div class="space-y-6">
    <Card>
      <template #header>
        <h2 class="text-xl font-semibold">Nova solicitação de interconsulta</h2>
      </template>

      <form class="space-y-4" @submit.prevent="enviar">
        <div class="form-group">
          <label for="pacientePrep" class="form-label">PREP do paciente</label>
          <input
            id="pacientePrep"
            v-model="pacientePrep"
            type="text"
            inputmode="numeric"
            maxlength="8"
            placeholder="7 a 8 dígitos"
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
            <option v-for="esp in interconsultaStore.especialidades" :key="esp.id" :value="esp.id">
              {{ esp.nome }}
            </option>
          </select>
        </div>

        <div class="form-group relative" ref="autocompleteContainer">
          <label for="sintomaSearch" class="form-label">Selecionar Sintomas Justificativos</label>
          <div class="relative flex items-center">
            <input
              id="sintomaSearch"
              type="text"
              v-model="termoBusca"
              @focus="showDropdown = true"
              @click="showDropdown = true"
              placeholder="Digite para buscar ou clique no ícone para ver todos..."
              class="form-control bg-white w-full pr-10 border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 rounded-lg px-4 py-2 text-sm text-gray-900 transition duration-150 ease-in-out shadow-sm"
              @keydown.down.prevent="highlightNext"
              @keydown.up.prevent="highlightPrev"
              @keydown.enter.prevent="selectHighlighted"
              @keydown.escape.prevent="showDropdown = false"
              autocomplete="off"
            />
            <button
              type="button"
              @click.stop="toggleDropdown"
              class="absolute right-3 focus:outline-none text-gray-400 hover:text-gray-600 transition duration-150"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 transition-transform duration-200"
                :class="{ 'rotate-180': showDropdown }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>

          <!-- Dropdown List -->
          <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div
              v-if="showDropdown"
              class="autocomplete-dropdown absolute z-50 left-0 right-0 mt-1.5 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto"
            >
              <ul v-if="sintomasFiltrados.length > 0" class="py-1">
                <li
                  v-for="(sintoma, index) in sintomasFiltrados"
                  :key="sintoma.id"
                  :class="[
                    'px-4 py-2.5 text-sm text-gray-700 cursor-pointer border-b border-gray-50 last:border-b-0 transition duration-150 ease-in-out',
                    index === highlightedIndex ? 'bg-blue-50 text-blue-900 font-medium active-item' : 'hover:bg-blue-50/50 hover:text-gray-900'
                  ]"
                  @mousedown.prevent="selecionarSintoma(sintoma)"
                >
                  <div class="flex justify-between items-center">
                    <span>{{ sintoma.nome }}</span>
                    <span class="text-xs text-gray-400 font-mono">ID: {{ sintoma.id }}</span>
                  </div>
                </li>
              </ul>
              <div v-else class="px-4 py-3.5 text-sm text-gray-500 text-center italic bg-gray-50">
                Nenhum sintoma encontrado para "{{ termoBusca }}"
              </div>
            </div>
          </transition>
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
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useToast } from 'vue-toastification';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import {
  validarFormularioInterconsulta,
  useInterconsultaStore,
  SintomaCatalogoItem,
} from '../stores/interconsulta';

const toast = useToast();
const interconsultaStore = useInterconsultaStore();

const pacientePrep = ref('');
const especialidadeId = ref(1);
const sintomasSelecionados = ref<SintomaCatalogoItem[]>([]);

// Autocomplete State
const autocompleteContainer = ref<HTMLElement | null>(null);
const termoBusca = ref('');
const showDropdown = ref(false);
const highlightedIndex = ref(-1);

onMounted(async () => {
  await interconsultaStore.listarEspecialidades();
  if (especialidadeId.value) {
    interconsultaStore.listarSintomasPorEspecialidade(especialidadeId.value);
  }
  window.addEventListener('click', cliqueForaAutocomplete);
});

onUnmounted(() => {
  window.removeEventListener('click', cliqueForaAutocomplete);
});

watch(especialidadeId, (newId) => {
  if (newId) {
    sintomasSelecionados.value = [];
    interconsultaStore.listarSintomasPorEspecialidade(newId);
  }
});

watch(() => interconsultaStore.especialidades, (esps) => {
  if (esps.length > 0 && !especialidadeId.value) {
    especialidadeId.value = esps[0].id;
  }
}, { immediate: true });

const sintomasDisponiveisParaAdicionar = computed(() => {
  const selecionadosIds = sintomasSelecionados.value.map((s) => s.id);
  return interconsultaStore.sintomas.filter((s) => !selecionadosIds.includes(s.id));
});

function removerAcentos(str: string): string {
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

const sintomasFiltrados = computed(() => {
  const query = removerAcentos(termoBusca.value.toLowerCase().trim());
  if (!query) {
    return sintomasDisponiveisParaAdicionar.value;
  }

  return sintomasDisponiveisParaAdicionar.value.filter((sintoma) => {
    const nomeClean = removerAcentos(sintoma.nome.toLowerCase());

    // 1. Substring match
    if (nomeClean.includes(query)) {
      return true;
    }

    // 2. Sequential character match (e.g. typing "drc" matches "Doenca Renal Cronica")
    let queryIdx = 0;
    for (let i = 0; i < nomeClean.length; i++) {
      if (nomeClean[i] === query[queryIdx]) {
        queryIdx++;
        if (queryIdx === query.length) {
          return true;
        }
      }
    }

    return false;
  });
});

function toggleDropdown() {
  showDropdown.value = !showDropdown.value;
  if (showDropdown.value) {
    highlightedIndex.value = -1;
  }
}

function selecionarSintoma(sintoma: SintomaCatalogoItem) {
  if (!sintomasSelecionados.value.some((s) => s.id === sintoma.id)) {
    sintomasSelecionados.value.push(sintoma);
  }
  termoBusca.value = '';
  showDropdown.value = false;
  highlightedIndex.value = -1;
}

function removerSintoma(id: number) {
  sintomasSelecionados.value = sintomasSelecionados.value.filter((s) => s.id !== id);
}

function cliqueForaAutocomplete(event: MouseEvent) {
  if (
    autocompleteContainer.value &&
    !autocompleteContainer.value.contains(event.target as Node)
  ) {
    showDropdown.value = false;
    highlightedIndex.value = -1;
  }
}

function highlightNext() {
  if (sintomasFiltrados.value.length === 0) return;
  highlightedIndex.value = (highlightedIndex.value + 1) % sintomasFiltrados.value.length;
  scrollToHighlighted();
}

function highlightPrev() {
  if (sintomasFiltrados.value.length === 0) return;
  highlightedIndex.value =
    (highlightedIndex.value - 1 + sintomasFiltrados.value.length) %
    sintomasFiltrados.value.length;
  scrollToHighlighted();
}

function selectHighlighted() {
  if (
    highlightedIndex.value >= 0 &&
    highlightedIndex.value < sintomasFiltrados.value.length
  ) {
    selecionarSintoma(sintomasFiltrados.value[highlightedIndex.value]);
  }
}

function scrollToHighlighted() {
  nextTick(() => {
    const listEl = document.querySelector('.autocomplete-dropdown');
    if (!listEl) return;
    const activeEl = listEl.querySelector('.active-item');
    if (!activeEl) return;

    const listRect = listEl.getBoundingClientRect();
    const activeRect = activeEl.getBoundingClientRect();

    if (activeRect.bottom > listRect.bottom) {
      listEl.scrollTop += activeRect.bottom - listRect.bottom;
    } else if (activeRect.top < listRect.top) {
      listEl.scrollTop -= listRect.top - activeRect.top;
    }
  });
}

function limparFormulario(): void {
  pacientePrep.value = '';
  especialidadeId.value = 1;
  sintomasSelecionados.value = [];
  termoBusca.value = '';
  showDropdown.value = false;
  highlightedIndex.value = -1;
}

async function enviar(): Promise<void> {
  const erroValidacao = validarFormularioInterconsulta(
    pacientePrep.value,
    especialidadeId.value,
    sintomasSelecionados.value,
  );
  if (erroValidacao) {
    toast.error(erroValidacao);
    return;
  }

  try {
    const criado = await interconsultaStore.criarPedido({
      paciente_prep: pacientePrep.value,
      medico_solicitante_crm: '-',
      especialidade_id: especialidadeId.value,
      sintomas_json: sintomasSelecionados.value.map((s) => ({ id: s.id, nome: s.nome })),
    });
    if (criado.status === 'ERRO') {
      toast.warning(`Solicitação de interconsulta não marcada. Motivo: ${criado.motivo_negacao || 'Não é papel do HC'}`);
    } else {
      toast.success('Solicitação de interconsulta registrada com sucesso (aguardando regulação).');
    }
    limparFormulario();
  } catch {
    const detail =
      (interconsultaStore.error as string | null) ??
      'Não foi possível criar o pedido. Verifique se está autenticado e se o backend está em execução.';
    toast.error(detail);
  }
}
</script>
