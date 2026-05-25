class RiskEngineService:
    """
    Serviço puro responsável por calcular a gravidade clínica (Risco)
    baseado no array de sintomas. Evita acoplamento com o banco de dados.
    """
    
    # Simulação de um catálogo parametrizado (em produção isso viria do banco ou cache)
    SINTOMAS_CRITICOS_IDS = [1, 2, 3] # Ex: 1=Cegueira, 2=Infarto, 3=AVC
    SINTOMAS_MODERADOS_IDS = [4, 5, 6] # Ex: 4=Febre alta, 5=Fratura
    
    @staticmethod
    def calcular_gravidade(sintomas: list) -> str:
        """
        Recebe uma lista de dicionários de sintomas (ex: [{"id": 1, "nome": "Cegueira"}])
        e retorna a cor da gravidade (VERMELHO, AMARELO, VERDE).
        """
        if not sintomas:
            return "VERDE"
            
        sintomas_ids = [s.get("id") for s in sintomas if isinstance(s, dict) and "id" in s]
        
        # Regra 1: Qualquer sintoma crítico eleva o pedido para VERMELHO
        for sid in sintomas_ids:
            if sid in RiskEngineService.SINTOMAS_CRITICOS_IDS:
                return "VERMELHO"
                
        # Regra 2: Qualquer sintoma moderado (sem crítico) eleva para AMARELO
        for sid in sintomas_ids:
            if sid in RiskEngineService.SINTOMAS_MODERADOS_IDS:
                return "AMARELO"
                
        # Regra 3: Default é VERDE
        return "VERDE"
