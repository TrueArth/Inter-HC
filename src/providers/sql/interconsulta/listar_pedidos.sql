SELECT 
    id, 
    paciente_prep, 
    paciente_contato,
    medico_solicitante_crm, 
    especialidade_id, 
    sintomas_json, 
    gravidade, 
    status, 
    marcado_por,
    data_consulta,
    motivo_negacao,
    criado_em, 
    atualizado_em
FROM interconsulta_pedidos
WHERE deleted_at IS NULL
ORDER BY 
    CASE gravidade
        WHEN 'VERMELHO' THEN 1
        WHEN 'AMARELO' THEN 2
        WHEN 'VERDE' THEN 3
        ELSE 4
    END,
    criado_em ASC;
