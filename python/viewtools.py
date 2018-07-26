'''
Things useful in view generation

Reference
======================================================================
'''

# Standard imports:
import itertools

def columnizedList(things, columnCount):
    q, r = divmod(len(things), columnCount)
    begins = [x * q for x in range(columnCount)]
    counts = [q + int(bool(x)) for x in reversed(range(r + 1))]
    for begin, count in itertools.izip_longest(
        begins, counts, fillvalue=q):
        yield things[begin : begin + count]
