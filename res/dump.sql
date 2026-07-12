CREATE SCHEMA universidade;

CREATE DOMAIN universidade.matricula AS VARCHAR(7);

CREATE DOMAIN universidade.tipo_cpf AS NUMERIC(13);

CREATE TABLE universidade.usuario(
	cpf universidade.tipo_cpf,
	nome	VARCHAR(100) NOT NULL,
	data_nascimento DATE,
	email VARCHAR[],
	telefone VARCHAR[],
	login VARCHAR(45) UNIQUE,
	senha VARCHAR(32),
	CONSTRAINT pk_usuario PRIMARY KEY (cpf)
);

CREATE TYPE universidade.tipo_jornada AS ENUM ('20h', '40h', 'DE');
CREATE TYPE universidade.tipo_formacao AS ENUM ('Graduação', 'Especialização', 'Mestrado', 'Doutorado');


CREATE TYPE universidade.tipo_grau AS ENUM ('Bacharelado', 'Licenciatura Plena');
CREATE TYPE universidade.tipo_nivel AS ENUM ('Graduação', 'Mestrado', 'Doutorado', 'Lato');
CREATE TYPE universidade.tipo_turno AS ENUM ('Matutino', 'Vespertino', 'Noturno', 'Turno Indefinido');

CREATE TABLE universidade.curso(
	idCurso SERIAL PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	grau universidade.tipo_grau,
	turno universidade.tipo_turno NOT NULL,
	campus VARCHAR(100),
	nivel universidade.tipo_nivel,
	CONSTRAINT uq_curso UNIQUE(nome, turno, campus, nivel)

);

CREATE TYPE universidade.status_estudante AS ENUM ('Ativo', 'Cancelada', 'Formando', 'Graduado');

CREATE TABLE universidade.estudante(
	mat_estudante universidade.matricula,
	cpf  universidade.tipo_cpf ,
	MC DECIMAL(2),
	ano_ingresso INT,

	CONSTRAINT pk_estudante PRIMARY KEY(mat_estudante),
	CONSTRAINT fk_usuario FOREIGN KEY (cpf) REFERENCES universidade.usuario(cpf)
	ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT uq_cpf UNIQUE(cpf)

);

CREATE TABLE universidade.vinculo(
	idVinculo SERIAL PRIMARY KEY,
	mat_estudante universidade.matricula,
	curso INT,
	data_entrada DATE,
	status universidade.status_estudante,
	data_saida DATE,
	CONSTRAINT fk_curso FOREIGN KEY (curso) REFERENCES universidade.curso(idCurso)
	ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT fk_estudabte FOREIGN KEY (mat_estudante) REFERENCES universidade.estudante(mat_estudante)
	ON DELETE SET NULL ON UPDATE CASCADE
);