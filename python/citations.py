#!/usr/bin/env python
'''
For parsing scriptural citations

Summary of Library Interface
======================================================================

* :func:`parse` - Parse a human-readable citation to an object representation
* :class:`Citation` - Represents a single-book scripture citation

Reference
======================================================================
'''

# Local imports:
import bible
import addrs

class Citation(object):
    '''
    Represents a citation as a sequence of verse addresses within one,
    particular book.

    Each verse location is either a verse address (:class:`addrs.Addr`)
    or a verse address range (:class:`addrs.AddrRange`).  For example:

    * John 3:16 - verse address
    * Exodus 20:1-10 - verse address range
    * Acts 13:16-17,27 - verse address range, verse address
    '''

    def __init__(self, book, addrs):
        self._book = book
        self._addrs = addrs

    def __str__(self):
        return '%s %s' % (
            self._book, ','.join([str(loc) for loc in self._addrs]))

    @property
    def displayString(self):
        '''
        A long-form display-string for the citation.
        '''

        book = bible._bible.findBook(self._book)
        return '%s %s' % (
            book.name,
            ','.join([str(loc) for loc in self._addrs]))

    @property
    def book(self):
        '''
        The normalized name of the book.
        '''

        return self._book

    @property
    def addrs(self):
        '''
        The verse locations as they were provided.  (Perhaps this is a
        mix of both verse addresses and verse address ranges.)
        '''

        return self._addrs

    @property
    def addrRanges(self):
        '''
        The verse locations with all verse address objects normalized
        to verse address range objects.
        '''

        # Perhaps this logic belongs in the constructor.
        def normalize(loc):
            if isinstance(loc, addrs.AddrRange):
                return loc
            else:
                return addrs.AddrRange(loc, loc)

        return [
            normalize(loc)
            for loc in self.addrs
            ]

def parse(query):
    '''
    Parse a human-readable citation (`query`) to its object
    representation.

    The book name is parsed by :func:`bible.parse`.  The locations
    within the book are parsed by :func:`addrs.parse`.  The result is a
    :class:`Citation` object.

    The `query` must be confined to a single book.

    '''

    # Fail if `query` is not a string.
    if not isinstance(query, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to citations.parse()!' % (
                type(query), query))

    # Fail if there are no non-white characters in `query`.
    tokens = query.strip().split()
    if len(tokens) == 0:
        raise ValueError(
            'No non-white characters passed to citations.parse()!')

    # Try to parse a book out of the leading tokens in a 'greedy'
    # fashion.
    book, tokensConsumed = bible.parse(tokens)
    if book is None:
        raise ValueError(
            'Unable to identify the book in citation "%s"!' % query)

    # If there is more than one token remaining, we have too many
    # tokens.
    remainingTokens = tokens[tokensConsumed:]
    if len(remainingTokens) > 1:
        raise ValueError(
            'Extra tokens %s!' % remainingTokens[1:])

    # If there is exactly remaining token, try to parse verses out of
    # it.
    verses = None
    if len(remainingTokens) == 1:
        remainingToken = remainingTokens[0]
        verses = addrs.parse(remainingToken)

    return Citation(book, verses)
