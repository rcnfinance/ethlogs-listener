import falcon

from resources import LogEventItem
from resources import LogEventList
from resources import StatusResource
from resources import BlockList
from resources import BlockItem

from falcon_cors import CORS

cors = CORS(allow_all_origins=True)

api = application = falcon.API(middleware=[cors.middleware])


api.add_route("/v1/log_event/", LogEventList())
api.add_route("/v1/log_event/{id_log_event}", LogEventItem())

api.add_route("/v1/blocks/", BlockList())
api.add_route("/v1/blocks/{block_id}/", BlockItem())


api.add_route("/status", StatusResource())
