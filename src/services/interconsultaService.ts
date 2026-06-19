// Dica: No Expo, não use 'localhost'. Use o IP da sua máquina na rede Wi-Fi.
const API_BASE_URL = 'http://192.168.1.100:8000/api'; 

export const InterconsultaService = {
  
  criarPedido: async (dadosPedido: any, tokenJwt: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/interconsultas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokenJwt}`
        },
        body: JSON.stringify(dadosPedido)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao criar interconsulta no servidor.');
      }

      return await response.json();
    } catch (error) {
      console.error("[InterconsultaService] Erro ao criar pedido:", error);
      throw error;
    }
  },

  listarPedidosAtivos: async (tokenJwt: string) => { // <-- Correção aqui
    try {
      const response = await fetch(`${API_BASE_URL}/interconsultas/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokenJwt}`
        }
      });
      
      if (!response.ok) throw new Error('Erro ao buscar lista de interconsultas');
      return await response.json();
    } catch (error) {
      console.error("[InterconsultaService] Erro ao listar pedidos:", error);
      throw error;
    }
  }
};