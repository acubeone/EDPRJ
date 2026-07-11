from dataclasses import asdict

from pymongo.errors import DuplicateKeyError

from db import (
	AbstractRepository,
	DataclassT,
	DuplicateKeyException,
	ReferencedRowExistsError,
)
from pymongo.database import Database

import db

REFERENCE_MAP: dict[str, list[tuple[str, str]]] = {
	"curso": [("vinculo", "curso")],
	"estudante": [
		("vinculo", "mat_estudante"),
		("plano", "mat_estudante"),
		("cursa", "mat_estudante"),
	],
	"professor": [
		("plano", "mat_professor"),
		("leciona", "mat_professor"),
		("departamento", "chefe"),
	],
	"departamento": [
		("professor", "departamento"),
		("disciplina", "depto_responsavel"),
	],
	"disciplina": [("turma", "cod_disc"), ("disciplina", "pre_req")],
	"semestre": [("turma", "ano")],
	"turma": [("leciona", "id_turma"), ("alocacao", "id_turma"), ("cursa", "id_turma")],
	"projeto": [("plano", "id_projeto")],
	"usuario": [("professor", "cpf"), ("estudante", "cpf")],
}


class RepositoryMongo[T: DataclassT](AbstractRepository[T]):
	def __init__(self, database: Database) -> None:
		self.database = database
		self.collection = database[self.name]

	def _row_to_entity(self, doc: dict) -> T:
		doc = {k: v for k, v in doc.items() if k != "_id"}
		return self.entity_cls(**doc)

	def _check_no_references(self, key: dict) -> None:
		refs = REFERENCE_MAP.get(self.name, [])
		for ref_collection, ref_field in refs:
			value = next(iter(key.values()))
			if self.database[ref_collection].find_one({ref_field: value}):
				raise ReferencedRowExistsError(self.name, ref_collection)

	def create(self, entity: T) -> T:
		data = {k: v for k, v in asdict(entity).items() if v is not None}

		# Do not accept duplicates
		try:
			self.collection.insert_one(data)
		except DuplicateKeyError:
			raise DuplicateKeyException(self.entity_cls.__name__)

		return self._row_to_entity(data)

	def get(self, key: dict) -> T | None:
		doc = self.collection.find_one(key)
		return self._row_to_entity(doc) if doc else None

	def update(self, key: dict, fields: dict) -> T | None:
		try:
			result = self.collection.update_one(key, {"$set": fields})
		except DuplicateKeyError:
			raise DuplicateKeyException(self.entity_cls.__name__)

		if result.matched_count == 0:
			raise KeyError(f"{self.entity_cls.__name__} with key {key} not found")

		doc = self.collection.find_one(key)
		return self._row_to_entity(doc) if doc else None

	def delete(self, key: dict) -> bool:
		self._check_no_references(key)

		result = self.collection.delete_one(key)
		return result.deleted_count > 0

	def list(self, filters: dict = {}) -> list[T]:
		docs = self.collection.find(filters)
		return [self._row_to_entity(d) for d in docs]


def ensure_indexes(database: Database) -> None:
	# Single PKs
	database["estudante"].create_index("mat_estudante", unique=True)
	database["professor"].create_index("mat_professor", unique=True)
	database["usuario"].create_index("cpf", unique=True)
	database["departamento"].create_index("cod_depto", unique=True)
	database["curso"].create_index("idcurso", unique=True)
	database["projeto"].create_index("id_projeto", unique=True)
	database["disciplina"].create_index("cod_disc", unique=True)
	database["sala"].create_index("id_sala", unique=True)
	database["horario"].create_index("id_horario", unique=True)
	database["turma"].create_index("id_turma", unique=True)
	database["vinculo"].create_index("idvinculo", unique=True)

	# Composite PKs
	database["plano"].create_index([("mat_estudante", 1), ("ano", 1)], unique=True)
	database["semestre"].create_index([("ano", 1), ("semestre", 1)], unique=True)
	database["leciona"].create_index(
		[("id_turma", 1), ("mat_professor", 1)], unique=True
	)
	database["alocacao"].create_index([("id_turma", 1), ("id_horario", 1)], unique=True)
	database["cursa"].create_index([("mat_estudante", 1), ("id_turma", 1)], unique=True)


class UsuarioRepositoryMongo(RepositoryMongo[db.Usuario]):
	collection_name = "usuario"
	entity_cls = db.Usuario


class ProfessorRepositoryMongo(RepositoryMongo[db.Professor]):
	collection_name = "professor"
	entity_cls = db.Professor


class DepartamentoRepositoryMongo(RepositoryMongo[db.Departamento]):
	collection_name = "departamento"
	entity_cls = db.Departamento


class CursoRepositoryMongo(RepositoryMongo[db.Curso]):
	collection_name = "curso"
	entity_cls = db.Curso


class EstudanteRepositoryMongo(RepositoryMongo[db.Estudante]):
	collection_name = "estudante"
	entity_cls = db.Estudante


class VinculoRepositoryMongo(RepositoryMongo[db.Vinculo]):
	collection_name = "vinculo"
	entity_cls = db.Vinculo


class ProjetoRepositoryMongo(RepositoryMongo[db.Projeto]):
	collection_name = "projeto"
	entity_cls = db.Projeto


class PlanoRepositoryMongo(RepositoryMongo[db.Plano]):
	collection_name = "plano"
	entity_cls = db.Plano


class DisciplinaRepositoryMongo(RepositoryMongo[db.Disciplina]):
	collection_name = "disciplina"
	entity_cls = db.Disciplina


class SemestreRepositoryMongo(RepositoryMongo[db.Semestre]):
	collection_name = "semestre"
	entity_cls = db.Semestre


class SalaRepositoryMongo(RepositoryMongo[db.Sala]):
	collection_name = "sala"
	entity_cls = db.Sala


class HorarioRepositoryMongo(RepositoryMongo[db.Horario]):
	collection_name = "horario"
	entity_cls = db.Horario


class TurmaRepositoryMongo(RepositoryMongo[db.Turma]):
	collection_name = "turma"
	entity_cls = db.Turma


class LecionaRepositoryMongo(RepositoryMongo[db.Leciona]):
	collection_name = "leciona"
	entity_cls = db.Leciona


class AlocacaoRepositoryMongo(RepositoryMongo[db.Alocacao]):
	collection_name = "alocacao"
	entity_cls = db.Alocacao


class CursaRepositoryMongo(RepositoryMongo[db.Cursa]):
	collection_name = "cursa"
	entity_cls = db.Cursa
