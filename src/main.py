import sys
import dotenv

import postgres
import db


def main() -> int | None:
	dotenv.load_dotenv()

	conn = postgres.get_connection()

	repo = postgres.EstudanteRepositoryPG(conn)

	# CREATE
	new = db.Estudante(mat_estudante="2021001", cpf=None, mc=None, ano_ingresso=2021)
	created = repo.create(new)
	print("created: ", created)

	# GET
	found = repo.get({"mat_estudante": "2021001"})
	print("get: ", found)

	# UPDATE
	updated = repo.update({"mat_estudante": "2021001"}, {"ano_ingresso": 2022})
	print("updated: ", updated)

	# LIST
	all_estudantes = repo.list()
	print("list:", all_estudantes)

	# DELETE
	deleted = repo.delete({"mat_estudante": "2021001"})
	print("deleted:", deleted)

	conn.close()


if __name__ == "__main__":
	sys.exit(main())
