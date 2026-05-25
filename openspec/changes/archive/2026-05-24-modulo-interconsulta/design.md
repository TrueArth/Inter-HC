## Context
O Hospital das Clínicas sofre com gargalos operacionais no fluxo de interconsultas. Atualmente operado via papel e sem diretrizes algorítmicas impositivas, a triagem muitas vezes falha, levando pacientes a buscar vagas que não existem e sobrecarregando a Central de Marcação. A solução digital construirá um pipeline robusto no backend: receber dados estruturados de formulários baseados nas diretrizes do AGHU, aplicar um Motor de Regras para inferência de risco (Verde, Amarelo, Vermelho), salvar um registro imutável do pedido via SQLAlchemy/SQL, e publicar em um Message Broker para consumo e agendamento resiliente pela Central de Marcação.

## Goals / Non-Goals

**Goals:**
- Prover um módulo seguro com rastreabilidade completa e Soft Delete (`deleted_at`).
- Definir uma interface de persistência dupla usando `SQLAlchemy` para o mapeamento da entidade, e arquivos `.sql` nativos gerenciados pelo provider para as consultas de negócio.
- Garantir que a classificação de risco dependa estritamente das diretrizes, implementado no Controller.
- Introduzir mecanismo de enfileiramento assíncrono para garantir o envio dos pedidos à Central.

**Non-Goals:**
- Não iremos construir uma engine de NLP/LLM para entender texto livre de médicos. O sistema operará unicamente via catálogos de sintomas padronizados (IDs/Códigos).
- Não haverá exclusão física (Hard Deletes) da base de dados, mitigando riscos da LGPD.

## Decisions

### 1. Database Schema (SQLAlchemy) e Criptografia
A entidade principal será `InterconsultaPedido`. Para garantir integridade, a coluna `deleted_at` gerencia exclusões e campos sensíveis serão gerenciados via AES-256.

```python
class InterconsultaPedido(Base):
    __tablename__ = "interconsulta_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    paciente_cns = Column(String, index=True) # AES-256 Encriptado
    medico_solicitante_crm = Column(String)
    especialidade_id = Column(Integer)
    sintomas_json = Column(JSON) # Array of symptom IDs
    gravidade = Column(String) # VERMELHO, AMARELO, VERDE
    status = Column(String) # PENDENTE, ENFILEIRADO, AGENDADO, ERRO
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True) # SOFT DELETE OBRIGATÓRIO
```

### 2. SQLs Nativos (Provider Layer)
Em aderência ao fluxo, as consultas pesadas de negócio estarão mapeadas nos templates `.sql`.
Os seguintes arquivos serão criados na pasta `src/providers/sql/interconsulta/`:
- `inserir_pedido.sql`: Processo seguro de INSERT com RETURNING de ID criado.
- `listar_pedidos.sql`: SELECT parametrizado filtrando os pedidos ativos (`deleted_at IS NULL`).
- `soft_delete_pedido.sql`: Executa `UPDATE interconsulta_pedidos SET deleted_at = NOW()`.
- `atualizar_status_pedido.sql`: Modifica apenas as colunas de controle da fila de mensageria.

### 3. Motor de Regras (Controller Layer)
A camada do Controller orquestrará a chamada: `interconsulta_controller.py` vai validar o payload, instanciar a rotina do Motor de Risco cruzando com os parâmetros da diretriz, e só então enviará a versão processada e "classificada" do pedido para o Provider salvar e para o serviço de mensageria.

### 4. Mensageria Assíncrona (Retry Design)
Será utilizado `Celery` com `Redis` (ou inicialmente as `BackgroundTasks` do FastAPI como ponte) configurado para despachar requisições para a API externa da Central de Marcação. Em caso de 503 HTTP do AGHU, as mensagens voltarão à fila com log de evento na trilha de auditoria.

## Risks / Trade-offs

- **Risk: Configuração Complexa de Mensageria.** O setup do Redis+Celery introduz um componente na stack (Docker required).
  - **Trade-off/Mitigação:** No ambiente local (`ENV=development`), o componente de mensageria poderá operar via interface mockada usando `FastAPI BackgroundTasks`, escalando para Celery verdadeiro em produção.
- **Risk: Vazamento de Keys de AES-256.**
  - **Mitigação:** Seguir rigorosamente o guardrail *No Secrets in Code*. Chaves serão exclusivas do `.env`.
