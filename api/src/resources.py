import logging
import json
from graceful.resources.generic import RetrieveAPI
from graceful.resources.generic import PaginatedListAPI
from graceful.parameters import StringParam
import falcon
from serializers import LogEventSerializer
from models import LogEvent
from utils import get_last_block_number


logger = logging.getLogger(__name__)


class LogEventList(PaginatedListAPI):
    serializer = LogEventSerializer()

    address = StringParam("address filter")
    block_hash = StringParam("block_hash filter")
    block_number = StringParam(" filter")
    data = StringParam("address filter")
    topic0 = StringParam("topic0 filter")
    topic1 = StringParam("topic1 filter")
    topic2 = StringParam("topic2 filter")
    topic3 = StringParam("topic3 filter")
    transaction_hash = StringParam("transaction_hash filter")

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        return LogEvent.objects.filter(**filter_params).skip(offset).limit(page_size)


class LogEventItem(RetrieveAPI):
    serializer = LogEventSerializer()

    def retrieve(self, params, meta, id_log_event):
        try:
            return LogEvent.objects.get(id=id_log_event)
        except LogEvent.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Log Event does not exists',
                description='Log Event with id={} does not exists'.format(id_log_event)
            )


class StatusResource(object):
    def on_get(self, req, resp):
        last_block_mined = get_last_block_number()
        last_block_processed = LogEvent.objects.order_by("-block_number").limit(1).first().block_number

        is_sync = (last_block_mined - last_block_processed) < 5
        data = {
            "last_block_mined": last_block_mined,
            "last_block_processed": last_block_processed
        }
        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_503

        if is_sync:
            resp.status = falcon.HTTP_200
