from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Optional, Literal


if TYPE_CHECKING:
	from _typeshed import DataclassInstance

	type DataclassT = DataclassInstance
else:
	from typing import Any

	type DataclassT = Any


class DuplicateKeyException(Exception):
	def __init__(self, entity_name: str):
		super().__init__(f"{entity_name} with this key already exists")


class ReferencedRowExistsError(Exception):
	def __init__(self, entity_name: str, blocking_collection: str):
		super().__init__(
			f"Cannot delete {entity_name}: still referenced in {blocking_collection}"
		)


class AbstractRepository[T](ABC):
	name: str
	entity_cls: type[T]

	@abstractmethod
	def create(self, entity: T) -> T | None: ...

	@abstractmethod
	def get(self, key: dict) -> T | None: ...

	@abstractmethod
	def update(self, key: dict, fields: dict) -> T | None: ...

	@abstractmethod
	def delete(self, key: dict) -> bool: ...

	@abstractmethod
	def list(self, filters: dict = {}) -> list[T]: ...


TipoGrau = Literal["Bacharelado", "Licenciatura Plena"]
TipoTurno = Literal["Matutino", "Vespertino", "Noturno", "Turno Indefinido"]
TipoNivel = Literal["Gradução", "Mestrado", "Doutorado", "Lato"]
StatusEstudante = Literal["Ativo", "Cancelada", "Formando", "Graduado"]


@dataclass
class Usuario:
	cpf: int
	nome: str
	data_nascimento: Optional[date] = None
	email: Optional[list[str]] = None
	telefone: Optional[list[str]] = None
	login: Optional[str] = None
	senha: Optional[str] = None


@dataclass
class Curso:
	idcurso: Optional[int] = None  # SERIAL, None until inserted
	nome: str = ""
	grau: Optional[TipoGrau] = None
	turno: TipoTurno = "Matutino"
	campus: Optional[str] = None
	nivel: Optional[TipoNivel] = None


@dataclass
class Estudante:
	mat_estudante: str
	cpf: Optional[int] = None
	mc: Optional[float] = None
	ano_ingresso: Optional[int] = None


@dataclass
class Vinculo:
	idvinculo: Optional[int] = None  # SERIAL, None until inserted
	mat_estudante: Optional[str] = None
	curso: Optional[int] = None
	data_entrada: Optional[date] = None
	status: Optional[StatusEstudante] = None
	data_saida: Optional[date] = None
