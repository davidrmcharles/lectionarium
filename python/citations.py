#!/usr/bin/env python
'''
Citations

* :class:`Citation`
* :func:`parseCitation`
'''

# Local imports:
import books
import locs

class Citation(object):
    '''
    A sequence of one or more verse locations within a particular
    book.

    Each verse location is potentially a verse address or an verse
    address range.  For example:

    * John 3:16 - verse address
    * Exodus 20:1-10 - verse address range
    * Acts 13:16-17,27 - verse address range, verse address
    '''

    def __init__(self, book, locs):
        self._book = book
        self._locs = locs

    @property
    def book(self):
        '''
        The normalized name of the book.
        '''

        return self._book

    @property
    def locs(self):
        '''
        The verse locations as they were provided.  (Perhaps this is a
        mix of both verse addresses and verse address ranges.)
        '''

        return self._locs

    @property
    def addrRanges(self):
        '''
        The verse locationss normalized to verse address ranges.
        '''

        # Perhaps this logic belongs in the constructor.
        def normalize(loc):
            if isinstance(loc, locs.AddrRange):
                return loc
            else:
                return locs.AddrRange(loc, loc)

        return [
            normalize(loc)
            for loc in self.locs
            ]

def parseCitation(text):
    '''
    Parse a human-readable, single-book bible reference and return the
    result as a :class:`Citation`.
    '''

    # Fail if `text` is not a string.
    if not isinstance(text, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to parseCitation()!' % (
                type(text), text))

    # Fail if there are no non-white characters in `text`.
    tokens = text.strip().split()
    if len(tokens) == 0:
        raise ValueError(
            'No non-white characters passed to parseCitation()!')

    # Try to parse a book out of the leading tokens in a 'greedy'
    # fashion.
    book, tokensConsumed = books.parseBookTokensGreedily(tokens)
    if book is None:
        raise ValueError(
            'Unable to identify the book in citation "%s"!' % text)

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
        verses = locs.parseLocsToken(remainingToken)

    return Citation(book, verses)
