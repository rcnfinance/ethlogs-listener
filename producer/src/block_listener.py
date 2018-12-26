import logging
import time
import pika
from utils import get_last_block_number

logger = logging.getLogger("block_listener")
SLEEP_SEC = 2


class BlockListener():
    def __init__(self, rabbit_url, rabbit_queue_name, rabbit_queue_max_items):
        self.rabbit_queue_name = rabbit_queue_name
        self.rabbit_queue_max_items = rabbit_queue_max_items
        self.magic_number = (self.rabbit_queue_max_items * 10) / 100

        self.url_parameters = pika.connection.URLParameters(rabbit_url)

        self.connection = pika.BlockingConnection(self.url_parameters)

        self.channel = self.connection.channel()
        self.q = self.channel.queue_declare(self.rabbit_queue_name)
        self.q_name = self.q.method.queue

        # Turn on delivery confirmations
        self.channel.confirm_delivery()

    def publish_block(self, block_number):
        published = self.channel.basic_publish("", self.q_name, str(block_number))

        if published:
            logger.info("Message has been delivered: {}".format(block_number))
        else:
            logger.info("Message not delivered: {}".format(block_number))

        return published

    def run(self):
        last_block_enqueued = 0
        try:
            while True:
                last_block_mined = get_last_block_number()

                logger.info("last_block.number: {}".format(last_block_mined))
                logger.info("last_block_enqueued: {}".format(last_block_enqueued))

                if last_block_mined != last_block_enqueued:
                    upper_block_number = min(
                        last_block_enqueued + 1 + self.rabbit_queue_max_items,
                        last_block_mined
                    )
                    blocks_to_enqueue = list(
                        range(last_block_enqueued + 1, upper_block_number + 1)
                    )

                    for block in blocks_to_enqueue:
                        self.publish_block(str(block))

                    last_block_enqueued = blocks_to_enqueue[-1]
                else:
                    logger.info("Sleeping for {} sec".format(SLEEP_SEC))
                    time.sleep(SLEEP_SEC)
        except Exception as e:
            logger.error(e, exc_info=True)
            self.connection.close()
