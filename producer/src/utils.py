import os
import web3


url_node = os.environ.get("URL_NODE", "https://ropsten.node.rcn.loans:8545/")
node_provider = web3.HTTPProvider(url_node)
w3 = web3.Web3(node_provider)


def get_last_block_number():
    block_number = w3.eth.blockNumber
    return block_number
