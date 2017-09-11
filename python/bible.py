#!/usr/bin/env python
'''
Sacred Scripture

Library Interface
======================================================================

* :class:`getVerses`
'''

# Standard imports:
import itertools

# Local imports:
import books
import locs
import citations

def getVerses(text):
    '''
    Return an object representation of the text associated with
    `text`.
    '''

    citation = citations.parseCitation(text)
    book = books.findBook(citation.book)
    return list(
        itertools.chain.from_iterable(
            book.getRangeOfVerses(addrRange)
            for addrRange in citation.addrRanges
            )
        )
