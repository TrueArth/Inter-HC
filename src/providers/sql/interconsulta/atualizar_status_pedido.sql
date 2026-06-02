UPDATE interconsulta_pedidos
SET status = #status, atualizado_em = CURRENT_TIMESTAMP
WHERE id = #id AND deleted_at IS NULL
RETURNING id, status, atualizado_em;
