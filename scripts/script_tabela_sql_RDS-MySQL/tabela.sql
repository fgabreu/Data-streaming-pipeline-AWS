CREATE DATABASE fazendas, -- Criando o banco na instancia RDS MySQL - dsm-case

USE fazendas; -- Seleciona o banco de dados 'fazendas'

CREATE TABLE historico_consumo (
    id_treated_data VARCHAR(36), -- UUID gerado, VARCHAR(36) é suficiente
    id_curral INT,
    id_raca INT,
    id_lote INT,
    peso_entrada DOUBLE, -- FLOAT64 vira DOUBLE no MySQL
    peso_medio DOUBLE, -- FLOAT64 vira DOUBLE no MySQL
    quantidade_animais INT,
    dia_confinamento INT,
    consumo_real DOUBLE, -- FLOAT64 vira DOUBLE no MySQL
    consumo_meta DOUBLE, -- FLOAT64 vira DOUBLE no MySQL
    data DATETIME, -- TIMESTAMP vira DATETIME no MySQL
    cod_cliente VARCHAR(50), -- Tamanho ajustável conforme necessário
    row_ts DATETIME -- TIMESTAMP vira DATETIME no MySQL
);