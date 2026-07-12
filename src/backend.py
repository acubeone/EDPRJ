import os

import postgres
import mongo

import pymongo as mg
import psycopg as pg

from dotenv import load_dotenv
from psycopg.connection import Connection
from pymongo.database import Database

from db import AbstractRepository

load_dotenv()

DEFAULT_TIMEOUT = 5000  # 5 seconds

REPO_REGISTRY_PG = {
	"usuario": postgres.UsuarioRepositoryPG,
	"curso": postgres.CursoRepositoryPG,
	"estudante": postgres.EstudanteRepositoryPG,
	"vinculo": postgres.VinculoRepositoryPG,
}

REPO_REGISTRY_MONGO = {
	"usuario": mongo.UsuarioRepositoryMongo,
	"curso": mongo.CursoRepositoryMongo,
	"estudante": mongo.EstudanteRepositoryMongo,
	"vinculo": mongo.VinculoRepositoryMongo,
}


class Backend:
	def __init__(self, kind: str):
		if kind not in ["postgres", "mongo"]:
			raise ValueError(f"Unknown backend: {self.kind}")

		self.kind = kind
		self._conn: Database | Connection | None = None

	def _ensure_alive(self) -> None:
		if (
			self.kind == "postgres"
			and isinstance(self._conn, Connection)
			and self._conn.closed
		):
			self.connect()
		elif self.kind == "mongo" and isinstance(self._conn, Database):
			try:
				self._conn.client.admin.command("ping")
			except Exception:
				self.connect()

	def connect(self) -> Database | Connection:
		if self.kind == "postgres":
			uri = (
				f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
				f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/"
				f"{os.environ['DB_NAME']}"
			)
			self._conn = pg.connect(uri, connect_timeout=DEFAULT_TIMEOUT)
		elif self.kind == "mongo":
			uri = (
				f"mongodb://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
				f"@{os.environ['MONGO_HOST']}:{os.environ['MONGO_PORT']}/"
				f"{os.environ['DB_NAME']}?authSource=admin"
			)
			client = mg.MongoClient(uri, serverSelectionTimeoutMS=DEFAULT_TIMEOUT)
			# Forces connection, so raises exception if server is unreachable
			client.admin.command("ping")
			self._conn = client[os.environ["DB_NAME"]]
		else:
			raise ValueError(f"Unknown backend: {self.kind}")

		assert self._conn is not None
		return self._conn

	def close(self) -> None:
		if self.kind == "postgres" and isinstance(self._conn, Connection):
			self._conn.close()
		elif self.kind == "mongo" and isinstance(self._conn, Database):
			self._conn.client.close()

	def get_repository(
		self,
		entity_name: str,
	) -> AbstractRepository:
		self._ensure_alive()
		registry = REPO_REGISTRY_PG if self.kind == "postgres" else REPO_REGISTRY_MONGO
		return registry[entity_name](self._conn)
