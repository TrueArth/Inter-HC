## Why

O processo atual de interconsultas (encaminhamento de pacientes) é analógico, sem rastreabilidade digital e com falhas na triagem da gravidade dos casos, o que gera perda de tempo para os pacientes e sobrecarrega a Central de Marcação. A solução "Módulo de Interconsulta" introduz um portal unificado inteligente que, através de formulários dinâmicos baseados em diretrizes clínicas, classifica o risco automaticamente (Motor de Regras) e enfileira a requisição usando um sistema resiliente de mensageria assíncrona, garantindo consistência e priorização para a Central do AGHU.

## What Changes

* Criação de formulários de solicitação baseados em especialidades médicas integradas aos dados pré-existentes do AGHU.
* Integração de um Motor de Regras que lê sintomas catalogados e atribui automaticamente a gravidade clínica (Vermelho, Amarelo, Verde).
* Criação de um sistema de mensageria / fila em background (Message Broker) para enviar pedidos à Central de Marcação com mecanismo de retry.
* **Fluxo de Dados:** Implementação arquitetural estrita do fluxo `SQL` ➔ `Resource` ➔ `Provider` ➔ `Controller` ➔ `Router`. O motor de regras existirá ao nível de Controller/Services auxiliando o Controller, utilizando as SQLs do Provider para persistência local.

## Capabilities

### New Capabilities
- `encaminhamento-digital`: Componente que consome a API AGHU e apresenta opções padronizadas de sintomas para solicitação. Inclui a base do formulário e persistência imutável.
- `motor-regras-gravidade`: Componente core de negócio que cruza os sintomas informados com as diretrizes e determina a classificação de prioridade.
- `integracao-central-marcacao`: Serviço de mensageria e worker em background responsável pela resiliência no envio das solicitações.

### Modified Capabilities


## Impact

* **Arquivos Afetados (Visão Preliminar):**
  * [NEW] `src/routers/interconsulta.py`
  * [NEW] `src/controllers/interconsulta_controller.py`
  * [NEW] `src/providers/implementations/interconsulta_postgres_provider.py`
  * [NEW] `src/providers/interfaces/interconsulta_provider_interface.py`
  * [NEW] `src/providers/sql/interconsulta/inserir_pedido.sql` (e outras)
  * [NEW] `src/models/interconsulta.py` (esquema SQLAlchemy com `deleted_at`)
  * [MODIFY] `src/main.py` (para incluir o novo router)
  * [MODIFY] `src/dependencies.py` (para injeção de dependência do provider)
* **LGPD e Trilha de Auditoria:** Criptografia obrigatória (AES-256) na base local para chaves identificadoras ou observações clínicas sensíveis. Toda interação de negócio exige *Soft Delete* (nenhum comando `DELETE` nativo pode existir em `sql/`).
* **Sistemas/Dependencies:** Adição de serviço/pacote para Message Broker (ex: Pika/Celery) para garantir processamento assíncrono.
