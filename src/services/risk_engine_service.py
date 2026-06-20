class RiskEngineService:
    """
    Serviço puro responsável por calcular a gravidade clínica (Risco)
    baseado no array de sintomas e na especialidade de destino.
    """
    
    # Sintomas Críticos Absolutos (sempre VERMELHO independente da especialidade)
    SINTOMAS_CRITICOS_IDS = [1, 2, 3] # Cegueira/Visão, Infarto/Dor, AVC/Fraqueza
    
    # Sintomas Moderados Absolutos (sempre no mínimo AMARELO)
    SINTOMAS_MODERADOS_IDS = [4, 5, 6, 7, 8, 10, 11, 12]
    
    # Overrides específicos de especialidade: (sintoma_id, especialidade_id) -> gravidade
    SPECIALTY_OVERRIDES = {
        # Cardiologia (ID 1)
        (4, 1): "VERMELHO",  # Dor torácica intensa -> VERMELHO
        (10, 1): "VERMELHO", # Dispneia aguda -> VERMELHO
        # Dermatologia (ID 3)
        (13, 3): "AMARELO",  # Erupção cutânea com febre -> AMARELO
        # Endocrinologia (ID 4)
        (9, 4): "AMARELO",   # Nódulo tireoidiano palpável -> AMARELO
        # Gastroenterologia (ID 5)
        (11, 5): "VERMELHO", # Dor abdominal intensa -> VERMELHO
        # Geriatria (ID 6)
        (14, 6): "AMARELO",  # Confusão mental aguda -> AMARELO
        # Infectologia (ID 8)
        (5, 8): "AMARELO",   # Febre alta -> AMARELO
        (13, 8): "AMARELO",  # Erupção cutânea com febre -> AMARELO
        # Nefrologia (ID 11)
        (8, 11): "VERMELHO", # Hematúria macroscópica -> VERMELHO
        # Neurologia (ID 12)
        (12, 12): "VERMELHO", # Convulsão -> VERMELHO
        (14, 12): "AMARELO",  # Confusão mental aguda -> AMARELO
        # Oncologia (ID 13)
        (9, 13): "AMARELO",   # Nódulo tireoidiano -> AMARELO
        # Pediatria (ID 14)
        (5, 14): "AMARELO",   # Febre alta -> AMARELO
        (12, 14): "VERMELHO", # Convulsão -> VERMELHO
        # Pneumologia (ID 15)
        (10, 15): "VERMELHO", # Dispneia aguda -> VERMELHO
        # Psiquiatria (ID 16)
        (7, 16): "VERMELHO",  # Ideação suicida ativa -> VERMELHO
        # Reumatologia (ID 17)
        (6, 17): "AMARELO",   # Fratura -> AMARELO
        # Urologia (ID 18)
        (8, 18): "VERMELHO",  # Hematúria macroscópica -> VERMELHO
    }

    @staticmethod
    def calcular_gravidade(sintomas: list, especialidade_id: int = None) -> str:
        """
        Recebe uma lista de dicionários de sintomas (ex: [{"id": 1, "nome": "Cegueira"}])
        e a especialidade desejada, e retorna a cor da gravidade (VERMELHO, AMARELO, VERDE).
        """
        if not sintomas:
            return "VERDE"
            
        sintomas_ids = [s.get("id") for s in sintomas if isinstance(s, dict) and "id" in s]
        
        maior_gravidade = "VERDE"
        
        for sid in sintomas_ids:
            # 1. Verifica se há override para o par (sintoma, especialidade)
            if especialidade_id is not None and (sid, especialidade_id) in RiskEngineService.SPECIALTY_OVERRIDES:
                gravidade_override = RiskEngineService.SPECIALTY_OVERRIDES[(sid, especialidade_id)]
                if gravidade_override == "VERMELHO":
                    return "VERMELHO" # Vermelho é o maior nível possível, pode retornar imediatamente
                elif gravidade_override == "AMARELO":
                    maior_gravidade = "AMARELO"
            
            # 2. Se não houver override, aplica a regra padrão baseada nas listas absolutas
            elif sid in RiskEngineService.SINTOMAS_CRITICOS_IDS:
                return "VERMELHO"
            elif sid in RiskEngineService.SINTOMAS_MODERADOS_IDS:
                maior_gravidade = "AMARELO"
                
        return maior_gravidade
