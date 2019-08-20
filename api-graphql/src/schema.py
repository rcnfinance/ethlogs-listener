from operator import itemgetter
import itertools
from copy import deepcopy
import graphene

from models import Log as LogModel
from models import Block as BlockModel

import logging


class Log(graphene.ObjectType):
    address = graphene.String()
    block_hash = graphene.String()
    block_number = graphene.String()
    data = graphene.String()
    topic0 = graphene.String()
    topic1 = graphene.String()
    topic2 = graphene.String()
    topic3 = graphene.String()
    transaction_hash = graphene.String()


def resolve(block, info, **args):
    logs = LogModel.objects.filter(**args).filter(block_number=block.number)
    logging.info(type(block))
    logging.info(block)
    logging.info(type(info))
    logging.info(info)
    logging.info(type(args))
    logging.info(args)
    return logs


class Block(graphene.ObjectType):
    author = graphene.String()
    difficulty = graphene.String()
    extra_data = graphene.String()
    gas_limit = graphene.String()
    gas_used = graphene.String()
    hash = graphene.String()
    logs_bloom = graphene.String()
    miner = graphene.String()
    mix_hash = graphene.String()
    nonce = graphene.String()
    number = graphene.String()
    parent_hash = graphene.String()
    receipts_root = graphene.String()
    seal_fields = graphene.List(graphene.String)
    sha3_uncles = graphene.String()
    size = graphene.String()
    state_root = graphene.String()
    timestamp = graphene.String()
    total_difficulty = graphene.String()
    transactions = graphene.List(graphene.String)
    transactions_root = graphene.String()
    uncles = graphene.List(graphene.String)
    logs = graphene.List(Log, resolver=resolve)


class BlockLogs(graphene.ObjectType):
    author = graphene.String()
    difficulty = graphene.String()
    extra_data = graphene.String()
    gas_limit = graphene.String()
    gas_used = graphene.String()
    hash = graphene.String()
    logs_bloom = graphene.String()
    miner = graphene.String()
    mix_hash = graphene.String()
    nonce = graphene.String()
    number = graphene.String()
    parent_hash = graphene.String()
    receipts_root = graphene.String()
    seal_fields = graphene.List(graphene.String)
    sha3_uncles = graphene.String()
    size = graphene.String()
    state_root = graphene.String()
    timestamp = graphene.String()
    total_difficulty = graphene.String()
    transactions = graphene.List(graphene.String)
    transactions_root = graphene.String()
    uncles = graphene.List(graphene.String)
    logs = graphene.List(Log)


class Query(graphene.ObjectType):
    block_logs = graphene.List(
        BlockLogs,
        author=graphene.String(required=False),
        hash=graphene.String(required=False),
        number=graphene.String(required=False),
        parent_hash=graphene.String(required=False),
        address=graphene.List(graphene.String, required=False),

        number__gt=graphene.String(required=False, name="number__gt"),
        number__gte=graphene.String(required=False, name="number__gte"),
        number__lt=graphene.String(required=False, name="number__lt"),
        number__lte=graphene.String(required=False, name="number__lte"),

        first=graphene.Int(required=False),
        skip=graphene.Int(required=False)
    )

    logs = graphene.List(Log,
        address=graphene.String(required=False),
        block_hash=graphene.String(required=False),
        block_number=graphene.String(required=False),
        topic0=graphene.String(required=False),
        topic1=graphene.String(required=False),
        topic2=graphene.String(required=False),
        topic3=graphene.String(required=False),
        transaction_hash=graphene.String(required=False),

        block_number__gt=graphene.String(required=False, name="block_number__gt"),
        block_number__gte=graphene.String(required=False, name="block_number__gte"),
        block_number__lt=graphene.String(required=False, name="block_number__lt"),
        block_number__lte=graphene.String(required=False, name="block_number__lte"),

        first=graphene.Int(required=False),
        skip=graphene.Int(required=False)
    )

    blocks = graphene.List(Block,
        author=graphene.String(required=False),
        hash=graphene.String(required=False),
        number=graphene.String(required=False),
        parent_hash=graphene.String(required=False),

        number__gt=graphene.String(required=False, name="number__gt"),
        number__gte=graphene.String(required=False, name="number__gte"),
        number__lt=graphene.String(required=False, name="number__lt"),
        number__lte=graphene.String(required=False, name="number__lte"),

        first=graphene.Int(required=False),
        skip=graphene.Int(required=False)
    )

    def resolve_logs(root, info, **args):
        first = args.get("first", 10)
        skip = args.get("skip", 0)
        if "first" in args:
            del args["first"]
        if "skip" in args:
            del args["skip"]
        return LogModel.objects.filter(**args).skip(skip).limit(first)

    def resolve_blocks(root, info, **args):
        logging.info(root)
        logging.info(info)
        logging.info(args)
        first = args.get("first", 10)
        skip = args.get("skip", 0)
        if "first" in args:
            del args["first"]
        if "skip" in args:
            del args["skip"]
        return BlockModel.objects.filter(**args).skip(skip).limit(first)

    def resolve_block_logs(root, info, **args):
        logging.info("asd")
        params = deepcopy(args)
        # first = args.get("first", 10)
        # skip = args.get("skip", 0)
        if "first" in args:
            del args["first"]
        if "skip" in args:
            del args["skip"]
        if "address" in args:
            address = args.get("address")
            logs = LogModel.objects.filter(address__in=address)
            del args["address"]
        else:
            logs = LogModel.objects.all()

        # TODO: basofia
        blocks = BlockModel.objects.filter(**args)
        if "skip" in params:
            blocks = blocks.skip(params.get("skip"))
        if "first" in params:
            blocks = blocks.limit(params.get("first"))
        blocks = list(blocks)

        if blocks:
            min_block, max_block = blocks[-1].number, blocks[0].number
            blocks = {block.number: block for block in blocks}

            logs = list(logs.filter(block_number__gte=min_block, block_number__lte=max_block))

            logs_groupby_number = itertools.groupby(logs, key=itemgetter("block_number"))

            for number, log_group in logs_groupby_number:
                blocks.get(number).logs = list(log_group)

            a = [block for number, block in blocks.items()]
            return a
        else:
            return []

schema = graphene.Schema(query=Query)
