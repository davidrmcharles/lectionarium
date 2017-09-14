#!/usr/bin/env python
'''
Sacred Scripture

Library Interface
======================================================================

* :func:`getVerses`
* :func:`formatVersesForConsole`
'''

# Standard imports:
import itertools
import sys
import textwrap

# Local imports:
import books
import locs
import citations

def getVerses(text):
    '''
    Return an object representation of the text associated with
    `text`.
    '''

    citation = citations.parse(text)
    book = books.findBook(citation.book)
    if citation.locs is None:
        # This is the citation of an entire book.
        return book.getAllVerses()

    return list(
        itertools.chain.from_iterable(
            book.getRangeOfVerses(addrRange)
            for addrRange in citation.addrRanges
            )
        )

def formatVersesForConsole(verses):
    '''
    Convert a list of verses to a formatted string that is readable on
    the console.
    '''

    lines = []
    for verseAddr, verseText in verses:
        chapterIndex, verseIndex = verseAddr
        lines.append(
            '[%d:%d] %s\n' % (chapterIndex, verseIndex, verseText))

    return textwrap.fill(' '.join(lines), width=80) + '\n'

def main():
    '''
    The command-line interface.
    '''

    if len(sys.argv) == 1:
        sys.stderr.write(
            'Provide a scripture citation and we will write it to stdout.\n')
        raise SystemExit(1)

    verses = getVerses(' '.join(sys.argv[1:]))

    sys.stdout.write(formatVersesForConsole(verses))

if __name__ == '__main__':
    main()
