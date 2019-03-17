import logging
import pika
from models import Block
from models import Log

from utils import get_block_header
from utils import get_logs
from utils import EMPTY_BLOOM
from bloom import build_bloom_filter
from bloom import verify_bloom

logger = logging.getLogger("worker")


class Worker():
    def __init__(self, rabbit_url, rabbit_queue):
        logger.info("Starting worker")
        self.queue_name = rabbit_queue
        self.url_parameters = pika.connection.URLParameters(rabbit_url)
        self.connection = pika.BlockingConnection(self.url_parameters)
        self.channel = self.connection.channel()

        self.channel.basic_consume(self.__on_message, self.queue_name)

    def send_block_to_queue(self, block_number):
        channel = self.connection.channel()
        q = channel.queue_declare(self.queue_name, arguments={"x-max-priority": 10})
        q_name = q.method.queue

        # Turn on delivery confirmations
        channel.confirm_delivery()

        published = False

        while not published:
            published = channel.basic_publish(
                "",
                q_name,
                str(block_number),
                properties=pika.BasicProperties(priority=10)
            )

        return published

    def handle_message(self, block_number):
        block = get_block_header(block_number)
        logger.debug("[*] block: {}, hash:[{}], parent_hash:[{}]".format(block.number, block.hash.hex(), block.parentHash.hex()))

        try:
            ok_ant = True
            ant = Block.objects.get(number=str(block_number - 1))
            ant_exist = True
            ok_ant = self.is_prev(ant, block)

            logger.debug("[*] ant: {}, hash:[{}], parent_hash:[{}]".format(ant.number, ant.hash, ant.parent_hash))
            logger.debug("ok_ant: {}".format(ok_ant))
        except Block.DoesNotExist:
            ant_exist = False

        try:
            ok_pos = True
            pos = Block.objects.get(number=str(block_number + 1))
            pos_exist = True
            ok_pos = self.is_prev(block, pos)
            logger.debug("[*] pos: {}, hash:[{}], parent_hash:[{}]".format(pos.number, pos.hash, pos.parent_hash))
            logger.debug("ok_pos: {}".format(ok_pos))
        except Block.DoesNotExist:
            pos_exist = False

        if ant_exist and not ok_ant:
            logger.debug("sending to queue: {}".format(ant.number))
            sent = self.send_block_to_queue(ant.number)
            logger.debug("sent?: {}".format(sent))
        if pos_exist and not ok_pos:
            logger.debug("sending to queue: {}".format(pos.number))
            sent = self.send_block_to_queue(pos.number)
            logger.debug("sent?: {}".format(sent))

        if ok_ant and ok_pos:
            self.save_block(block)
            block_bloom = block.get("logsBloom").hex()

            if block_bloom != EMPTY_BLOOM:
                logs = get_logs(block_number)

                generated_bloom = build_bloom_filter(logs)
                valid_bloom = verify_bloom(block_bloom, generated_bloom)
                if valid_bloom:
                    self.save_events(block_number, logs)
                    return True
                else:
                    return False

            return True
        return False

    def save_block(self, block_data):
        try:
            block = Block.objects.get(number=block_data.number)
        except Block.DoesNotExist:
            block = Block()

        block.author = block_data.author
        block.difficulty = block_data.difficulty
        block.extra_data = block_data.extraData.hex()
        block.gas_limit = block_data.gasLimit
        block.gas_used = block_data.gasUsed
        block.hash = block_data.hash.hex()
        block.logs_bloom = block_data.logsBloom.hex()
        block.miner = block_data.miner
        block.mix_hash = block_data.mixHash.hex()
        block.nonce = block_data.nonce.hex()
        block.number = block_data.number
        block.parent_hash = block_data.parentHash.hex()
        block.receipts_root = block_data.receiptsRoot.hex()
        # block.seal_fields = [seal_field for seal_field in block_data.sealFields]
        block.sha3_uncles = block_data.sha3Uncles.hex()
        block.size = block_data.size
        block.state_root = block_data.stateRoot.hex()
        block.timestamp = block_data.timestamp
        block.total_difficulty = block_data.totalDifficulty
        block.transactions = [tx.hex() for tx in block_data.transactions]
        block.transactions_root = block_data.transactionsRoot.hex()
        block.uncles = [uncle.hex() for uncle in block_data.uncles]

        block.save()

    def remove_prev_logs(self, block_number):
        prev_logs = Log.objects.filter(block_number=block_number)
        deleted_logs = prev_logs.delete()

        return deleted_logs

    def save_events(self, block_number, logs):
        # remove logs with block_number = current_block.number
        self.remove_prev_logs(block_number)
        for log in logs:
            log_event = Log()
            log_event.address = log.get("address")
            log_event.block_hash = log.get("blockHash").hex()
            log_event.block_number = log.get("blockNumber")
            log_event.data = log.get("data")
            topics = [topic.hex() for topic in log.get("topics")]
            try:
                log_event.topic0 = topics[0]
                log_event.topic1 = topics[1]
                log_event.topic2 = topics[2]
                log_event.topic3 = topics[3]
            except IndexError:
                pass
            log_event.transaction_hash = log.get("transactionHash").hex()

            log_event.save()

    def is_prev(self, b1, b2):
        if isinstance(b2, Block):
            return b1.hash.hex() == b2.parent_hash
        if isinstance(b1, Block):
            return b1.hash == b2.parentHash.hex()

    def __on_message(self, channel, method_frame, header_frame, body):
        logger.info('Message has been received {}'.format(body))
        valid = self.handle_message(int(body))
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
