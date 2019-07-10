from itertools import tee
from itertools import takewhile
import requests
import time
from string import Template


def query_builder(filter_params=None):
    query_template = Template("""{
      blockLogs $filter_params {
        number
        hash
        parentHash
        logs {
          address
          blockHash
          blockNumber
          data
          topic0
          topic1
          topic2
          topic3
          transactionHash
        }
      }
    }
    """
    )

    if filter_params is None:
        filter_params = "(first:32)"

    return query_template.substitute(filter_params=filter_params)


def get_last_nth_blocks(number):
    params = "(first:{})".format(number)

    query = query_builder(params)
    blocks = run_graphql_query(query)

    return blocks


def get_range_blocks(from_block_number, to_block_number):
    params = "(block_number__gte:{}, block_number__lte:{})".format(
        from_block_number,
        to_block_number
    )

    query = query_builder(params)
    blocks = run_graphql_query(query)

    return blocks


def run_graphql_query(query):
    url = "http://localhost:8001/"
    return requests.get(url, params=query)


def get_blocks_logs():
    url = "http://localhost:8001/"
    graphql_query = """{
      blockLogs (first:32) {
        number
        hash
        parentHash
        logs {
          address
          blockHash
          blockNumber
          data
          topic0
          topic1
          topic2
          topic3
          transactionHash
        }
      }
    }"""
    querystring = {"query": graphql_query}

    response = requests.get(url, params=querystring).json().get("data").get("blockLogs")

    return response

def get_blocks_logs_from(block_number):
    graphql_query = """{
      blockLogs (number__gte: "", first:32) {
        number
        hash
        parentHash
        logs {
          address
          blockHash
          blockNumber
          data
          topic0
          topic1
          topic2
          topic3
          transactionHash
        }
      }
    }
    """


def pairwise(iterable):
    a, b = tee(iterable)
    next(a, None)
    return list(zip(a, b))


def is_prev(b1, b2):
    return b1["hash"] == b2["parentHash"]


def validate_chain(chain):
    return all(map(lambda pair: is_prev(pair[0], pair[1]), pairwise(chain)))


def same_block(block1, block2):
    return block1.get("number") == block2.get("number")


def same_hash(block1, block2):
    return block1.get("hash") == block2.get("hash")


def have_new_blocks(old_chain, new_chain):
    last_block = old_chain[0]
    return list(takewhile(lambda new_block: same_block(last_block, new_block), new_chain))


def restore_to_block(block):
    # commits = Commits.objects.filter(block__gte=block.get("number"))
    print("restore_to_block({})".format(old_chain[j]))



def new_blocks_to_process(old_chain, new_chain):
    i, j = 0, 0
    while True:
        if same_block(new_chain[i], old_chain[j]):
            if not same_hash(new_chain[i], old_chain[j]):
                restore_to_block(old_chain[j])
            else:
                break
            i += 1
            j += 1
        elif new_chain[i].get("number") > old_chain[j].get("number"):
            i += 1
    return new_chain[:i]

# CASE SAME CHAINS, NO NEW BLOCKS
old_chain1 = [
    {"number": 3, "hash": "0x3"},
    {"number": 2, "hash": "0x2"},
    {"number": 1, "hash": "0x1"},
]

new_chain1 = [
    {"number": 3, "hash": "0x3"},
    {"number": 2, "hash": "0x2"},
    {"number": 1, "hash": "0x1"},
]
# CASE NEW BLOCKS
old_chain2 = [
    {"number": 3, "hash": "0x3"},
    {"number": 2, "hash": "0x2"},
    {"number": 1, "hash": "0x1"},
]

new_chain2 = [
    {"number": 4, "hash": "0x4"},
    {"number": 3, "hash": "0x3"},
    {"number": 2, "hash": "0x2"},
]
# CASE NEW_BLOCK AND FORK
old_chain3 = [
    {"number": 3, "hash": "0x3"},
    {"number": 2, "hash": "0x2"},
    {"number": 1, "hash": "0x1"},
]

new_chain3 = [
    {"number": 4, "hash": "0x4"},
    {"number": 3, "hash": "0x33"},
    {"number": 2, "hash": "0x2"},
]


def main():
    old_blocks_logs = get_blocks_logs()
    time.sleep(10)
    while True:

        new_blocks_logs = get_blocks_logs()

        print("old_blocks: last_block: {}, first_block: {}".format(
            old_blocks_logs[0].get("number"),
            old_blocks_logs[-1].get("number")
        ))

        print("new_blocks: last_block: {}, first_block: {}".format(
            new_blocks_logs[0].get("number"),
            new_blocks_logs[-1].get("number")
        ))

        print("Validate new_blocks", validate_chain(new_blocks_logs))

        new_blocks = new_blocks_to_process(old_blocks_logs, new_blocks_logs)

        for block in new_blocks:  # new_blocks reverse
            print("Process block_number:{} with hash:{}".format(block.get("number"), block.get("hash")))

        old_blocks_logs = new_blocks_logs
        print("sleep 10 sec")
        time.sleep(10)