from graceful.serializers import BaseSerializer
from graceful.fields import RawField, StringField


class LogEventSerializer(BaseSerializer):
    id = StringField("id")
    address = RawField("address")
    block_hash = RawField("block_hash")
    block_number = RawField("block_number")
    data = RawField("data")
    topic0 = RawField("topic0")
    topic1 = RawField("topic1")
    topic2 = RawField("topic2")
    topic3 = RawField("topic3")
    transaction_hash = RawField("transaction_hash")


class BlockSerializer(BaseSerializer):
    author = RawField("author")
    difficulty = RawField("difficulty")
    extra_data = RawField("extra_data")
    gas_limit = RawField("gas_limit")
    gas_used = RawField("gas_used")
    hash = RawField("hash")
    logs_bloom = RawField("logs_bloom")
    miner = RawField("miner")
    mix_hash = RawField("mix_hash")
    nonce = RawField("nonce")
    number = RawField("number")
    parent_hash = RawField("parent_hash")
    receipts_root = RawField("receipts_root")
    seal_fields = RawField("seal_fields")  # list
    sha3_uncles = RawField("sha3_uncles")
    size = RawField("size")
    state_root = RawField("state_root")
    timestamp = RawField("timestamp")
    total_difficulty = RawField("total_difficulty")
    transactions = RawField("transactions")  # list
    transactions_root = RawField("transactions_root")
    uncles = RawField("uncles")  # list
