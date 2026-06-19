# Universidade Federal de Pernambuco
# Centro de Informática - CIn

**Curso:** Integração e Evolução de Sistemas Digitais - 2026.1  
**Projeto:** Portal de Dados e Governança de Interconsultas do Hospital das Clínicas  
**Fase:** Primeiro Relatório de Desenvolvimento (MVP)  

### Equipe de Desenvolvimento
*   João Guilherme Lemos Duarte de Oliveira
*   João Vitor Figueiredo de Vasconcelos
*   Nara Maria Silva de Pontes
*   Arthur Sean Cerqueira Campos
*   Arthur Fidney da Cunha Cavalcante
*   Isabela Possídio Amorim

**Local:** Recife, PE  
**Data:** Maio de 2026  

---

## 1. Processos

No cenário hospitalar do Hospital das Clínicas (HC), o fluxo de solicitação e marcação de interconsultas (quando um médico de uma especialidade solicita a avaliação de um colega de outra especialidade para um paciente internado ou ambulatorial) é caracterizado por ineficiência operacional, deslocamento desnecessário de pacientes e ausência de triagem. A tabela abaixo detalha as diferenças cruciais entre a realidade operacional atual e o fluxo otimizado implementado no nosso MVP.

| Etapa do Processo | Processo Atual (As-Is) | Processo Futuro (To-Be) |
| :--- | :--- | :--- |
| **1. Solicitação Clínica** | **Solicitação Sem Critério:** O médico preenche o formulário de interconsulta manualmente em papel. Embora existam PDFs orientativos de protocolos clínicos, não há validação ativa de elegibilidade ou obrigatoriedade de critérios mínimos no ato do preenchimento. | **Garantia de Protocolo Digital:** O médico preenche a solicitação de forma 100% digital. O formulário exige critérios obrigatórios em tempo real (como o CNS válido com 15 dígitos) e valida os sintomas clínicos selecionados. |
| **2. Triagem e Priorização** | **Inexistente / Por Ordem de Chegada:** Não há triagem de gravidade. Pacientes graves e leves competem igualmente por vagas, e a priorização clínica é ignorada em favor da fila física. | **Classificação de Risco Automatizada:** O sistema intercepta a lista de sintomas informados e executa um motor de regras clínico (`RiskEngineService`) para classificar a prioridade em tempo real (Vermelho, Amarelo ou Verde). |
| **3. Trâmite Físico vs. Digital** | **Deslocamento do Paciente:** O paciente (ou seu acompanhante) é obrigado a portar a guia física de papel e se deslocar até a recepção da Central de Marcação para realizar a entrega e tentar agendar a vaga. | **Trâmite Interno Automatizado:** A solicitação é transmitida eletronicamente e entra na fila digital da Central de Marcação imediatamente após o envio médico. O trâmite é 100% livre de papel e de esforço físico do paciente. |
| **4. Gestão da Fila de Espera** | **Verificação Manual e Repetitiva:** O atendente checa as vagas no sistema legado. Se não houver vaga disponível na hora, o paciente retorna para casa sem perspectiva e deve voltar fisicamente no próximo ciclo de abertura de agendas. | **Retenção Inteligente de Fila:** Caso não existam vagas de imediato, a solicitação permanece retida na fila digital, conservando sua prioridade de acordo com a gravidade clínica para o cruzamento automático do dia seguinte. |
| **5. Agendamento de Vagas** | **Agendamento Imediato Sem Triagem:** A vaga é entregue para quem está no guichê no exato momento da abertura. As filas no setor de recepção geram gargalos crônicos de atendimento. | **Cruzamento Otimizado de Vagas:** Ao final de cada ciclo, a Central cruza as vagas disponíveis com a fila digital prioritária. O paciente é contatado diretamente com a data confirmada, eliminando viagens desnecessárias ao hospital. |

---

## 2. Serviços a serem desenvolvidos

Com base no levantamento de requisitos conduzido junto à equipe do Hospital das Clínicas (com destaque para as dores compartilhadas pela gestora Camila), identificamos que o gargalo operacional reside em três pilares: **falta de governança e controle**, **ausência de critérios clínicos para encaminhamento** e **falta de priorização de gravidade**. 

Para sanar essas deficiências, estruturamos o desenvolvimento do sistema em torno de três serviços modulares e integrados:

### A. Triagem e Classificação de Risco Automatizada
*   **Problema:** As clínicas solicitam interconsultas sem critérios objetivos de encaminhamento, gerando um volume inflacionado de pedidos de baixa complexidade que sobrecarregam os especialistas.
*   **Solução:** Implementação de um motor de triagem automática no backend (`RiskEngineService`). A partir da seleção de um catálogo parametrizável de sintomas no formulário digital, o sistema classifica a solicitação conforme o nível de urgência, aplicando regras clínicas parametrizadas inspiradas no Protocolo de Manchester.
*   **Impacto:** Redução expressiva de encaminhamentos indevidos e ordenação inteligente da lista de espera por gravidade do caso, e não por tempo de chegada.

### B. Gestão e Controle de Fluxo (Governança Operacional)
*   **Problema:** A Central de Marcação não possui governança sobre o ciclo de vida das interconsultas, operando "no escuro" sem saber a demanda reprimida, o tempo médio de espera e o perfil epidemiológico dos pacientes que aguardam vaga.
*   **Solução:** Centralização estruturada de dados de pacientes (integrados ao AGHU/PostgreSQL), médicos solicitantes e pedidos de interconsulta em um banco de dados relacional robusto. A Central ganha uma fila digital unificada ("Pedidos Ativos") que permite acompanhar o status de cada solicitação (ex: *PENDENTE*, *AGENDADO*, *PROCESSANDO*).
*   **Impacto:** Rastreabilidade ponta a ponta e geração de indicadores de performance que viabilizam uma gestão de saúde preditiva e baseada em dados reais.

### C. Digitalização do Processo de Solicitação
*   **Problema:** O trâmite baseado em guias de papel físicas gera perda de informações, erros crônicos de preenchimento (caligrafia ilegível, campos em branco) e exige o trânsito do paciente ou familiar pelas dependências do hospital.
*   **Solução:** Migração do formulário analógico para uma aplicação web responsiva (Single Page Application - SPA) desenvolvida com Vue 3, TypeScript e Tailwind CSS, integrada a uma API REST robusta construída em Python e FastAPI.
*   **Impacto:** Eliminação do retrabalho de digitação, garantia de consistência dos dados do paciente e agilidade instantânea no trâmite entre a clínica de origem e o setor de marcação.

---

## 3. Nossa solução e protótipo

Nossa solução transforma um processo atualmente manual, descentralizado e analógico em um ecossistema digital inteligente. Ao integrar a digitalização dos formulários, a automação da triagem clínica e a centralização dos dados operacionais, o sistema elimina os gargalos de comunicação, garante critérios justos de priorização baseados no risco do paciente e devolve à central de marcação o controle e a governança de ponta a ponta sobre o fluxo de interconsultas.

### O Protótipo Funcional (MVP)
Para validar a arquitetura e demonstrar a viabilidade prática da solução, desenvolvemos um protótipo funcional completo integrando o Frontend em Vue 3 ao Backend em FastAPI. O protótipo é estruturado em três telas e fluxos principais:

#### A. Login Integrado com Controle de Acesso Corporativo (LDAP / Active Directory)
*   **Interface:** Uma tela de login moderna com identidade visual limpa.
*   **Funcionamento:** Integra-se ao sistema de diretórios corporativo do hospital (AD/Ebserh) através da biblioteca `ldap3`. Quando o médico ou atendente realiza o login:
    *   O sistema valida a senha corporativa via *Simple Bind*.
    *   Buscando no AD, o backend extrai os grupos de segurança do usuário (como `GLO-SEC-HCPE-SETISD` para administradores).
    *   Um token JWT é emitido para controlar a sessão de maneira stateless, acompanhado de um *Refresh Token* seguro e exclusivo do navegador via cookie `HttpOnly`.

#### B. Formulário Digital de Solicitação de Interconsulta com Validação em Tempo Real
*   **Interface:** Uma tela limpa e focada no preenchimento de solicitações.
*   **Segurança no Preenchimento:** O formulário impede erros de digitação validando o **CNS (Cartão Nacional de Saúde)** do paciente para conter exatamente 15 dígitos numéricos antes de permitir o envio.
*   **Catálogo MVP de Sintomas:** O médico seleciona, a partir de caixas de seleção (checkboxes), os sintomas apresentados pelo paciente. O catálogo inicial inclui:
    1.  *Cegueira* (Crítico)
    2.  *Infarto* (Crítico)
    3.  *AVC* (Crítico)
    4.  *Dor torácica intensa* (Moderado)
    5.  *Febre alta* (Moderado)
    6.  *Fratura* (Moderado)

#### C. Painel de Governança e Motor de Risco (Central de Marcação)
*   **Motor de Classificação de Risco:** No momento em que o formulário é enviado, o backend executa instantaneamente o `RiskEngineService` sem acoplamento de banco de dados, aplicando a lógica:
    *   **VERMELHO (Crítico):** Atribuído automaticamente se o paciente apresentar *Cegueira, Infarto ou AVC* (IDs 1, 2, 3).
    *   **AMARELO (Moderado):** Atribuído se apresentar sintomas como *Dor torácica intensa, Febre alta ou Fratura* (IDs 4, 5, 6) e nenhum sintoma crítico.
    *   **VERDE (Baixo):** Classificação padrão para casos sem sintomas críticos ou moderados registrados.
*   **Fila Digital de Pedidos Ativos:** A Central de Marcação tem acesso a uma tabela em tempo real com todos os pedidos ativos. As solicitações são exibidas com distintivos (*badges*) coloridos indicando a gravidade clínica (**VERMELHO**, **AMARELO**, **VERDE**), o código da especialidade e o status atual da solicitação, permitindo que o atendente ordene e atenda os pacientes prioritários primeiro.
*   **Worker de Integração com o AGHU Legacy:** Ao criar uma solicitação, o sistema enfileira o envio do pedido para o sistema legado do hospital utilizando um background worker assíncrono. Esse worker possui uma política resiliente de **Backoff Exponencial** (retentativas com espera de 1s, 2s, 4s...) que garante que o pedido seja transmitido mesmo que a API legado sofra instabilidades temporárias de rede.

---

### Arquitetura de Software do Protótipo (Monólito Multibanco)

Abaixo, descrevemos o fluxo de dados do protótipo, destacando a separação em camadas que assegura a manutenibilidade do código:

```mermaid
graph TD
    User([Médico / Atendente]) -->|Interage| VueApp[Frontend Vue 3 SPA]
    
    subgraph Servidor Monolítico (Python/FastAPI)
        VueApp -->|Consome API REST| Routers[Routers - Entrada de Dados / Pydantic]
        Routers -->|Validação JWT / LDAP| Auth[Módulo de Autenticação AD]
        Routers -->|Executa Regras de Negócio| Controllers[Controllers - Lógica Clínica]
        
        Controllers -->|Chama Serviço de Risco| RiskEngine[RiskEngineService - Cálculo de Gravidade]
        Controllers -->|Envia Pedidos| Broker[Message Broker Assíncrono]
        
        Broker -->|Executa Tarefa Resiliente| Worker[Central de Marcação Worker]
        Controllers -->|Persistência e Acesso| Providers[Data Providers - SQL Nativo]
        
        Providers -->|Busca Estruturada| DatabaseManager[Database Manager]
    end

    DatabaseManager -->|PostgreSQL (asyncpg)| PG[(Banco AGHU - Dados de Pacientes)]
    DatabaseManager -->|SQLite (aiosqlite)| SQLite[(Banco Local - Refresh Tokens & Pedidos)]
    Worker -->|Integração de Fila| LegacyAPI[Sistema Central do AGHU]
```

Este protótipo arquitetado prova que é possível mitigar as filas físicas, digitalizar com segurança os formulários do Hospital das Clínicas e entregar controle preditivo em tempo real para a equipe de gestão de marcação.
