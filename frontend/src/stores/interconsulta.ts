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
  paciente_contato?: string;
  medico_solicitante_crm: string;
  especialidade_id: number;
  sintomas_json: SintomaPayload[];
}

export interface InterconsultaPedido {
  id: number;
  paciente_prep: string;
  paciente_nome?: string | null;
  paciente_contato?: string | null;
  medico_solicitante_crm: string;
  especialidade_id: number;
  gravidade: string;
  status: string;
  sintomas_json?: any;
  marcado_por?: string | null;
  data_consulta?: string | null;
  motivo_negacao?: string | null;
  criado_em?: string | null;
  atualizado_em?: string | null;
  dias_na_fila?: number;
  score_prioridade?: number;
}

export interface EspecialidadeCatalogoItem {
  id: number;
  nome: string;
}

export interface UndoAction {
  id: string;
  name: string;
  execute: () => Promise<void>;
  cancel?: () => void;
  secondsLeft: number;
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
  contato?: string,
): string | null {
  if (/\D/.test(prep)) {
    return 'O número do PREP deve conter apenas números.';
  }
  if (prep.length < 7 || prep.length > 8) {
    return 'O número do PREP deve conter entre 7 e 8 dígitos.';
  }
  if (contato && contato.trim() !== '') {
    const contatoClean = contato.trim();
    const regex = /^\(\d{2}\)\s?\d{4,5}-\s?\d{4}$/;
    if (!regex.test(contatoClean)) {
      return 'O número de contato deve estar no formato (dd) xxxxx-xxxx ou (dd) xxxx-xxxx.';
    }
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

  const activeUndoAction = ref<UndoAction | null>(null);
  let undoIntervalId: any = null;
  let undoTimeoutId: any = null;

  function registerUndoableAction(
    name: string,
    execute: () => Promise<void>,
    cancel?: () => void
  ) {
    if (activeUndoAction.value) {
      clearTimeout(undoTimeoutId);
      clearInterval(undoIntervalId);
      activeUndoAction.value.execute().catch(console.error);
      activeUndoAction.value = null;
    }

    const actionId = Math.random().toString(36).substring(7);
    activeUndoAction.value = {
      id: actionId,
      name,
      execute,
      cancel,
      secondsLeft: 30
    };

    undoIntervalId = setInterval(() => {
      if (activeUndoAction.value && activeUndoAction.value.id === actionId) {
        activeUndoAction.value.secondsLeft -= 1;
        if (activeUndoAction.value.secondsLeft <= 0) {
          clearInterval(undoIntervalId);
        }
      }
    }, 1000);

    undoTimeoutId = setTimeout(async () => {
      if (activeUndoAction.value && activeUndoAction.value.id === actionId) {
        clearInterval(undoIntervalId);
        const actionToExecute = activeUndoAction.value.execute;
        activeUndoAction.value = null;
        try {
          await actionToExecute();
        } catch (err) {
          console.error("Erro ao executar ação agendada:", err);
        }
      }
    }, 30000);
  }

  function triggerUndo() {
    console.log("triggerUndo chamado");
    if (activeUndoAction.value) {
      console.log("Desfazendo ação:", activeUndoAction.value.name);
      clearTimeout(undoTimeoutId);
      clearInterval(undoIntervalId);
      if (activeUndoAction.value.cancel) {
        activeUndoAction.value.cancel();
      }
      activeUndoAction.value = null;
    } else {
      console.log("Nenhuma ação ativa para desfazer");
    }
  }

  async function triggerConfirm() {
    console.log("triggerConfirm chamado");
    if (activeUndoAction.value) {
      console.log("Confirmando ação imediatamente:", activeUndoAction.value.name);
      clearTimeout(undoTimeoutId);
      clearInterval(undoIntervalId);
      const actionToExecute = activeUndoAction.value.execute;
      activeUndoAction.value = null;
      try {
        await actionToExecute();
        console.log("Ação executada com sucesso!");
      } catch (err) {
        console.error("Erro ao executar ação confirmada:", err);
      }
    } else {
      console.log("Nenhuma ação ativa para confirmar");
    }
  }

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
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Falha ao criar pedido de interconsulta.';
      error.value = errMsg;
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
      if (status === 'AGENDADO' && dataConsulta) {
        payload.data_consulta = dataConsulta;
      } else {
        payload.data_consulta = null;
      }
      await api.patch(`/api/interconsultas/${pedidoId}/status`, payload);
      const p = pedidos.value.find((x) => x.id === pedidoId);
      if (p) {
        p.status = status;
        if (status === 'AGENDADO') {
          if (dataConsulta) {
            p.data_consulta = dataConsulta;
          }
        } else {
          p.data_consulta = null;
          p.marcado_por = null;
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

  async function cancelarPedido(pedidoId: number): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/api/interconsultas/${pedidoId}`);
      pedidos.value = pedidos.value.filter((x) => x.id !== pedidoId);
    } catch (err: unknown) {
      error.value = 'Falha ao cancelar o pedido.';
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
    activeUndoAction,
    registerUndoableAction,
    triggerUndo,
    triggerConfirm,
    listarPedidos,
    listarSintomas,
    listarSintomasPorEspecialidade,
    listarEspecialidades,
    criarPedido,
    mascararPrep,
    atualizarStatusPedido,
    cancelarPedido,
    reprocessarPedido,
  };
});
