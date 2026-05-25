# Especificação de Requisitos

## 1. Requisitos Funcionais (RF)
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF001 | Autenticação | Login via LDAP/AD do hospital. | Essencial |
| RF002 | Cadastro | Registro de pacientes com CNS/CPF. | Essencial |
| RF003 | Visualização de Prontuário | Exibição de dados da consulta geradora e histórico clínico via API do AGHU. | Essencial |
| RF004 | Seleção de Sintomas | Seleção de sintomas a partir de uma lista padronizada baseada nas diretrizes do HC. | Essencial |
| RF005 | Cálculo de Gravidade | Atribuição automática do grau de risco clínico através do motor de regras. | Essencial |
| RF006 | Registro de Solicitação | Persistência local do pedido com logs de auditoria imutáveis. | Essencial |
| RF006 | Envio de Interconsulta | Submissão do pedido para a Central de Marcação do AGHU de forma resiliente. | Essencial |


## 2. Requisitos Não Funcionais (RNF)
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF001 | Segurança | Criptografia AES-256. |
| RNF002 | LGPD | Auditoria de acesso a dados sensíveis. |
| RNF003 | Performance | Tempo de resposta para leitura do AGHU deve ser inferior a 2 segundos. |
| RNF004 | Resiliência | Uso de filas e retentativas (Retry) para garantir o envio à Central de Marcação. |
| RNF005 | Consistência | Foco em CP (Teorema CAP) para evitar agendamentos duplicados ou inválidos. |

## 3. Detalhamento SDD (CARE)
Para cada requisito, a implementação deve seguir o padrão:

### [CARE-RF001] Autenticação LDAP
* **Context (Contexto)**: Servidor LDAP configurado e credenciais de serviço disponíveis.
* **Action (Ação)**: Realizar chamada síncrona GET /api/aghu/prontuario/{cpf} ao identificar o paciente.
* **Result (Resultado)**: Agregação visual dos dados clínicos na tela de interconsulta sem replicação de dados.
* **Evaluation (Avaliação)**: Validar se o mapeamento dos campos do legado para o portal ocorre sem perda de semântica.

### [CARE-RF002] Cadastro de Pacientes
* **Context (Contexto)**: Esquema de banco de dados 'PACIENTE' criado.
* **Action (Ação)**: Criar endpoint POST `/api/pacientes` com validação de CPF e CNS.
* **Result (Resultado)**: Registro persistido no banco; Log de auditoria criado.
* **Evaluation (Avaliação)**: Validar contra JSON Schema definido em `04-modelo-dados.md`.

### [CARE-RF-003] Consulta de Prontuário
* **Context (Contexto)**: Médico autenticado e endpoint de leitura do AGHU disponível.
* **Action (Ação)**: Criar middleware de autenticação que consulte o AD.
* **Result (Resultado)**: Token JWT gerado após sucesso; Código 401 em falha.
* **Evaluation (Avaliação)**: Executar `npm test tests/auth.spec.ts` (deve passar com 100% de sucesso).

### [CARE-RF-004] Catálogo Padronizado de Sintomas
* **Context (Contexto)**: O prontuário foi carregado e o médico está preenchendo o formulário de interconsulta no Information Portal.
* **Action (Ação)**: Disponibilizar os sintomas de forma parametrizada (ex: menus dropdown) filtrados pela especialidade de destino escolhida.
Result (Resultado): Bloqueio de entrada de texto livre na queixa principal, garantindo a padronização semântica (códigos fixos) que o Motor de Regras precisa para rodar.
Evaluation (Avaliação): Teste de validação de payload no backend garantindo que a requisição seja rejeitada (HTTP 400) caso o frontend tente enviar um sintoma fora do catálogo estabelecido pelas diretrizes.

### [CARE-RF-005] Motor de Classificação de Risco
* **Context (Contexto)**: Sintomas padronizados selecionados pelo médico assistente.
* **Action (Ação)**: Cruzar a seleção com a matriz de decisão baseada nas diretrizes clínicas do HC-UFPE.
* **Result (Resultado)**: Definição automática da prioridade (ex: Vermelho, Amarelo, Verde) antes do envio.
* **Evaluation (Avaliação)**: Executar bateria de testes unitários (gravity.spec.ts) com 100% de cobertura nos cenários das diretrizes.

### [CARE-RF-006] Registro e Trilha de Auditoria (Persistência Local)
* **Context (Contexto)**: O Motor de Regras finalizou o cálculo da gravidade e a transação de negócio vai ser iniciada.
* **Action (Ação)**: Inserir os dados estruturados do pedido no banco de dados local do módulo antes de enfileirar a mensagem para o Message Broker.
* **Result (Resultado)**: Criação de um registro imutável com metadados cruciais (ID Médico, ID Paciente, created_at, Gravidade) garantindo rastreabilidade "De/Para" mesmo se a Central de Marcação falhar.
* **Evaluation (Avaliação)**: Executar testes no repositório de banco de dados para garantir que a constraint de "Soft Delete" (deleted_at) funciona e que operações de exclusão física (DELETE SQL) retornam erro crítico.

### [CARE-RF-007] Envio Assíncrono (Messaging)
* **Context (Contexto)**: Gravidade calculada e solicitação registrada no banco de dados local.
* **Action (Ação)**: Publicar o pedido em um barramento de mensagens (Message Bus) para entrega ao AGHU.
* **Result (Resultado)**: Confirmação imediata ao médico; entrega garantida em background mesmo sob instabilidade do sistema de destino.
* **Evaluation (Avaliação)**: Simular queda de conexão e verificar se o mecanismo de Retry preserva a ordem e a integridade dos pedidos.
