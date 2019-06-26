import os
from mongoengine import StringField
from mongoengine import ListField
from mongoengine import IntField
from mongoengine import Document
from mongoengine import connect

DB_NAME = os.environ.get("MONGO_DB") or "events"
DB_HOST = os.environ.get("MONGO_HOST") or "mongo"
connection = connect(db=DB_NAME, host=DB_HOST)


class Log(Document):
    address = StringField(required=True)
    block_hash = StringField(required=True)
    block_number = IntField(required=True, primary=True)
    data = StringField(required=True)
    topic0 = StringField(required=False, null=True)
    topic1 = StringField(required=False, null=True)
    topic2 = StringField(required=False, null=True)
    topic3 = StringField(required=False, null=True)
    transaction_hash = StringField(required=True)

    meta = {
        "indexes": [
            "address",
            "block_number",
            "topic0",
            "topic1",
            "topic2",
            "topic3",
            "transaction_hash"
        ]
    }


class Block(Document):
    author = StringField(required=True)
    difficulty = IntField(required=True)
    extra_data = StringField(required=True)
    gas_limit = IntField(required=True)
    gas_used = IntField(required=True)
    hash = StringField(required=True)
    logs_bloom = StringField(required=True)
    miner = StringField(required=True)
    mix_hash = StringField(required=True)
    nonce = StringField(required=True)
    number = IntField(required=True, primary=True)
    parent_hash = StringField(required=True)
    receipts_root = StringField(required=True)
    seal_fields = ListField(StringField())
    sha3_uncles = StringField(required=True)
    size = IntField(required=True)
    state_root = StringField(required=True)
    timestamp = IntField(required=True)
    total_difficulty = IntField(required=True)
    transactions = ListField(StringField())
    transactions_root = StringField(required=True)
    uncles = ListField(StringField())

    meta = {
        "indexes": [
            "author",
            "hash",
            "miner",
            "nonce",
            "number",
            "parent_hash"
        ]
    }
