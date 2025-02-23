-- criação de tabela, tipos do bigquery
-- trm é o dataset, caso utilize o bigquery
create table trm.historico_consumo (
    id_treated_data STRING, -- uuid gerado
    id_curral INT64,
    id_raca INT64,
    id_lote INT64,
    peso_entrada FLOAT64,
    peso_medio FLOAT64,
    quantidade_animais INT64,
    dia_confinamento INT64,
    consumo_real FLOAT64, 
    consumo_meta FLOAT64,  
    data TIMESTAMP,
    cod_cliente STRING, -- pode ser fixo, variável cod_cliente
    row_ts TIMESTAMP -- data hora de processamento
)