from datetime import datetime, timezone
from typing import List, Dict, Any

class QueueOptimizerService:
    # Pontuação base (quanto maior, mais prioritário)
    BASE_SCORES = {
        "VERMELHO": 100,
        "AMARELO": 60,
        "VERDE": 30,
        "AZUL": 10
    }
    
    # Quantos pontos o paciente ganha por dia esperando na fila
    FATOR_ACELERACAO_DIARIO = 2.5 

    @classmethod
    def reordenar_fila_dinamica(cls, pedidos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        hoje = datetime.now(timezone.utc)
        
        for pedido in pedidos:
            # 1. Identifica a pontuação base da cor
            score_base = cls.BASE_SCORES.get(pedido["gravidade"].upper(), 0)
            
            # 2. Calcula quantos dias o paciente está na fila
            data_criacao = pedido["criado_em"]
            if isinstance(data_criacao, str):
                data_criacao = datetime.fromisoformat(data_criacao.replace("Z", "+00:00"))
                
            dias_espera = (hoje - data_criacao).days
            dias_espera = max(0, dias_espera) # Evita números negativos
            
            # 3. A MÁGICA: Calcula o Score Total (Aceleração)
            score_dinamico = score_base + (dias_espera * cls.FATOR_ACELERACAO_DIARIO)
            
            # 4. Injeta os dados novos para o Frontend exibir
            pedido["dias_na_fila"] = dias_espera
            pedido["score_prioridade"] = round(score_dinamico, 1)

        # 5. Reordena a lista baseada no score dinâmico (do maior para o menor)
        pedidos_reordenados = sorted(pedidos, key=lambda p: p["score_prioridade"], reverse=True)
        
        return pedidos_reordenados