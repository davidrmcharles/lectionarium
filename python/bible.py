#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
For retrieving texts from Sacred Scripture

This module currently uses the Celementine Vulgate text maintained
here:

* http://vulsearch.sourceforge.net/index.html

Summary of Command-Line Interface
======================================================================

Provide a scripture citation and :mod:`bible` will write it to
``stdout``.  For example:

.. code-block:: none

    $ bible.py john 3:16
    [3:16] Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret : ut omnis
    qui credit in eum, non pereat, sed habeat vitam æternam.

You can use this to experiment with and observe the behavior library
functions :func:`getVerses` and :func:`formatVersesForConsole`.

Summary of Library Interface
======================================================================

* :func:`getVerses` - Get an object representation of some verses
* :func:`formatVersesForConsole` - Format verses for display on the console

Reference
======================================================================
'''

# Standard imports:
import itertools
import sys
import textwrap

# Local imports:
import books
import locs
import citations

def getVerses(query):
    '''
    Return an object representation of the verses associated with
    `query` that you can format according to your needs.

    The `query` is parsed by :func:`citations.parse`.

    The representation of the returned verses is a ``list`` of pairs.
    The first element in each pair is the **address** of a verse.  The
    second element in each pair is the **text** of the same verse.

    The address of the verse is itself a pair of integers representing
    the **chapter** and **verse** respectively.  (This will have to
    change to handle the insertions into Esther.)
    '''

    citation = citations.parse(query)
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
    Convert a list of `verses` to a formatted string that is readable
    on the console.

    The expected format of `verses` is the same as that returned by
    :func:`getVerses`.
    '''

    lines = []
    for verseAddr, verseText in verses:
        chapterIndex, verseIndex = verseAddr
        lines.append(
            '[%d:%d] %s\n' % (chapterIndex, verseIndex, verseText))

    return textwrap.fill(' '.join(lines), width=80) + '\n'

def main():
    '''
    This is the entry point to the command-line interface.
    '''

    if len(sys.argv) == 1:
        sys.stderr.write(
            'Provide a scripture citation and we will write it to stdout.\n')
        raise SystemExit(1)

    verses = getVerses(' '.join(sys.argv[1:]))

    sys.stdout.write(formatVersesForConsole(verses))

if __name__ == '__main__':
    main()
