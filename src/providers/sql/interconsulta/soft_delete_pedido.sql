UPDATE interconsulta_pedidos
SET 
    deleted_at = CURRENT_TIMESTAMP,
    atualizado_em = CURRENT_TIMESTAMP
WHERE id = #id
  AND deleted_at IS NULL
RETURNING id, deleted_at;
