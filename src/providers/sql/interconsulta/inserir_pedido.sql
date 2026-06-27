INSERT INTO interconsulta_pedidos (
    paciente_prep,
    medico_solicitante_crm,
    especialidade_id,
    sintomas_json,
    gravidade,
    status,
    marcado_por,
    criado_em,
    atualizado_em
) VALUES (
    #paciente_prep,
    #medico_solicitante_crm,
    #especialidade_id,
    #sintomas_json,
    #gravidade,
    #status,
    #marcado_por,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
RETURNING id, paciente_prep, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, marcado_por, data_consulta, criado_em, atualizado_em;
