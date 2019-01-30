import os
import web3
import logging
from bloom import build_bloom_filter
from bloom import verify_bloom
from models import Log
from models import Block


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


def save_block(block_data):
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


def handle_message(block_number):
    EMPTY_BLOOM = "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    block = get_block(block_number)
    save_block(block)
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
