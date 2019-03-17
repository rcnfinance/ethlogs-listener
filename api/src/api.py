import falcon

from resources import LogItem
from resources import LogList
from resources import StatusResource
from resources import BlockList
from resources import BlockItem

from falcon_cors import CORS

cors = CORS(allow_all_origins=True)

api = application = falcon.API(middleware=[cors.middleware])


api.add_route("/v1/logs/", LogList())
api.add_route("/v1/logs/{log_id}", LogItem())

api.add_route("/v1/blocks/", BlockList())
api.add_route("/v1/blocks/{block_id}/", BlockItem())


api.add_route("/status", StatusResource())
