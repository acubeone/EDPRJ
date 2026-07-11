from dataclasses import asdict
import os

import psycopg as pg
from psycopg import sql
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from psycopg.rows import dict_row
from pymongo.errors import DuplicateKeyError

import db
from db import AbstractRepository, DataclassT


def get_connection() -> pg.Connection:
	return pg.connect(
		dbname=os.environ["DB_NAME"],
		user=os.environ["DB_USER"],
		password=os.environ["DB_PASSWORD"],
		host=os.environ["DB_HOST"],
		port=os.environ["DB_PORT"],
	)


class RepositoryPG[T: DataclassT](AbstractRepository[T]):
	def __init__(self, conn: pg.Connection) -> None:
		self.conn = conn
		self._schema, self._table = self.name.split(".")

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

	def create(self, entity: T) -> T | None:
		data = {k: v for k, v in asdict(entity).items() if v is not None}
		query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
			self._table_ident,
			sql.SQL(", ").join(sql.Identifier(c) for c in data),
			sql.SQL(", ").join(sql.Placeholder(c) for c in data),
		)

		# Do not accept duplicates
		try:
			with self.conn.cursor(row_factory=dict_row) as cur:
				cur.execute(query, data)
				row = cur.fetchone()
			self.conn.commit()
		except UniqueViolation:
			self.conn.rollback()  # Revert any violations
			raise DuplicateKeyError(self.entity_cls.__name__)

		return self._row_to_entity(row) if row else None

	def get(self, key: dict) -> T | None:
		query = sql.SQL("SELECT * FROM {} WHERE {}").format(
			self._table_ident, self._where_sql(key)
		)

		with self.conn.cursor(row_factory=dict_row) as cur:
			cur.execute(query, key)
			row = cur.fetchone()

		return self._row_to_entity(row) if row else None

	def update(self, key: dict, fields: dict) -> T | None:
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

		try:
			with self.conn.cursor(row_factory=dict_row) as cur:
				cur.execute(query, {**set_params, **key})
				row = cur.fetchone()
			self.conn.commit()
		except UniqueViolation:
			self.conn.rollback()
			raise DuplicateKeyError(self.entity_cls.__name__)
		except ForeignKeyViolation:
			self.conn.rollback()
			raise ReferenceError(
				f"{self.entity_cls.__name__} update referecens a nonexistent row"
			)

		return self._row_to_entity(row) if row else None

	def delete(self, key: dict) -> bool:
		query = sql.SQL("DELETE FROM {} WHERE {}").format(
			self._table_ident, self._where_sql(key)
		)

		try:
			with self.conn.cursor() as cur:
				cur.execute(query, key)
				deleted = cur.rowcount > 0
			self.conn.commit()
		except ForeignKeyViolation:
			self.conn.rollback()
			raise ReferenceError(
				f"{self.entity_cls.__name__} is still referenced by other rows"
			)

		return deleted

	def list(self, filters: dict = {}) -> list[T]:
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
	name = "universidade.usuario"
	entity_cls = db.Usuario


class ProfessorRepositoryPG(RepositoryPG[db.Professor]):
	name = "universidade.professor"
	entity_cls = db.Professor


class DepartamentoRepositoryPG(RepositoryPG[db.Departamento]):
	name = "universidade.departamento"
	entity_cls = db.Departamento


class CursoRepositoryPG(RepositoryPG[db.Curso]):
	name = "universidade.curso"
	entity_cls = db.Curso


class EstudanteRepositoryPG(RepositoryPG[db.Estudante]):
	name = "universidade.estudante"
	entity_cls = db.Estudante


class VinculoRepositoryPG(RepositoryPG[db.Vinculo]):
	name = "universidade.vinculo"
	entity_cls = db.Vinculo


class ProjetoRepositoryPG(RepositoryPG[db.Projeto]):
	name = "universidade.projeto"
	entity_cls = db.Projeto


class PlanoRepositoryPG(RepositoryPG[db.Plano]):
	name = "universidade.plano"
	entity_cls = db.Plano


class DisciplinaRepositoryPG(RepositoryPG[db.Disciplina]):
	name = "universidade.disciplina"
	entity_cls = db.Disciplina


class SemestreRepositoryPG(RepositoryPG[db.Semestre]):
	name = "universidade.semestre"
	entity_cls = db.Semestre


class SalaRepositoryPG(RepositoryPG[db.Sala]):
	name = "universidade.sala"
	entity_cls = db.Sala


class HorarioRepositoryPG(RepositoryPG[db.Horario]):
	name = "universidade.horario"
	entity_cls = db.Horario


class TurmaRepositoryPG(RepositoryPG[db.Turma]):
	name = "universidade.turma"
	entity_cls = db.Turma


class LecionaRepositoryPG(RepositoryPG[db.Leciona]):
	name = "universidade.leciona"
	entity_cls = db.Leciona


class AlocacaoRepositoryPG(RepositoryPG[db.Alocacao]):
	name = "universidade.alocacao"
	entity_cls = db.Alocacao


class CursaRepositoryPG(RepositoryPG[db.Cursa]):
	name = "universidade.cursa"
	entity_cls = db.Cursa
