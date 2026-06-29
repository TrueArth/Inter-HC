INSERT INTO interconsulta_pedidos (
    paciente_prep,
    paciente_contato,
    medico_solicitante_crm,
    especialidade_id,
    sintomas_json,
    gravidade,
    status,
    marcado_por,
    motivo_negacao,
    criado_em,
    atualizado_em
) VALUES (
    #paciente_prep,
    #paciente_contato,
    #medico_solicitante_crm,
    #especialidade_id,
    #sintomas_json,
    #gravidade,
    #status,
    #marcado_por,
    #motivo_negacao,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
RETURNING id, paciente_prep, paciente_contato, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, marcado_por, data_consulta, motivo_negacao, criado_em, atualizado_em;
