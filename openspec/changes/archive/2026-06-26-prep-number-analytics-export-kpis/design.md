## Context

Com a descontinuação do CNS no fluxo hospitalar do HC-UFPE, o sistema deve passar a utilizar o identificador PREP (Prontuário Eletrônico do Paciente). O PREP possui comprimento variável de 7 a 8 dígitos numéricos. 
Adicionalmente, a equipe de administração regulatória necessita de maior inteligência analítica. Precisamos extrair dados históricos (como tempo médio decorrido desde a abertura da interconsulta até o efetivo agendamento) e classificar pendências. A exportação para planilhas eletrônicas compatíveis com o Microsoft Excel é crucial para a interoperabilidade com sistemas legados e relatórios gerenciais externos.

## Goals / Non-Goals

**Goals:**
* Substituir o campo `paciente_cns` por `paciente_prep` em toda a base de dados, controllers e frontend, garantindo que continue criptografado via AES-256 no banco local.
* Limitar e validar o PREP do paciente no frontend e backend para conter exclusivamente entre 7 e 8 dígitos.
* Computar no backend novos KPIs: Total de Interconsultas, Tempo Médio de Atendimento da Marcação (em horas/minutos) e Especialidades com mais Pendências.
* Desenvolver no backend um gerador de planilhas Excel (.xlsx) estruturado com abas específicas via pandas.
* Implementar no frontend botões de exportação e cards/tabelas para exibição visual dos novos KPIs.

**Non-Goals:**
* Não será mantida compatibilidade retrógrada para CNS de 15 dígitos na criação de novas interconsultas.
* O arquivo Excel exportado não será persistido no servidor para economizar espaço e evitar vazamento de dados sensíveis; ele será gerado em tempo real em memória (`BytesIO`) e enviado direto como stream HTTP.

## Decisions

### 1. Migração de Banco de Dados (Alembic / SQLAlchemy)

No modelo `InterconsultaPedido`, o campo `paciente_cns` será renomeado para `paciente_prep` e manterá o tipo String, com índice de busca ativa.

```python
# src/models/interconsulta.py
class InterconsultaPedido(Base):
    __tablename__ = "interconsulta_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    paciente_prep = Column(String, index=True, nullable=False) # PREP criptografado com AES-256
    # ... outros campos ...
```

A migração do Alembic será responsável por:
1. Renomear a coluna `paciente_cns` para `paciente_prep` na tabela `interconsulta_pedidos`.
2. Recriar os índices associados à nova coluna.

### 2. Validação do PREP
No Pydantic schema e no Vue frontend:
* **Pydantic Validator:**
  ```python
  @field_validator("paciente_prep")
  @classmethod
  def validate_prep_format(cls, v: str) -> str:
      v_clean = v.strip()
      if not v_clean.isdigit():
          raise ValueError("O número do PREP deve conter apenas dígitos numéricos.")
      if not (7 <= len(v_clean) <= 8):
          raise ValueError("O número do PREP deve conter exatamente entre 7 e 8 dígitos.")
      return v_clean
  ```

### 3. Modificação dos Arquivos SQL Nativo
* **`src/providers/sql/interconsulta/inserir_pedido.sql`**:
  ```sql
  INSERT INTO interconsulta_pedidos (
      paciente_prep, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, marcado_por, criado_em, atualizado_em
  ) VALUES (
      #paciente_prep, #medico_solicitante_crm, #especialidade_id, #sintomas_json, #gravidade, #status, #marcado_por, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
  )
  RETURNING id, paciente_prep, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, marcado_por, data_consulta, criado_em, atualizado_em;
  ```
* **`src/providers/sql/interconsulta/listar_pedidos.sql`**:
  ```sql
  SELECT id, paciente_prep, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, marcado_por, data_consulta, criado_em, atualizado_em
  FROM interconsulta_pedidos
  WHERE deleted_at IS NULL;
  ```

### 4. Geração de Relatório Excel no Backend
Utilização do `pandas` combinada com o `openpyxl`.
```python
import io
import pandas as pd
from fastapi.responses import StreamingResponse

@router.get("/admin/statistics/export")
async def export_statistics_excel(
    interconsulta_provider = Depends(get_interconsulta_provider()),
    catalogo_provider = Depends(get_catalogo_provider()),
    current_user = Depends(verify_admin_group)
):
    pedidos = await interconsulta_provider.listar_pedidos_ativos()
    
    # 1. Resolver especialidades
    especialidades = await catalogo_provider.listar_especialidades()
    especialidades_map = {esp["id"]: esp["nome"] for esp in especialidades}
    
    # 2. Processar registros para DataFrame
    # Decriptografar paciente_prep e associar nomes das especialidades
    # ...
    
    # 3. Gerar Excel com multiplas abas na memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_overview.to_excel(writer, sheet_name='Geral', index=False)
        df_pedidos.to_excel(writer, sheet_name='Solicitacoes', index=False)
        df_especialidades.to_excel(writer, sheet_name='Por Especialidade', index=False)
        df_pendencias.to_excel(writer, sheet_name='Pendencias', index=False)
    
    output.seek(0)
    
    # Auditoria
    # ...
    
    headers = {
        'Content-Disposition': 'attachment; filename="analytics_interhc.xlsx"'
    }
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers
    )
```

## Risks / Trade-offs

* **Risco de crash no Excel por falta de biblioteca:** O `pandas` falhará silenciosamente ou lançará exceção se `openpyxl` não estiver instalado no ambiente.
  ➔ *Mitigação*: Adicionar `openpyxl` explicitamente ao `requirements.txt` e realizar sua instalação. Em caso de falhas, adicionar fallback que gera CSV.
* **Criptografia legada no arquivo Excel:** Exportar dados decifrados para Excel introduz um risco de vazamento de dados caso a planilha seja enviada a terceiros.
  ➔ *Mitigação*: Restringir o endpoint de exportação unicamente ao perfil `admin` via guard de token e auditoria explícita nos logs com o identificador do administrador que requisitou.
