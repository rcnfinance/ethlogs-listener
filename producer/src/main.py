import os
import logging
from block_listener import BlockListener

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("main")


USER = os.environ.get("RABBIT_USER", "guest")
PASSWORD = os.environ.get("RABBIT_PASSWORD", "guest")
SERVER = os.environ.get("RABBIT_SERVER", "rabbitmq")
PORT = os.environ.get("RABBIT_PORT", 5672)
VHOST = os.environ.get("RABBIT_VHOST", "/")
QUEUE_NAME = os.environ.get("RABBIT_QUEUE_NAME", "pc")
QUEUE_MAX_ITEMS = int(os.environ.get("QUEUE_MAX_ITEMS", 100))

CONTRACTS = os.environ.get("CONTRACTS")
if CONTRACTS:
    CONTRACTS = CONTRACTS.split(",")

RABBIT_URL = "amqp://{user}:{password}@{server}:{port}/{vhost}".format(
    user=USER,
    password=PASSWORD,
    server=SERVER,
    port=PORT,
    vhost="%2F" if VHOST == "/" else VHOST
)

logger.debug("RABBIT_URL: {}".format(RABBIT_URL))

listener = BlockListener(
    RABBIT_URL,
    QUEUE_NAME,
    QUEUE_MAX_ITEMS
)

listener.run()
