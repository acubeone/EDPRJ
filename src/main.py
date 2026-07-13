import dataclasses
import json
import shlex
import sys
import argparse

import psycopg
from psycopg.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

from backend import Backend
import db

ENTITY_REGISTRY = {
	"usuario": db.Usuario,
	"curso": db.Curso,
	"estudante": db.Estudante,
	"vinculo": db.Vinculo,
}

backend_kind: str = ""


def _parse_arguments() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Ferramenta CRUD")
	parser.add_argument("--backend", choices=["postgres", "mongo"], required=True)

	return parser.parse_args()


def _build_command_parser() -> argparse.ArgumentParser:
	# fmt: off
	parser = argparse.ArgumentParser(prog="", add_help=False)
	parser.add_argument("entity")

	sub = parser.add_subparsers(dest="action", required=True)
	sub.add_parser("exit")
	sub.add_parser("help")

	p_create = sub.add_parser("create")
	p_create.add_argument("-d", "--data", required=True)

	p_get = sub.add_parser("get")
	p_get.add_argument("-k", "--key", required=True)

	p_update = sub.add_parser("update")
	p_update.add_argument("-k", "--key", required=True)
	p_update.add_argument("-f", "--fields", required=True)

	p_delete = sub.add_parser("delete")
	p_delete.add_argument("-k", "--key", required=True)

	p_list = sub.add_parser("list")
	p_list.add_argument("--filters", default="{}")
	# fmt: on

	return parser


def _dispatch_action(
	repo: db.AbstractRepository, cmd: argparse.Namespace, entity_name: str
):
	if cmd.action == "create":
		data = json.loads(cmd.data)
		data = db.parse_dates(data, ENTITY_REGISTRY[entity_name], backend_kind)
		entity = ENTITY_REGISTRY[entity_name](**data)
		return repo.create(entity)
	elif cmd.action == "get":
		key = json.loads(cmd.key)
		return repo.get(key)
	elif cmd.action == "update":
		key = json.loads(cmd.key)
		fields = json.loads(cmd.fields)
		return repo.update(key, fields)
	elif cmd.action == "delete":
		key = json.loads(cmd.key)
		return repo.delete(key)
	elif cmd.action == "list":
		filters = json.loads(cmd.filters)
		return repo.list(filters or {})


def _print_help(current_entity: str | None = None) -> None:
	if current_entity:
		entity_cls = ENTITY_REGISTRY[current_entity]
		fields = [f.name for f in dataclasses.fields(entity_cls)]
		print(f"""
Entity: {current_entity}
Fields: {", ".join(fields)}

Actions:
  {current_entity} create --data '{{"field": "value", ...}}'
  {current_entity} get    --key '{{"field": "value"}}'
  {current_entity} update --key '{{"field": "value"}}' --fields '{{"field": "new_value"}}'
  {current_entity} delete --key '{{"field": "value"}}'
  {current_entity} list
""")
		return

	entities = sorted(ENTITY_REGISTRY)
	print(f"""
Universidade CRUD tool

Available entities ({len(entities)}):
  {", ".join(entities)}

Actions (apply to any entity above):
  <entity> create --data '{{"field": "value", ...}}'
  <entity> get    --key '{{"field": "value"}}'
  <entity> update --key '{{"field": "value"}}' --data '{{"field": "new_value"}}'
  <entity> delete --key '{{"field": "value"}}'
  <entity> list

Examples:
  estudante create --data '{{"mat_estudante": "2021001", "ano_ingresso": 2021}}'
  estudante get --key '{{"mat_estudante": "2021001"}}'
  estudante list

Other commands:
  help              show this message
  help <entity>     show fields and examples for one entity
  exit              quit the program
""")


def _command_line(backend: Backend, args: argparse.Namespace) -> None:
	cmd_parser = _build_command_parser()

	print(f"Connected to {args.backend}. Type commands, or 'exit' to quit.")
	while True:
		try:
			line = input(f"[{args.backend}]> ").strip()
		except (EOFError, KeyboardInterrupt):
			break

		if not line:
			continue  # Skip empty lines or commands
		if line == "help" or line.startswith("help "):
			parts = line.split(maxsplit=1)
			entity_arg = parts[1] if len(parts) > 1 else None
			if entity_arg and entity_arg not in ENTITY_REGISTRY:
				print(f"Unknown entity: {entity_arg}")
			else:
				_print_help(entity_arg)
			continue
		elif line == "exit":
			break

		try:
			parsed = cmd_parser.parse_args(shlex.split(line))
		except SystemExit:
			continue  # argparse already handles it, so just skip

		repo = backend.get_repository(parsed.entity)
		try:
			entity_name = args.entity if hasattr(args, "entity") else parsed.entity
			result = _dispatch_action(repo, parsed, entity_name)
			print(result)
		except Exception as e:
			print(f"ERROR: {e}")


def main() -> int | None:
	args = _parse_arguments()

	backend_kind = args.backend
	backend = Backend(args.backend)
	try:
		print(f"Attempting connection to {args.backend}...")
		backend.connect()
		print("\r")
	except psycopg.OperationalError:
		print(
			"Could not reach Postgres - check host/port/credentials and server status"
		)
		sys.exit(1)
	except (ConnectionFailure, ServerSelectionTimeoutError):
		print("Could not reach MongoDB - check host/port/credentials and server status")
		sys.exit(1)
	except KeyError as e:
		print(f"Missing environment variable: {e}. Check your .env file")
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error connecting to {args.backend}: {e}")
		sys.exit(1)

	_command_line(backend, args)
	backend.close()


if __name__ == "__main__":
	sys.exit(main())
