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
  paciente_nome?: string | null;
  medico_solicitante_crm: string;
  especialidade_id: number;
  gravidade: string;
  status: string;
  sintomas_json?: any;
  marcado_por?: string | null;
  criado_em?: string | null;
  atualizado_em?: string | null;
  dias_na_fila?: number;
  score_prioridade?: number;
}

export interface EspecialidadeCatalogoItem {
  id: number;
  nome: string;
}

export const ESPECIALIDADES_CATALOGO: EspecialidadeCatalogoItem[] = [
  { id: 1, nome: 'Cardiologia' },
  { id: 2, nome: 'Clínica Médica' },
  { id: 3, nome: 'Dermatologia' },
  { id: 4, nome: 'Endocrinologia' },
  { id: 5, nome: 'Gastroenterologia' },
  { id: 6, nome: 'Geriatria' },
  { id: 7, nome: 'Hematologia' },
  { id: 8, nome: 'Infectologia' },
  { id: 9, nome: 'Medicina de Família e Comunidade' },
  { id: 10, nome: 'Medicina do Trabalho' },
  { id: 11, nome: 'Nefrologia' },
  { id: 12, nome: 'Neurologia' },
  { id: 13, nome: 'Oncologia (Alta Complexidade - CACON)' },
  { id: 14, nome: 'Pediatria' },
  { id: 15, nome: 'Pneumologia' },
  { id: 16, nome: 'Psiquiatria' },
  { id: 17, nome: 'Reumatologia' },
  { id: 18, nome: 'Urologia' },
  { id: 19, nome: 'Ginecologia e Obstetrícia' },
];

export const SINTOMAS_CATALOGO_MVP: SintomaCatalogoItem[] = [
  { id: 1, nome: 'Cegueira / Perda súbita de visão' },
  { id: 2, nome: 'Infarto / Dor torácica súbita' },
  { id: 3, nome: 'AVC / Perda de força unilateral' },
  { id: 4, nome: 'Dor torácica intensa' },
  { id: 5, nome: 'Febre alta' },
  { id: 6, nome: 'Fratura' },
  { id: 7, nome: 'Ideação suicida ativa' },
  { id: 8, nome: 'Hematúria macroscópica' },
  { id: 9, nome: 'Nódulo tireoidiano palpável' },
  { id: 10, nome: 'Dispneia aguda' },
  { id: 11, nome: 'Dor abdominal intensa' },
  { id: 12, nome: 'Convulsão' },
  { id: 13, nome: 'Erupção cutânea com febre' },
  { id: 14, nome: 'Confusão mental aguda' },
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
