args = {}

first = args.get("first", 10)
skip = args.get("skip", 0)
if "first" in args:
    del args["first"]
if "skip" in args:
    del args["skip"]
if "address" in args:
    address = args.get("address")
    logs = Log.objects.filter(address__in=address)
    del args["address"]
else:
    logs = Log.objects.all()

blocks = list(Block.objects.filter(**args).skip(skip).limit(first))
min_block, max_block = blocks[-1].number, blocks[0].number
blocks = {block.number: block for block in blocks}

logs = list(logs.filter(block_number__gte=min_block, block_number__lte=max_block))

logs_groupby_number = itertools.groupby(logs, key=itemgetter("block_number"))

for number, log_group in logs_groupby_number:
    blocks.get(number).logs = list(log_group)

return blocks
