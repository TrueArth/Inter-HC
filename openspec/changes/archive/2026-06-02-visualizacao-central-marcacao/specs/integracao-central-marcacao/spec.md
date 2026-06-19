## ADDED Requirements

### Requirement: Disparo Manual de Re-enfileiramento
O sistema MUST permitir que uma tentativa de envio com status de 'ERRO' seja re-enfileirada de forma manual, reiniciando o fluxo assíncrono de envio para a Central de Marcação do AGHU.

#### Scenario: Re-envio Manual com Sucesso
- **WHEN** o operador da Central de Marcação aciona a opção "Re-enviar" em um pedido com falha
- **THEN** o worker do Message Broker é acionado para tentar processar o envio novamente, alterando o status do pedido local para 'ENFILEIRADO'.
