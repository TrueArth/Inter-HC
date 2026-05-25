import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api';

export const useLeitoStore = defineStore('leito', () => {
  const leitos = ref<any[]>([]);
  const loading = ref(false);

  async function buscarLeitosDoSetor(setorId: number) {
    loading.value = true;
    try {
      const response = await api.get(`/api/leitos/setor/${setorId}`);
      leitos.value = response.data;
    } catch (error) {
      console.error("Erro ao buscar leitos:", error);
    } finally {
      loading.value = false;
    }
  }
  return { leitos, loading, buscarLeitosDoSetor };
});