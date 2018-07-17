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

* :func:`parse` - Parse adjacent book tokens to a :class:`Book` object
* :class:`Bible` - The whole canon of Sacred Scripture
* :func:`getBible` - A singleton instance of :class:`Bible`
* :class:`Book` - A single book with all its text
* :func:`getVerses` - Get an object representation of some verses

Reference
======================================================================
'''

# Standard imports:
import argparse
import itertools
import os
import sys

# Local imports:
import addrs
import citations
import rendering
import texts

def parse(tokens):
    '''
    Return the book represented by the leading tokens and the number
    of tokens consumed.  If no book can be parsed out of the tokens,
    return ``(None, 0)``.

    This function parses in a 'greedy' fashion, trying to consume as
    many tokens as possible.  This is key to parsing 'Song of Songs',
    whose abbreviations include 'Song'.
    '''

    def generateSupertokens(tokens):
        '''
        Given ``['foo', 'bar', 'zod']``, generate ``'foobarzod'``,
        ``'foobar'``, and ``'foo'``.
        '''

        for index in reversed(range(len(tokens))):
            yield ''.join(tokens[:index + 1]), index

    def parseSupertoken(token):
        '''
        Parse a book token in any form to a normalized form:

        * Full-book name (no abbreviation)
        * All lowercase
        * Interior whitespace removed
        '''

        book = getBible().findBook(token)
        if book is None:
            return None
        return book.normalName

    for superToken, index in generateSupertokens(tokens):
        book = parseSupertoken(superToken)
        if book is not None:
            return book, index + 1

    return None, 0

class Bible(object):
    '''
    The whole Canon of Scripture
    '''

    def __init__(self):
        self._otBooks = [
            Book('Genesis', ['Gn']),
            Book('Exodus', ['Ex']),
            Book('Leviticus', ['Lv']),
            Book('Numbers', ['Nm']),
            Book('Deuteronomy', ['Dt']),
            Book('Joshua', ['Jos']),
            Book('Judges', ['Jgs']),
            Book('Ruth', ['Ru']),
            Book('1 Samuel', ['1 Sm']),
            Book('2 Samuel', ['2 Sm']),
            Book('1 Kings', ['1 Kgs']),
            Book('2 Kings', ['2 Kgs']),
            Book('1 Chronicles', ['1 Chr']),
            Book('2 Chronicles', ['2 Chr']),
            Book('Ezra', ['Ezr']),
            Book('Nehemiah', ['Neh']),
            Book('Tobit', ['Tb']),
            Book('Judith', ['Jdt']),
            Book('Esther', ['Est']),
            Book('1 Maccabees', ['1 Mc']),
            Book('2 Maccabees', ['2 Mc']),
            Book('Job', ['Jb']),
            Book('Psalms', ['Ps', 'Pss']),
            Book('Proverbs', ['Prv']),
            Book('Ecclesiastes', ['Eccl']),
            Book('Song of Songs', ['Song', 'Sg']),
            Book('Wisdom', ['Wis']),
            Book('Sirach', ['Sir']),
            Book('Isaiah', ['Is']),
            Book('Jeremiah', ['Jer']),
            Book('Lamentations', ['Lam']),
            Book('Baruch', ['Bar']),
            Book('Ezekiel', ['Ez']),
            Book('Daniel', ['Dn']),
            Book('Hosea', ['Hos']),
            Book('Joel', ['Jl']),
            Book('Amos', ['Am']),
            Book('Obadiah', ['Ob'], hasChapters=False),
            Book('Jonah', ['Jon']),
            Book('Michah', ['Mi']),
            Book('Nahum', ['Na']),
            Book('Habakkuk', ['Hb']),
            Book('Zephaniah', ['Zep']),
            Book('Haggai', ['Hg']),
            Book('Zechariah', ['Zec']),
            Book('Malachi', ['Mal']),
            ]

        self._ntBooks = [
            Book('Matthew', ['Mt']),
            Book('Mark', ['Mk']),
            Book('Luke', ['Lk']),
            Book('John', ['Jn']),
            Book('Acts', ['Acts']),
            Book('Romans', ['Rom']),
            Book('1 Corinthians', ['1 Cor']),
            Book('2 Corinthians', ['2 Cor']),
            Book('Galatians', ['Gal']),
            Book('Ephesians', ['Eph']),
            Book('Philippians', ['Phil']),
            Book('Colossians', ['Col']),
            Book('1 Thessalonians', ['1 Thes']),
            Book('2 Thessalonians', ['2 Thes']),
            Book('1 Timothy', ['1 Tm']),
            Book('2 Timothy', ['2 Tm']),
            Book('Titus', ['Ti']),
            Book('Philemon', ['Phlm'], hasChapters=False),
            Book('Hebrews', ['Heb']),
            Book('James', ['Jas']),
            Book('1 Peter', ['1 Pt']),
            Book('2 Peter', ['2 Pt']),
            Book('1 John', ['1 Jn']),
            Book('2 John', ['2 Jn'], hasChapters=False),
            Book('3 John', ['3 Jn'], hasChapters=False),
            Book('Jude', ['Jude'], hasChapters=False),
            Book('Revelation', ['Rv']),
            ]

        self._allBooks = self._otBooks + self._ntBooks
        self._loadText()

    _instance = None

    @classmethod
    def _getInstance(cls):
        if cls._instance is None:
            cls._instance = Bible()
        return cls._instance

    @property
    def allBooks(self):
        '''
        All books
        '''

        return self._allBooks

    @property
    def otBooks(self):
        '''
        Old Testament books
        '''

        return self._otBooks

    @property
    def ntBooks(self):
        '''
        New Testament books
        '''

        return self._ntBooks

    def findBook(self, token):
        '''
        Find and return the book that goes with `token`.
        '''

        for book in self._allBooks:
            if book.matchesToken(token):
                return book
        return None

    def findText(self, ref):
        '''
        Find and return the text that goes with `ref`.
        '''

        book = self.findBook(ref.book)
        return book.findText(ref.verses)

    def _loadText(self):
        for book in self.allBooks:
            book.text.loadFromFile()

class Book(object):
    '''
    A single scriptural 'book'.
    '''

    def __init__(self, name, abbreviations=[], hasChapters=True):
        self.name = name
        self.abbreviations = abbreviations
        self._hasChapters = hasChapters
        self._text = texts.Text(self.normalName, self.hasChapters)
        self._concordance = None

    @property
    def normalName(self):
        '''
        The normalized name for the book:

        * Full-book name (no abbreviations)
        * All lowercase
        * No interior whitespace
        '''

        return ''.join(self.name.lower().split())

    @property
    def normalAbbreviations(self):
        '''
        The abbreviations for the book, normalized.

        (Same rules as for ``normalName``.
        '''

        return [
            ''.join(abbreviation.lower().split())
            for abbreviation in self.abbreviations
            ]

    def matchesToken(self, token):
        '''
        Return ``True`` if `token` can refer to this book.
        '''

        token = ''.join(token.lower().split())
        return token in [self.normalName] + self.normalAbbreviations

    @property
    def hasChapters(self):
        '''
        ``True`` if the book has chapters, otherwise ``False``.  (Some
        of the smaller books don't.)

        We currently defer assignment of this property until the text
        is loaded.  That may not be the best strategy.
        '''

        return self._hasChapters

    @property
    def text(self):
        '''
        The text content of the book.
        '''

        return self._text

    @property
    def concordance(self):
        if self._concordance is None:
            self._concordance = texts.Concordance()
            self._concordance.addWords(self._text.getAllWords())
        return self._concordance

    def __str__(self):
        return '%s (%s)' % (
            self.name,
            ', '.join(self.abbreviations))

    def __repr__(self):
        return '<bible.Book object "%s" at 0x%x>' % (
            self, id(self))

def getBible():
    '''
    Return a singleton instance of :class:`Bible`.
    '''

    return Bible._getInstance()

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
    book = getBible().findBook(citation.book)
    if citation.addrs is None:
        # This is the citation of an entire book.
        return book.text.getAllVerses()

    return list(
        itertools.chain.from_iterable(
            book.text.getRangeOfVerses(addrRange)
            for addrRange in citation.addrRanges
            )
        )

def main():
    '''
    This is the entry point to the command-line interface.
    '''

    args = _CommandLineParser().parse()

    if len(args.citations) > 0:
        verses = getVerses(' '.join(args.citations))
        sys.stdout.write(formatVersesForConsole(verses))
    elif args.exportFolderPath is not None:
        rendering.exportBibleAsHTML(args.exportFolderPath)

class _CommandLineParser(argparse.ArgumentParser):

    def __init__(self):
        argparse.ArgumentParser.__init__(
            self, description='The canon of Sacred Scripture in Python')
        self._configure()

    def _configure(self):
        self.add_argument(
            dest='citations',
            default=[],
            nargs='*',
            help='scripture citations')
        self.add_argument(
            '--export',
            dest='exportFolderPath',
            default=None,
            help='export the whole biblical text')

    def parse(self):
        '''
        Return an object representation of the command line.
        '''

        self.args = self.parse_args()
        self._rejectMissingCommand()
        self._rejectMultipleCommands()
        return self.args

    def _rejectMissingCommand(self):
        if (len(self.args.citations) == 0) and \
                (self.args.exportFolderPath is None):
            self.print_help()
            sys.stderr.write(
                '\nNo citations and no commands were provided.\n')
            raise SystemExit(1)

    def _rejectMultipleCommands(self):
        if (len(self.args.citations) > 0) and \
                (self.args.exportFolderPath is not None):
            self.print_help()
            sys.stderr.write(
                '\nCitations and the --export command'
                ' are mutually exclusive.\n')
            raise SystemExit(1)

if __name__ == '__main__':
    main()
