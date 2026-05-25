SELECT 
    lto_id, 
    qrt_numero, 
    unf_seq, 
    ind_situacao 
FROM 
    agh.ain_leitos 
WHERE 
    unf_seq = :setor_id
ORDER BY 
    qrt_numero, lto_id;