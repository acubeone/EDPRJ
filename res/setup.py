import json
import os

from dotenv import load_dotenv
from pymongo.database import Database
import pymongo as mg
from pymongo.errors import CollectionInvalid

load_dotenv()

DEFAULT_TIMEOUT = 5000  # 5 seconds

SCHEMA_DIR: str = os.path.join(os.path.dirname(__file__), "schemas")

UNIQUE_INDEXES = {
	"usuario": [
		("cpf", {"unique": True}),
		("login", {"unique": True, "sparse": True}),
	],
	"curso": [
		("idcurso", {"unique": True, "sparse": True}),
	],
	"estudante": [
		("mat_estudante", {"unique": True}),
		("cpf", {"unique": True, "sparse": True}),
	],
	"vinculo": [
		("idvinculo", {"unique": True, "sparse": True}),
	],
}


def _get_mongo_db() -> Database:
	uri = (
		f"mongodb://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
		f"@{os.environ['MONGO_HOST']}:{os.environ['MONGO_PORT']}/"
		f"{os.environ['DB_NAME']}?authSource=admin"
	)
	client = mg.MongoClient(uri, serverSelectionTimeoutMS=DEFAULT_TIMEOUT)
	client.admin.command("ping")
	return client[os.environ["DB_NAME"]]


def _load_schema(entity_name: str) -> dict:
	path = os.path.join(SCHEMA_DIR, f"{entity_name}.json")
	with open(path) as f:
		return json.load(f)


def _setup_collections(database: Database) -> None:
	for filename in sorted(os.listdir(SCHEMA_DIR)):
		if not filename.endswith(".json"):
			continue
		entity_name = filename.removesuffix(".json")
		schema = _load_schema(entity_name)

		try:
			database.create_collection(entity_name, validator=schema)
			print(f"Created collection: {entity_name}")
		except CollectionInvalid:
			database.command("collMod", entity_name, validator=schema)
			print(f"Updated validator: {entity_name}")


def _setup_indexes(database: Database) -> None:
	for entity_name, indexes in UNIQUE_INDEXES.items():
		for spec, options in indexes:
			if isinstance(spec, str):
				spec = [(spec, 1)]
			database[entity_name].create_index(spec, **options)  # pyright: ignore[reportArgumentType]
			print(f"Index ensured on {entity_name}: {spec} {options}")


def main() -> None:
	try:
		database = _get_mongo_db()
	except Exception as e:
		print(f"Could not connect to MongoDB: {e}")
		return

	_setup_collections(database)
	_setup_indexes(database)
	print("MongoDB setup complete!")


if __name__ == "__main__":
	main()
