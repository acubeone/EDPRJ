from dataclasses import asdict
import os
from typing import TYPE_CHECKING

import psycopg as pg
from psycopg import sql
from psycopg.rows import DictRow, dict_row

import db
from db import AbstractRepository

if TYPE_CHECKING:
	from _typeshed import DataclassInstance

	type DataclassT = DataclassInstance
else:
	from typing import Any

	type DataclassT = Any


def get_connection() -> pg.Connection:
	return pg.connect(
		dbname=os.environ["DB_NAME"],
		user=os.environ["DB_USER"],
		password=os.environ["DB_PASSWORD"],
		host=os.environ["DB_HOST"],
		port=os.environ["DB_PORT"],
	)


class RepositoryPG[T: DataclassT](AbstractRepository[T]):
	conn: pg.Connection
	table_name: str
	entity_cls: type[T]

	def __init__(self, conn: pg.Connection) -> None:
		self.conn = conn
		self._schema, self._table = self.table_name.split(".")

	@property
	def _table_ident(self) -> sql.Identifier:
		return sql.Identifier(self._schema, self._table)

	def _row_to_entity(self, row: dict) -> T:
		return self.entity_cls(**row)

	def _where_sql(self, key: dict) -> sql.Composed:
		return sql.SQL(" AND ").join(
			sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder(col))
			for col in key
		)

	def create(self, entity: T) -> T:
		data = {k: v for k, v in asdict(entity).items() if v is not None}
		query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
			self._table_ident,
			sql.SQL(", ").join(sql.Identifier(c) for c in data),
			sql.SQL(", ").join(sql.Placeholder(c) for c in data),
		)

		with self.conn.cursor(row_factory=dict_row) as cur:
			cur.execute(query, data)
			row = cur.fetchone()

		self.conn.commit()
		assert row is not None, "Failed to fetch row"
		return self._row_to_entity(row)

	def get(self, key: dict) -> T | None:
		query = sql.SQL("SELECT * FROM {} WHERE {}").format(
			self._table_ident, self._where_sql(key)
		)

		with self.conn.cursor(row_factory=dict_row) as cur:
			cur.execute(query, key)
			row = cur.fetchone()

		return self._row_to_entity(row) if row else None

	def update(self, key: dict, fields: dict) -> T:
		set_params = {f"set_{k}": v for k, v in fields.items()}
		set_sql = sql.SQL(", ").join(
			sql.SQL("{} = {}").format(
				sql.Identifier(col), sql.Placeholder(f"set_{col}")
			)
			for col in fields
		)

		query = sql.SQL("UPDATE {} SET {} WHERE {} RETURNING *").format(
			self._table_ident, set_sql, self._where_sql(key)
		)
		with self.conn.cursor(row_factory=dict_row) as cur:
			cur.execute(query, {**set_params, **key})
			row = cur.fetchone()

		self.conn.commit()
		assert row is not None, "Failed to fetch row"
		return self._row_to_entity(row)

	def delete(self, key: dict) -> bool:
		query = sql.SQL("DELETE FROM {} WHERE {}").format(
			self._table_ident, self._where_sql(key)
		)
		with self.conn.cursor() as cur:
			cur.execute(query, key)
			deleted = cur.rowcount > 0

		self.conn.commit()
		return deleted

	def list(self, filters: dict | None = None) -> list[T]:
		if filters:
			query = sql.SQL("SELECT * FROM {} WHERE {}").format(
				self._table_ident, self._where_sql(filters)
			)
			params = filters
		else:
			query = sql.SQL("SELECT * FROM {}").format(self._table_ident)
			params = {}

		with self.conn.cursor(row_factory=dict_row) as cur:
			cur.execute(query, params)
			rows = cur.fetchall()

		return [self._row_to_entity(row) for row in rows]


class UsuarioRepositoryPG(RepositoryPG[db.Usuario]):
	table_name = "universidade.usuario"
	entity_cls = db.Usuario


class ProfessorRepositoryPG(RepositoryPG[db.Professor]):
	table_name = "universidade.professor"
	entity_cls = db.Professor


class DepartamentoRepositoryPG(RepositoryPG[db.Departamento]):
	table_name = "universidade.departamento"
	entity_cls = db.Departamento


class CursoRepositoryPG(RepositoryPG[db.Curso]):
	table_name = "universidade.curso"
	entity_cls = db.Curso


class EstudanteRepositoryPG(RepositoryPG[db.Estudante]):
	table_name = "universidade.estudante"
	entity_cls = db.Estudante


class VinculoRepositoryPG(RepositoryPG[db.Vinculo]):
	table_name = "universidade.vinculo"
	entity_cls = db.Vinculo


class ProjetoRepositoryPG(RepositoryPG[db.Projeto]):
	table_name = "universidade.projeto"
	entity_cls = db.Projeto


class PlanoRepositoryPG(RepositoryPG[db.Plano]):
	table_name = "universidade.plano"
	entity_cls = db.Plano


class DisciplinaRepositoryPG(RepositoryPG[db.Disciplina]):
	table_name = "universidade.disciplina"
	entity_cls = db.Disciplina


class SemestreRepositoryPG(RepositoryPG[db.Semestre]):
	table_name = "universidade.semestre"
	entity_cls = db.Semestre


class SalaRepositoryPG(RepositoryPG[db.Sala]):
	table_name = "universidade.sala"
	entity_cls = db.Sala


class HorarioRepositoryPG(RepositoryPG[db.Horario]):
	table_name = "universidade.horario"
	entity_cls = db.Horario


class TurmaRepositoryPG(RepositoryPG[db.Turma]):
	table_name = "universidade.turma"
	entity_cls = db.Turma


class LecionaRepositoryPG(RepositoryPG[db.Leciona]):
	table_name = "universidade.leciona"
	entity_cls = db.Leciona


class AlocacaoRepositoryPG(RepositoryPG[db.Alocacao]):
	table_name = "universidade.alocacao"
	entity_cls = db.Alocacao


class CursaRepositoryPG(RepositoryPG[db.Cursa]):
	table_name = "universidade.cursa"
	entity_cls = db.Cursa


REPO_REGISTRY_PG = {
	"usuario": UsuarioRepositoryPG,
	"professor": ProfessorRepositoryPG,
	"departamento": DepartamentoRepositoryPG,
	"curso": CursaRepositoryPG,
	"estudante": EstudanteRepositoryPG,
	"vinculo": VinculoRepositoryPG,
	"projeto": ProjetoRepositoryPG,
	"plano": PlanoRepositoryPG,
	"disciplina": DisciplinaRepositoryPG,
	"semestre": SemestreRepositoryPG,
	"sala": SalaRepositoryPG,
	"horario": HorarioRepositoryPG,
	"turma": TurmaRepositoryPG,
	"leciona": LecionaRepositoryPG,
	"alocacao": AlocacaoRepositoryPG,
	"cursa": CursaRepositoryPG,
}


def get_repository(entity_name: str, conn: pg.Connection) -> RepositoryPG:
	return REPO_REGISTRY_PG[entity_name](conn)
