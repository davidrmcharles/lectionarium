#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
For parsing a reference to a scriptural book and retrieving all its
text

Summary of Library Interface
======================================================================

* :func:`parse` - Parse adjacent book tokens to a :class:`Book` object
* :func:`findBook` - Find and return a  :class:`Book` by name
* :class:`Book` - A single book with all its text

Reference
======================================================================
'''

# Local imports:
import addrs
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

        book = _bible.findBook(token)
        if book is None:
            return None
        return book.normalName

    for superToken, index in generateSupertokens(tokens):
        book = parseSupertoken(superToken)
        if book is not None:
            return book, index + 1

    return None, 0

def findBook(bookToken):
    '''
    Return the :class:`Book` object that goes with `bookToken`.
    '''

    return _bible.findBook(bookToken)

class Book(object):
    '''
    Represents a single scriptural 'book'.
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

class _Bible(object):
    '''
    Represents the whole Canon of Scripture.
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

_bible = _Bible()
