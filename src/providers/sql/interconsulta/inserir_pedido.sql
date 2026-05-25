INSERT INTO interconsulta_pedidos (
    paciente_cns,
    medico_solicitante_crm,
    especialidade_id,
    sintomas_json,
    gravidade,
    status,
    criado_em,
    atualizado_em
) VALUES (
    #paciente_cns,
    #medico_solicitante_crm,
    #especialidade_id,
    #sintomas_json,
    #gravidade,
    #status,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
RETURNING id, paciente_cns, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, criado_em, atualizado_em;
