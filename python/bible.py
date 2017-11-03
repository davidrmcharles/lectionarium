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
import re
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

class FormattingError(RuntimeError):
    '''
    Represents an error that has occurred during formatting.
    '''

    def __init__(self, s):
        RuntimeError.__init__(self, s)

class Paragraph(object):
    '''
    Represents a paragraph of text, either prose or poetry, and
    provides the means to format it.  (Console formatting only, at the
    moment!)
    '''

    # A wrapper for the leading paragraph of prose.
    textWrapperForProse1 = textwrap.TextWrapper(
        width=80)

    # A wrapper for second and following paragraphs of prose.
    textWrapperForProse2 = textwrap.TextWrapper(
        width=80, initial_indent='    ')

    # The ANSI sequence for 'dim' text.
    DIM = '\033[2m'

    # The ANSI sequence for 'normal brightness' text.
    NORMAL = '\033[22m'

    def __init__(self, formatting):
        self.formatting = formatting
        self.lines = []

    def addText(self, addr, text):
        self.lines.append((addr, text))

    @property
    def isEmpty(self):
        return len(self.lines) == 0

    def formatForConsole(self, isFirst=True):
        if self.formatting == 'prose':
            return self._formatProseForConsole(isFirst)
        elif self.formatting == 'poetry':
            return self._formatPoetryForConsole()

    def _formatProseForConsole(self, isFirst):
        def formatLineOfProse(addr, text):
            if addr is None:
                addrToken = ''
            else:
                chapter, verse = addr
                addrToken = '[%d:%d]' % (chapter, verse)
            return '%s %s' % (addrToken, text)

        if isFirst:
            textWrapper = self.textWrapperForProse1
        else:
            textWrapper = self.textWrapperForProse2

        return textWrapper.fill(
            ' '.join([
                    formatLineOfProse(addr, text)
                    for (addr, text)
                    in self.lines
                    ]))

    def _formatPoetryForConsole(self):
        def formatLineOfPoetry(addr, text, isFirst):
            if addr is None:
                addrToken = ''
            else:
                chapter, verse = addr
                addrToken = '[%d:%d]' % (chapter, verse)

            padding = (12 if isFirst else 16)
            return '%-*s%s' % (padding, addrToken, text)

        return '\n'.join([
                formatLineOfPoetry(addr, text, index == 0)
                for index, (addr, text) in
                enumerate(self.lines)
                ])

def _formatVerse(paragraphs, verseAddr, verseText):
    '''
    Update `paragraphs` with the content of `verseAddr` and
    `verseText` while observing formatting metacharacters that appear
    in the `verseText`.
    '''

    matchResult = re.search(r'[\[\]/\\]', verseText)
    while matchResult is not None:
        # Capture everything up to the metacharacter in `verseTextSegment`.
        verseTextSegment = verseText[:matchResult.start()].strip()
        metaChar = verseText[matchResult.start()]
        if metaChar == '[':
            # This is a request to commit the current
            # `verseTextSegment` to the current paragraph and start a
            # new paragraph with poetry formatting.
            if len(paragraphs) > 0 and paragraphs[-1].formatting == 'poetry':
                raise FormattingError(
                    'Saw "[" inside of poetry!')

            if len(verseTextSegment) > 0:
                if len(paragraphs) == 0:
                    paragraphs.append(Paragraph('prose'))
                paragraphs[-1].addText(verseAddr, verseTextSegment)
                verseAddr = None

            # This is here for the transition from Baruch 3:38 to 4:1.
            # Verse 3:38 terminates a paragraph of poetry, causing us
            # to add an empty paragraph of prose.  Then we see the
            # beginning of poetry in verse 4:1 and start a new
            # paragraph of poetry.  We don't want the interleaving
            # paragraph of prose.
            if len(paragraphs) > 0:
                if paragraphs[-1].isEmpty:
                    paragraphs.pop()

            paragraphs.append(Paragraph('poetry'))

        elif metaChar == ']':
            # This is a request to commit the current
            # `verseTextSegment` to the current paragraph, to start a
            # new paragraph, and to exit poetry formatting.
            if paragraphs[-1].formatting == 'prose':
                raise FormattingError(
                    'Saw "]" inside of prose!')

            if len(verseTextSegment) > 0:
                if len(paragraphs) == 0:
                    paragraphs.append(Paragraph('prose'))
                paragraphs[-1].addText(verseAddr, verseTextSegment)
                verseAddr = None

            paragraphs.append(Paragraph('prose'))

        elif metaChar == '/':
            # Assuming poetry formatting, this means a line break.
            # Add the `verseTextSegment` to the current paragraph.
            if len(paragraphs) > 0 and paragraphs[-1].formatting != 'poetry':
                # The first reading for all-souls-1 (Jb 19:1,23-27)
                # has precisely this thing, so it must be legit.
                #
                # raise FormattingError(
                #     'Saw "/" outside of poetry!')
                paragraphs.append(Paragraph('poetry'))

            if len(verseTextSegment) > 0:
                if len(paragraphs) == 0:
                    paragraphs.append(Paragraph('prose'))
                paragraphs[-1].addText(verseAddr, verseTextSegment)
                verseAddr = None

        elif metaChar == '\\':
            # Assuming prose formatting, this means a paragraph break.
            # Commit the current `verseTextSegment` to the current
            # paragraph and start a new paragraph.
            if len(paragraphs) > 0 and paragraphs[-1].formatting != 'prose':
                raise FormattingError(
                    'Saw "\\" outside of prose!')

            if len(verseTextSegment) > 0:
                if len(paragraphs) == 0:
                    paragraphs.append(Paragraph('prose'))
                paragraphs[-1].addText(verseAddr, verseTextSegment)
                verseAddr = None

            # This is conditional for the sake of Baruch 4:4, when
            # ends poetry AND a paragraph with ']\'.  We don't two
            # empty paragraphs on the end.  One is enough.
            if not paragraphs[-1].isEmpty:
                paragraphs.append(Paragraph('prose'))

        # Discard the portion of `verseText` up to and including the
        # metacharacter and attempt to match again.
        verseText = verseText[matchResult.start() + 1:]
        matchResult = re.search(r'[\[\]/\\]', verseText)

    # Everything that remains of the current `verseText` should be
    # committed to the current paragraph.

    if len(verseText) > 0:
        if len(paragraphs) == 0:
            paragraphs.append(Paragraph('prose'))
        paragraphs[-1].addText(verseAddr, verseText)

def formatVersesForConsole(verses):
    '''
    Convert a list of `verses` to a formatted string that is readable
    on the console.

    The expected format of `verses` is the same as that returned by
    :func:`getVerses`.
    '''

    paragraphs = []
    for verseAddr, verseText in verses:
        _formatVerse(paragraphs, verseAddr, verseText)

    if paragraphs[-1].isEmpty:
        paragraphs.pop()

    return '\n'.join([
            paragraph.formatForConsole(index == 0)
            for index, paragraph
            in enumerate(paragraphs)
            ]) + '\n'

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
