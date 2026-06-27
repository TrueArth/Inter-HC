# analytics-dashboard Specification

## Purpose
Fornecer à administração e à coordenação da Central de Regulação uma interface analítica contendo KPIs regulatórios chave e a capacidade de exportação desses dados para planilhas do Microsoft Excel.

## Requirements

### Requirement: Exibição de KPIs Analíticos
O painel administrativo do sistema MUST exibir KPIs atualizados baseados nas solicitações de interconsultas ativas. Os seguintes KPIs MUST ser visíveis na interface:
1. **Total de interconsultas**: O volume absoluto de solicitações ativas inseridas no sistema.
2. **Total de interconsultas por especialidade**: Distribuição detalhada da demanda de solicitações agrupadas por especialidade médica.
3. **Tempo médio de atendimento da marcação**: A média do tempo decorrido entre a criação da solicitação (`criado_em`) e a efetivação do agendamento (`atualizado_em` quando o status é definido como 'AGENDADO').
4. **Especialidades com mais pendências**: Um ranking das especialidades médicas com o maior volume de solicitações ativas no status 'PENDENTE'.

#### Scenario: Visualização do Dashboard pelo Admin
- **WHEN** um usuário com perfil 'admin' acessar a aba 'Estatísticas' do painel administrativo
- **THEN** o sistema carrega e renderiza os cards contendo o Total de Interconsultas, o Tempo Médio de Atendimento da Marcação, o gráfico de barras/ranking de demanda por especialidade e a lista com as especialidades com mais pendências ativas.

### Requirement: Exportação para Excel (.xlsx)
O sistema MUST expor uma funcionalidade que compile os dados regulatórios consolidados e detalhados em um arquivo em formato Excel (`.xlsx`). O arquivo gerado MUST conter abas separadas para:
- **Geral**: Um resumo contendo os KPIs analíticos globais.
- **Solicitacoes**: Uma tabela detalhada de todos os pedidos ativos (com o número do PREP do paciente decifrado e legível).
- **Demanda por Especialidade**: Tabela de contagem por especialidade.
- **Pendencias por Especialidade**: Tabela de contagem de pedidos pendentes por especialidade.

#### Scenario: Exportar Planilha de Estatísticas
- **WHEN** o administrador clicar no botão "Exportar para Excel" na interface do painel administrativo
- **THEN** o sistema solicita o download do arquivo `analytics_interhc.xlsx`, realiza o registro de auditoria no log do backend e baixa o arquivo contendo todas as planilhas descritas.
