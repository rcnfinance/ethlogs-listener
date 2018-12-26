from eth_utils import encode_hex as encode_hex_0x
from eth_utils import decode_hex
from eth_utils import int_to_big_endian
from eth_utils import big_endian_to_int

BUCKETS_PER_VAL = 3


def is_numeric(x):
    return isinstance(x, int)


def bloom(val):
    return bloom_insert(0, val)


def encode_hex(n):
    if isinstance(n, str):
        return encode_hex(n.encode('ascii'))
    return encode_hex_0x(n)[2:]


def to_string(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def safe_ord(value):
    if isinstance(value, int):
        return value
    else:
        return ord(value)


def zpad(x, l):
    """ Left zero pad value `x` at least to length `l`.

    >>> zpad('', 1)
    '\x00'
    >>> zpad('\xca\xfe', 4)
    '\x00\x00\xca\xfe'
    >>> zpad('\xff', 1)
    '\xff'
    >>> zpad('\xca\xfe', 2)
    '\xca\xfe'
    """
    return b'\x00' * max(0, l - len(x)) + x


def sha3(seed):
    return sha3_256(to_string(seed))


try:
    from Crypto.Hash import keccak

    def sha3_256(x):
        return keccak.new(digest_bits=256, data=x).digest()
except ImportError:
    import sha3 as _sha3

    def sha3_256(x):
        return _sha3.keccak_256(x).digest()


def bloom_insert(bloom, val):
    h = sha3(val)
#   print('bloom_insert', bloom_bits(val), repr(val))
    for i in range(0, BUCKETS_PER_VAL * 2, 2):
        bloom |= 1 << ((safe_ord(h[i + 1]) + (safe_ord(h[i]) << 8)) & 2047)
    return bloom


def bloom_bits(val):
    h = sha3(val)
    return [bits_in_number(1 << ((safe_ord(h[i + 1]) + (safe_ord(h[i]) << 8)) & 2047))
            for i in range(0, BUCKETS_PER_VAL * 2, 2)]


def bits_in_number(val):
    assert is_numeric(val)
    return [n for n in range(2048) if (1 << n) & val]


def bloom_query(bloom, val):
    bloom2 = bloom_insert(0, val)
    return (bloom & bloom2) == bloom2


def bloom_combine(*args):
    bloom = 0
    for arg in args:
        bloom |= arg
    return bloom


def bloom_from_list(args):
    return bloom_combine(*[bloom_insert(0, arg) for arg in args])


def b64(int_bloom):
    "returns b256"
    return zpad(int_to_big_endian(int_bloom), 256)


def encode_hex_from_int(x):
    return encode_hex(zpad(int_to_big_endian(x), 256))


def flatten(li):
    o = []
    for l in li:
        o.extend(l)
    return o


def decode_int_from_hex(x):
    r = decode_int(decode_hex(x).lstrip(b"\x00"))
    return r


def decode_int(v):
    """decodes and integer from serialization"""
    if len(v) > 0 and (v[0] == b'\x00' or v[0] == 0):
        raise Exception("No leading zero bytes allowed for integers")
    return big_endian_to_int(v)


def bloomables(event):
    # return [event.get("address")] + [BigEndianInt(32).serialize(topic) for topic in event.get("topics")]
    # return [decode_hex(event.get("address"))] + [topic.hex() for topic in event.get("topics")]
    return [decode_hex(event.get("address"))] + [decode_hex(topic.hex()) for topic in event.get("topics")]


def build_bloom_filter(events):
    blooms = [bloomables(event) for event in events]
    bloom = bloom_from_list(flatten(blooms))
    return encode_hex_0x(b64(bloom))


def verify_bloom(block_bloom, generated_bloom):
    return block_bloom == generated_bloom
