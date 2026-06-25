## Context

Atualmente, o sistema InterHC utiliza autenticação Mock via `MockAuthProvider` com três usuários estáticos com papéis pré-definidos (admin, medico, regulador). Não há controle de acesso e isolamento estrito de rotas no Vue Router, e a interface exibe as abas/telas de forma indistinta para todos os perfis. As cores da interface são verdes genéricas, e existe a rota `/exemplos` que precisa ser removida. O drawer de detalhes da Central de Marcação possui um bug onde os sintomas não são exibidos por causa de um filtro de serialização do Pydantic. Além disso, não há rastreabilidade de qual regulador realizou a marcação das consultas.

## Goals / Non-Goals

**Goals:**
* Prover controle de acesso visual e de rotas (role isolation) no frontend e backend.
* Implementar a persistência local e CRUD de usuários no painel Admin, incluindo o Soft Delete `deleted_at`.
* Modificar a paleta de cores padrão do frontend para tons azuis inspirados no HC-UFPE.
* Corrigir a serialização do Pydantic no backend e exibição correspondente no frontend para listar os sintomas no drawer.
* Integrar o nome de usuário do regulador (`marcado_por`) no pedido de agendamento.
* Remover por completo a seção "Exemplos" do frontend.

**Non-Goals:**
* Não será implementado login integrado com Active Directory real de produção nesta etapa (apenas preparação do Mock/Database provider de desenvolvimento).
* Não faremos Hard Delete de dados de usuários ou pedidos.

## Decisions

### 1. Novo Esquema de Banco de Dados Local (SQLAlchemy)

Será criada a tabela `users` no banco de dados local SQLite/PostgreSQL para armazenar usuários e papéis.

```python
# src/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.resources.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, medico, regulador
    email = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
```

### 2. Modificação na Tabela de Interconsultas

Adicionar a coluna `marcado_por` na tabela `interconsulta_pedidos` para fins de auditoria.

```python
# src/models/interconsulta.py
# Adicionar:
marcado_por = Column(String, nullable=True)
```

### 3. Queries SQL Nativas Geradas

* **Inserir Usuário:** `src/providers/sql/user/inserir_usuario.sql`
  ```sql
  INSERT INTO users (username, hashed_password, display_name, role, email, created_at, updated_at)
  VALUES (#username, #hashed_password, #display_name, #role, #email, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
  RETURNING id, username, display_name, role, email, created_at, updated_at;
  ```
* **Listar Usuários Ativos:** `src/providers/sql/user/listar_usuarios.sql`
  ```sql
  SELECT id, username, display_name, role, email, created_at, updated_at 
  FROM users 
  WHERE deleted_at IS NULL;
  ```
* **Atualizar Usuário:** `src/providers/sql/user/atualizar_usuario.sql`
  ```sql
  UPDATE users 
  SET display_name = #display_name, role = #role, email = #email, updated_at = CURRENT_TIMESTAMP
  WHERE id = #id AND deleted_at IS NULL
  RETURNING id, username, display_name, role, email, updated_at;
  ```
* **Deletar Usuário (Soft Delete):** `src/providers/sql/user/deletar_usuario.sql`
  ```sql
  UPDATE users 
  SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = #id AND deleted_at IS NULL
  RETURNING id;
  ```

### 4. Correções e Roteamento de Segurança
* **Authentication Fallback:** O `auth_handler` tentará autenticar no banco de dados local caso o AD/LDAP não esteja configurado. Se o banco não possuir nenhum usuário cadastrado, um usuário `admin` padrão (`admin`/`admin`) será criado na primeira inicialização para permitir o acesso.
* **Isolamento no Vue Router:** O token JWT decodificado no frontend fornecerá os grupos/role do usuário. O Router do Vue validará os papéis por rota (`requiresAuth`, `allowedRoles` no meta) e impedirá acessos indevidos.

## Risks / Trade-offs

* **[Risco] Incompatibilidade com migrações antigas ou ausência do campo no banco já existente**  
  ➔ *Mitigação*: Executar script de migração no startup para adicionar a coluna `marcado_por` à tabela de `interconsulta_pedidos` caso não exista, e criar a tabela `users`.
* **[Risco] Vulnerabilidade de senhas armazenadas localmente**  
  ➔ *Mitigação*: Armazenar senhas cifradas com `bcrypt` no banco de dados local.
