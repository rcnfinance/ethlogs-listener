import logging
import pika

from utils import handle_message

logger = logging.getLogger("worker")


class Worker():
    def __init__(self, rabbit_url, rabbit_queue):
        self.url_parameters = pika.connection.URLParameters(rabbit_url)
        self.connection = pika.BlockingConnection(self.url_parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(rabbit_queue)
        self.channel.basic_consume(self.__on_message, rabbit_queue)

    def __on_message(self, channel, method_frame, header_frame, body):
        logger.info('Message has been received {}'.format(body))
        valid = handle_message(int(body))
        logger.info("block {} is valid? {}".format(body, valid))
        if valid:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    def run(self):
        try:
            logger.info("Start consuming")
            self.channel.start_consuming()
        except Exception as ex:
            logger.error(ex, exc_info=True)
        finally:
            self.channel.stop_consuming()
            self.connection.close()
