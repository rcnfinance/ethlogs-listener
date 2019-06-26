from mongoengine import connect

DB_NAME = os.environ.get("MONGO_DB") or "events"
DB_HOST = os.environ.get("MONGO_HOST") or "mongo"
connection = connect(db=DB_NAME, host=DB_HOST)
