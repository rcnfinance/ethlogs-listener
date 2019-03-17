import os
import requests
import web3


url_node = os.environ.get("URL_NODE", "https://ropsten.node.rcn.loans:8545/")
node_provider = web3.HTTPProvider(url_node)
w3 = web3.Web3(node_provider)
ENDPOINT_STATUS_LISTENER = "http://api:8000/status/"


def get_last_block_number():
    block_number = w3.eth.blockNumber
    return block_number


def get_last_block_processed():
    response = requests.get(ENDPOINT_STATUS_LISTENER)

    if response.content:
        last_block_processed = int(response.json().get("last_block_processed"))
    else:
        last_block_processed = 0

    return last_block_processed
