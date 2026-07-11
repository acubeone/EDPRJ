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


TipoFormacao = Literal["Gradução", "Especialização", "Mestrado", "Doutorado"]
TipoJornada = Literal["20h", "40h", "DE"]
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
class Professor:
	mat_professor: str
	cpf: Optional[int] = None
	departamento: Optional[str] = None
	formacao: Optional[TipoFormacao] = None
	data_admissao: Optional[date] = None
	tipo_jornada_trabalho: Optional[TipoJornada] = None
	salario: Optional[float] = None


@dataclass
class Departamento:
	cod_depto: str
	nome: str
	chefe: Optional[str] = None
	orcamento: Optional[float] = None
	comissal: Optional[float] = None


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


@dataclass
class Projeto:
	id_projeto: int
	descricao: Optional[str] = None


@dataclass
class Plano:
	id_projeto: Optional[int] = None
	mat_professor: Optional[str] = None
	mat_estudante: str = ""
	ano: int = 0
	# composite PK: (mat_estudante, ano)


@dataclass
class Disciplina:
	cod_disc: str
	nome: str
	pre_req: Optional[str]
	creditos: Optional[int]
	depto_responsavel: Optional[date]


@dataclass
class Semestre:
	ano: int
	semestre: int
	data_inicio: Optional[date] = None
	data_fom: Optional[date] = None
	# composite PK: (ano, semestre)


@dataclass
class Sala:
	id_sala: Optional[int] = None  # SERIAL, None until inserted
	descricao: Optional[str] = None


@dataclass
class Horario:
	id_horario: Optional[int] = None
	dia: str = ""
	slot: int = 0


@dataclass
class Turma:
	id_turma: Optional[int] = None  # from sequence
	cod_disc: str = ""
	numero: Optional[int] = None
	ano: Optional[int] = None
	semestre: Optional[int] = None


@dataclass
class Leciona:
	id_turma: int
	mat_professor: str
	# composite PK: (id_turma, mat_professor)


@dataclass
class Alocacao:
	id_turma: int
	id_horario: int
	id_sala: Optional[int] = None
	# composite PK: (id_turma, id_horario)


@dataclass
class Cursa:
	mat_estudante: str
	id_turma: int
	nota: Optional[float] = None
	# composite PK: (mat_estudante, id_turma)
