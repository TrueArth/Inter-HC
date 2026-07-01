## Processo de Validação do Paciente na Criação de Interconsulta

Para simular e garantir a integridade e consistência com o banco hospitalar (AGHU), a arquitetura agora realiza uma verificação síncrona da existência do paciente antes de consolidar o pedido de interconsulta:

1. **Solicitação**: O médico submete a solicitação de interconsulta informando o prontuário (`paciente_prep`).
2. **Verificação (AGHU)**: O `InterconsultaController` consome o `PacienteProviderInterface` (que aponta para a base PostgreSQL, Oracle ou mock CSV do AGHU) chamando `obter_paciente_por_prep(prep)`.
3. **Consistência**: Se o paciente não existir no AGHU, a solicitação é abortada imediatamente com erro `HTTP 400 Bad Request (Paciente não encontrado)`.
4. **Persistência Local**: Após a validação positiva de existência do paciente, a interconsulta é classificada pelo motor de risco, encriptada via AES-256, e salva no banco de dados local.
