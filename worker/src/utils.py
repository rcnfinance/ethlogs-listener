import os
import web3
import logging
from bloom import build_bloom_filter
from bloom import verify_bloom
from models import LogEvent


logger = logging.getLogger("worker.utils")

url_node = os.environ.get("URL_NODE", "https://ropsten.node.rcn.loans:8545/")
node_provider = web3.HTTPProvider(url_node)
w3 = web3.Web3(node_provider)


def get_block(block_number):
    block = w3.eth.getBlock(block_number)

    return block


def get_logs(block_number):
    block_logs = get_block_logs(block_number)

    return block_logs


def get_block_logs(block_number):
    data = {
        "fromBlock": block_number,
        "toBlock": block_number
    }

    logs = w3.eth.getLogs(data)

    return logs


def save_events(logs):
    for log in logs:
        log_event = LogEvent()
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


def handle_message(block_number):
    EMPTY_BLOOM = "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    block = get_block(block_number)
    block_bloom = block.get("logsBloom").hex()

    if block_bloom != EMPTY_BLOOM:
        logs = get_logs(block_number)

        generated_bloom = build_bloom_filter(logs)
        valid_bloom = verify_bloom(block_bloom, generated_bloom)
        if valid_bloom:
            save_events(logs)
            return True
        else:
            return False

    return True
