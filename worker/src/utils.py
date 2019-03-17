import os
import web3
import logging


logger = logging.getLogger("worker.utils")

url_node = os.environ.get("URL_NODE", "https://ropsten.node.rcn.loans:8545/")
node_provider = web3.HTTPProvider(url_node)
w3 = web3.Web3(node_provider)


EMPTY_BLOOM = "0x".ljust(514, "0")


def get_block_header(block_number):
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
