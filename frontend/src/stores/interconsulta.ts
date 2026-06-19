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
  paciente_cns: string;
  medico_solicitante_crm: string;
  especialidade_id: number;
  sintomas_json: SintomaPayload[];
}

export interface InterconsultaPedido {
  id: number;
  paciente_cns: string;
  medico_solicitante_crm: string;
  especialidade_id: number;
  gravidade: string;
  status: string;
  sintomas_json?: any;
  criado_em?: string | null;
  atualizado_em?: string | null;
  dias_na_fila?: number;
  score_prioridade?: number;
}

export const SINTOMAS_CATALOGO_MVP: SintomaCatalogoItem[] = [
  { id: 1, nome: 'Cegueira' },
  { id: 2, nome: 'Infarto' },
  { id: 3, nome: 'AVC' },
  { id: 4, nome: 'Dor torácica intensa' },
  { id: 5, nome: 'Febre alta' },
  { id: 6, nome: 'Fratura' },
];

export function mascararCns(cns: string): string {
  const digits = cns.replace(/\D/g, '');
  if (digits.length < 4) {
    return '***';
  }
  return `***${digits.slice(-4)}`;
}

export function validarFormularioInterconsulta(
  cns: string,
  especialidadeId: number,
  sintomasSelecionados: SintomaCatalogoItem[],
): string | null {
  const cnsDigits = cns.replace(/\D/g, '');
  if (cnsDigits.length !== 15) {
    return 'O CNS deve conter exatamente 15 dígitos.';
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
  const loading = ref(false);
  const submitting = ref(false);
  const error = ref<string | null>(null);

  async function listarPedidos(): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get<InterconsultaPedido[]>('/api/interconsultas/');
      pedidos.value = response.data;
    } catch (err: unknown) {
      error.value = 'Falha ao carregar pedidos de interconsulta.';
      throw err;
    } finally {
      loading.value = false;
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

  async function atualizarStatusPedido(pedidoId: number, status: string): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await api.patch(`/api/interconsultas/${pedidoId}/status`, { status });
      const p = pedidos.value.find((x) => x.id === pedidoId);
      if (p) {
        p.status = status;
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
    loading,
    submitting,
    error,
    listarPedidos,
    criarPedido,
    mascararCns,
    atualizarStatusPedido,
    reprocessarPedido,
  };
});
