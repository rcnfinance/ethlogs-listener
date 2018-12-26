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
