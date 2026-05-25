# Arquitetura e Segurança

## 1. Arquitetura da Solução
### Front-End
* Desenvolvido como uma SPA (Single Page Application) de alta fidelidade.
* **Interface médica**: Foco em UX intuitiva para entrada de dados de gravidade.
* **Interface da central de marcação**: Dashboard com tabelas atualizadas em tempo real para gestão de marcações.
### Back-End
* API isolada com o Motor de Regras (calculadora de gravidade).
### Integrações
*  API Gateway (ponte de comunicação com o AGHU).
### Outros
* Banco de Dados Relacional próprio (armazenar rastreabilidade "De/Para").

## 2. Stack tecnológica e Framework
### Front-End
* Uso de Vue 3 + Vite para desenvolvimento rápido e uma interface reativa.

### Back-End
* FastAPI
* Documentação de API automática via Swagger/OpenAPI.

### Estrutura escalável
* Separação de reponsabilidades entre Routers, Controllers e Providers.
* Arquitetura de provedores que permite trocar a fonte dos dados facilmente.


## 3. Conformidade LGPD
* Anonimização e gestão de consentimento (TCLE).

## 4. Acessos
* RBAC e MFA.

## 5. Guardrails para IA (SDD)
Para manter a integridade sistêmica, os assistentes de IA devem aderir às seguintes restrições:

### Escopo Positivo (O que fazer)
- **Documentação de Código**: Comentar funções complexas seguindo o padrão JSDoc/TSDoc.
- **Tratamento de Erros**: Utilizar blocos try-catch com logs de erro padronizados.
- **Testes**: Criar um arquivo de teste `.spec.ts` para cada novo controller ou service.

### Escopo Negativo (O que NÃO fazer - Anti-Patterns)
- **No Hard Deletes**: Proibido o uso de `DELETE` SQL. Utilizar coluna `deleted_at`.
- **No Secrets in Code**: Proibido salvar chaves de API ou senhas no código; utilizar `.env`.
- **No Refactoring Unasked**: Não alterar arquivos de infraestrutura ou configuração global sem instrução explícita no `SPEC.md`.