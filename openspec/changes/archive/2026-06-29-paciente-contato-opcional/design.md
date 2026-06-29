## Context

Para facilitar a comunicação e regulação dos pacientes regulados, o sistema de interconsulta passará a coletar opcionalmente o número de contato do paciente no formato `(dd) xxxxx-xxxx` ou `(dd) xxxx-xxxx`.

## Goals / Non-Goals

**Goals:**
* Armazenar o campo `paciente_contato` de forma criptografada usando Fernet (AES-128-CBC + HMAC) no banco de dados SQLite e no Mock.
* Validar e normalizar o número de telefone no frontend e no backend.
* Disponibilizar o número decifrado na tabela de visualização e detalhes do regulador.
* Exportar o número na aba de detalhes da Fila Reguladora no Excel.

**Non-Goals:**
* O número de telefone de contato não será compartilhado com o Message Broker se o AGHU não suportar este campo ou se não estiver mapeado no payload de integração externa.

## Decisions

### 1. Modelo de Banco de Dados (SQLAlchemy)
```python
# src/models/interconsulta.py
class InterconsultaPedido(Base):
    # ...
    paciente_contato = Column(String, nullable=True) # Telefone criptografado com AES-256
```

### 2. Validação Regex no Pydantic Schema
```python
# src/schemas/interconsulta_schema.py
import re

@field_validator("paciente_contato")
@classmethod
def validate_contato_format(cls, v: Optional[str]) -> Optional[str]:
    if not v:
        return None
    v_clean = v.strip()
    # Regex flexível para (dd) xxxxx-xxxx ou (dd) xxxx-xxxx, com ou sem espaços
    regex = r"^\(\d{2}\)\s?\d{4,5}-\s?\d{4}$"
    if not re.match(regex, v_clean):
        raise ValueError("O número de contato do paciente deve estar no formato (dd) xxxxx-xxxx ou (dd) xxxx-xxxx.")
    return v_clean
```

### 3. Modificação dos Arquivos SQL Nativo
* **`inserir_pedido.sql`**: Inclusão de `paciente_contato` e `#paciente_contato`.
* **`listar_pedidos.sql`**: Inclusão de `paciente_contato` no `SELECT`.

## Risks / Trade-offs

* **Dados Pessoais (LGPD):** O vazamento de telefones de pacientes é uma violação de privacidade.
  * *Mitigação*: Criptografia simétrica Fernet (AES-128-CBC + HMAC) em repouso na base de dados SQLite local.
