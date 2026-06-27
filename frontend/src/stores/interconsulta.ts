import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api';

/** Alinhado a `RiskEngineService.SINTOMAS_CRITICOS_IDS` e `SINTOMAS_MODERADOS_IDS` no backend. */
export interface SintomaCatalogoItem {
  id: number;
  nome: string;
}

export interface SintomaPayload {
  id: number;
  nome: string;
}

export interface InterconsultaCreatePayload {
  paciente_prep: string;
  medico_solicitante_crm: string;
  especialidade_id: number;
  sintomas_json: SintomaPayload[];
}

export interface InterconsultaPedido {
  id: number;
  paciente_prep: string;
  paciente_nome?: string | null;
  medico_solicitante_crm: string;
  especialidade_id: number;
  gravidade: string;
  status: string;
  sintomas_json?: any;
  marcado_por?: string | null;
  data_consulta?: string | null;
  criado_em?: string | null;
  atualizado_em?: string | null;
  dias_na_fila?: number;
  score_prioridade?: number;
}

export interface EspecialidadeCatalogoItem {
  id: number;
  nome: string;
}

// Fallbacks vazios para retrocompatibilidade
export const ESPECIALIDADES_CATALOGO: EspecialidadeCatalogoItem[] = [];
export const SINTOMAS_CATALOGO_MVP: SintomaCatalogoItem[] = [];

export function mascararPrep(prep: string): string {
  const digits = prep.replace(/\D/g, '');
  if (digits.length < 3) {
    return '***';
  }
  return `***${digits.slice(-3)}`;
}

export function validarFormularioInterconsulta(
  prep: string,
  especialidadeId: number,
  sintomasSelecionados: SintomaCatalogoItem[],
): string | null {
  if (/\D/.test(prep)) {
    return 'O número do PREP deve conter apenas números.';
  }
  if (prep.length < 7 || prep.length > 8) {
    return 'O número do PREP deve conter entre 7 e 8 dígitos.';
  }
  if (!Number.isInteger(especialidadeId) || especialidadeId < 1) {
    return 'Informe o código da especialidade (número maior ou igual a 1).';
  }
  if (sintomasSelecionados.length === 0) {
    return 'Selecione ao menos um sintoma.';
  }
  return null;
}

export const useInterconsultaStore = defineStore('interconsulta', () => {
  const pedidos = ref<InterconsultaPedido[]>([]);
  const sintomas = ref<SintomaCatalogoItem[]>([]);
  const especialidades = ref<EspecialidadeCatalogoItem[]>([]);
  const loading = ref(false);
  const submitting = ref(false);
  const error = ref<string | null>(null);

  async function listarPedidos(especialidadeId?: number | null): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const url = especialidadeId ? `/api/interconsultas/?especialidade_id=${especialidadeId}` : '/api/interconsultas/';
      const response = await api.get<InterconsultaPedido[]>(url);
      pedidos.value = response.data;
    } catch (err: unknown) {
      error.value = 'Falha ao carregar pedidos de interconsulta.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function listarSintomas(): Promise<void> {
    try {
      const response = await api.get<SintomaCatalogoItem[]>('/api/interconsultas/sintomas');
      sintomas.value = response.data;
    } catch (err: unknown) {
      console.error('Falha ao carregar sintomas.', err);
    }
  }

  async function listarSintomasPorEspecialidade(especialidadeId: number): Promise<void> {
    try {
      const response = await api.get<SintomaCatalogoItem[]>(`/api/interconsultas/especialidades/${especialidadeId}/sintomas`);
      if (response.data && response.data.length > 0) {
        sintomas.value = response.data;
      } else {
        await listarSintomas();
      }
    } catch (err: unknown) {
      console.error('Falha ao carregar sintomas da especialidade.', err);
      await listarSintomas();
    }
  }

  async function listarEspecialidades(): Promise<void> {
    try {
      const response = await api.get<EspecialidadeCatalogoItem[]>('/api/interconsultas/especialidades');
      especialidades.value = response.data;
    } catch (err: unknown) {
      console.error('Falha ao carregar especialidades.', err);
    }
  }

  async function criarPedido(payload: InterconsultaCreatePayload): Promise<InterconsultaPedido> {
    submitting.value = true;
    error.value = null;
    try {
      const response = await api.post<InterconsultaPedido>('/api/interconsultas/', payload);
      return response.data;
    } catch (err: unknown) {
      error.value = 'Falha ao criar pedido de interconsulta.';
      throw err;
    } finally {
      submitting.value = false;
    }
  }

  async function atualizarStatusPedido(pedidoId: number, status: string, dataConsulta?: string): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const payload: any = { status };
      if (dataConsulta) {
        payload.data_consulta = dataConsulta;
      }
      await api.patch(`/api/interconsultas/${pedidoId}/status`, payload);
      const p = pedidos.value.find((x) => x.id === pedidoId);
      if (p) {
        p.status = status;
        if (dataConsulta) {
          p.data_consulta = dataConsulta;
        }
        p.atualizado_em = new Date().toISOString();
      }
    } catch (err: unknown) {
      error.value = 'Falha ao atualizar status do pedido.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function reprocessarPedido(pedidoId: number): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await api.post(`/api/interconsultas/${pedidoId}/retry`);
      const p = pedidos.value.find((x) => x.id === pedidoId);
      if (p) {
        p.status = 'ENFILEIRADO';
        p.atualizado_em = new Date().toISOString();
      }
    } catch (err: unknown) {
      error.value = 'Falha ao reprocessar pedido.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    pedidos,
    sintomas,
    especialidades,
    loading,
    submitting,
    error,
    listarPedidos,
    listarSintomas,
    listarSintomasPorEspecialidade,
    listarEspecialidades,
    criarPedido,
    mascararPrep,
    atualizarStatusPedido,
    reprocessarPedido,
  };
});
