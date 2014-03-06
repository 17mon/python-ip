import struct
from socket import gethostbyname
from socket import inet_aton
import os
import functools


_unpack_V = lambda b: struct.unpack("<L", b)
_unpack_N = lambda b: struct.unpack(">L", b)
_unpack_C = lambda b: struct.unpack("B", b)


try:
    with open(os.path.join(os.path.dirname(__file__), "17monipdb.dat"), "rb") as f:
        dat = f.read()
        offset, = _unpack_N(dat[:4])
        index = dat[4:offset]
except:
    print "cannot open file 17monipdb.dat"
    exit(0)


def cache(func):
    """cache the value in memory
    """
    table = func.cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = '{0}{1}'.format(args, kwargs)
        if key not in table:
            table[key] = func(*args, **kwargs)
        return table[key]
    return wrapper


@cache
def _find_by_ip(ip):
    nip = inet_aton(ip)
    ipdot = ip.split('.')
    if int(ipdot[0]) < 0 or int(ipdot[0]) > 255 or len(ipdot) != 4:
        return "N/A"

    tmp_offset = int(ipdot[0]) * 4
    start, = _unpack_V(index[tmp_offset:tmp_offset + 4])

    index_offset = index_length = 0
    max_comp_len = offset - 1028
    start = start * 8 + 1024
    while start < max_comp_len:
        if index[start:start + 4] >= nip:
            index_offset, = _unpack_V(index[start + 4:start + 7] + chr(0).encode('utf-8'))
            index_length, = _unpack_C(index[start + 7])
            break
        start += 8

    if index_offset == 0:
        return "N/A"

    res_offset = offset + index_offset - 1024
    return dat[res_offset:res_offset + index_length].decode('utf-8')


def find(name):
    try:
        ip = gethostbyname(name)
    except:
        return "wrong host name"

    return _find_by_ip(ip)
