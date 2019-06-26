import logging
import json
from graceful.resources.generic import RetrieveAPI
from graceful.resources.generic import PaginatedListAPI
from graceful.parameters import StringParam
import falcon
from serializers import LogSerializer
from serializers import BlockSerializer
from models import Log
from models import Block
from utils import get_last_block_number


logger = logging.getLogger(__name__)


class LogList(PaginatedListAPI):
    serializer = LogSerializer()

    address = StringParam("address filter")
    block_hash = StringParam("block_hash filter")
    block_number = StringParam("block_number filter")
    data = StringParam("data filter")
    topic0 = StringParam("topic0 filter")
    topic1 = StringParam("topic1 filter")
    topic2 = StringParam("topic2 filter")
    topic3 = StringParam("topic3 filter")
    transaction_hash = StringParam("transaction_hash filter")

    block_number__lt = StringParam("block_number lt")
    block_number__lte = StringParam("block_number lte")
    block_number__gt = StringParam("block_number gt")
    block_number__gte = StringParam("block_number gte")

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        return Log.objects.filter(**filter_params).skip(offset).limit(page_size)


class BlockList(PaginatedListAPI):
    serializer = BlockSerializer()

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        return Block.objects.filter(**filter_params).skip(offset).limit(page_size)


class BlockItem(RetrieveAPI):
    serializer = BlockSerializer()

    def retrieve(self, params, meta, block_id):
        try:
            return Block.objects.get(number=block_id)
        except Block.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Block does not exists',
                description='Block with id={} does not exists'.format(block_id)
            )


class LogItem(RetrieveAPI):
    serializer = LogSerializer()

    def retrieve(self, params, meta, log_id):
        try:
            return Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Log Event does not exists',
                description='Log Event with id={} does not exists'.format(log_id)
            )


class StatusResource(object):
    def on_get(self, req, resp):
        last_block_mined = get_last_block_number()
        last_block_processed = Block.objects.order_by("-number").limit(1).first()
        if last_block_processed:
            last_block_processed = last_block_processed.number

            is_sync = (last_block_mined - last_block_processed) < 5
            data = {
                "last_block_mined": last_block_mined,
                "last_block_processed": last_block_processed
            }
            resp.body = json.dumps(data)
            resp.status = falcon.HTTP_503

            if is_sync:
                resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_503
