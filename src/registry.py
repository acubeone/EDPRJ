from pymongo.database import Database

from pyscopg import Connection

from db import AbstractRepository
import postgres as pg
import mongo as mg


REPO_REGISTRY_PG = {
	"usuario": pg.UsuarioRepositoryPG,
	"professor": pg.ProfessorRepositoryPG,
	"departamento": pg.DepartamentoRepositoryPG,
	"curso": pg.CursaRepositoryPG,
	"estudante": pg.EstudanteRepositoryPG,
	"vinculo": pg.VinculoRepositoryPG,
	"projeto": pg.ProjetoRepositoryPG,
	"plano": pg.PlanoRepositoryPG,
	"disciplina": pg.DisciplinaRepositoryPG,
	"semestre": pg.SemestreRepositoryPG,
	"sala": pg.SalaRepositoryPG,
	"horario": pg.HorarioRepositoryPG,
	"turma": pg.TurmaRepositoryPG,
	"leciona": pg.LecionaRepositoryPG,
	"alocacao": pg.AlocacaoRepositoryPG,
	"cursa": pg.CursaRepositoryPG,
}

REPO_REGISTRY_MONGO = {
	"usuario": mg.UsuarioRepositoryMongo,
	"professor": mg.ProfessorRepositoryMongo,
	"departamento": mg.DepartamentoRepositoryMongo,
	"curso": mg.CursoRepositoryMongo,
	"estudante": mg.EstudanteRepositoryMongo,
	"vinculo": mg.VinculoRepositoryMongo,
	"projeto": mg.ProjetoRepositoryMongo,
	"plano": mg.PlanoRepositoryMongo,
	"disciplina": mg.DisciplinaRepositoryMongo,
	"semestre": mg.SemestreRepositoryMongo,
	"sala": mg.SalaRepositoryMongo,
	"horario": mg.HorarioRepositoryMongo,
	"turma": mg.TurmaRepositoryMongo,
	"leciona": mg.LecionaRepositoryMongo,
	"alocacao": mg.AlocacaoRepositoryMongo,
	"cursa": mg.CursaRepositoryMongo,
}


def get_repository(
	entity_name: str,
	backend: str,
	conn_or_db: Connection | Database,
) -> AbstractRepository:
	if backend == "postgres":
		if not isinstance(conn_or_db, Connection):
			raise ValueError("conn_or_db should be a pyscopg.Connection!")

		return REPO_REGISTRY_PG[entity_name](conn_or_db)
	elif backend == "mongo":
		if not isinstance(conn_or_db, Database):
			raise ValueError("conn_or_db should be a pymongo.database.Database!")

		return REPO_REGISTRY_MONGO[entity_name](conn_or_db)

	raise ValueError(f"Unknown backend: {backend}")
