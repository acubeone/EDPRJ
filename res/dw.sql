CREATE DATABASE dw_ufs;

CREATE TABLE dim_professor (
    id_professor SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    tipo_jornada VARCHAR(100),
    formacao VARCHAR(100),
    id_departamento INT
);

CREATE TABLE dim_disciplina (
    id_disciplina SERIAL PRIMARY KEY,
    codigo VARCHAR(10),
    nome VARCHAR(100),
    cr_total INT,
    id_departamento INT
);

CREATE TABLE dim_departamento (
    id_departamento SERIAL PRIMARY KEY,
    codigo VARCHAR(100),
    nome VARCHAR(100) 
);

CREATE TABLE dim_semestre (
    id_semestre SERIAL PRIMARY KEY,
    ano INT,
    periodo INT
);

CREATE TABLE dim_campus (
    id_campus SERIAL PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE fato_turma (
    id_fatoturma SERIAL PRIMARY KEY,

    id_professor INT,
    id_disciplina INT,
    id_departamento INT,
    id_semestre INT,

    num_discentes INT,
    media_notas DECIMAL,
    num_aprovados INT,
    num_reprovados INT,

    FOREIGN KEY (id_professor) REFERENCES dim_professor(id_professor),
    FOREIGN KEY (id_disciplina) REFERENCES dim_disciplina(id_disciplina),
    FOREIGN KEY (id_departamento) REFERENCES dim_departamento(id_departamento),
    FOREIGN KEY (id_semestre) REFERENCES dim_semestre(id_semestre)
);