'''
Things useful in view generation

Reference
======================================================================
'''

# Standard imports:
import itertools

def columnizedList(things, columnCount):
    q, r = divmod(len(things), columnCount)

    # The number of *extra* items in each column (1 or 0)
    extras = [int(bool(x)) for x in reversed(range(r + 1))]
    if len(extras) < columnCount:
        extras.extend([0] * columnCount)

    # The number of total items in each column (count + 1 or count)
    counts = [q + x for x in extras]

    begin = 0
    for count in counts:
        yield things[begin : begin + count]
        begin += count
