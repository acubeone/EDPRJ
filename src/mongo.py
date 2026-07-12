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
	# PKs
	database["usuario"].create_index("cpf", unique=True)
	database["curso"].create_index("idcurso", unique=True)
	database["estudante"].create_index("mat_estudante", unique=True)
	database["vinculo"].create_index("idvinculo", unique=True)


class UsuarioRepositoryMongo(RepositoryMongo[db.Usuario]):
	name = "usuario"
	entity_cls = db.Usuario


class CursoRepositoryMongo(RepositoryMongo[db.Curso]):
	name = "curso"
	entity_cls = db.Curso


class EstudanteRepositoryMongo(RepositoryMongo[db.Estudante]):
	name = "estudante"
	entity_cls = db.Estudante


class VinculoRepositoryMongo(RepositoryMongo[db.Vinculo]):
	name = "vinculo"
	entity_cls = db.Vinculo
