#!/usr/bin/env python
'''
Books

Interface
======================================================================

* :class:`Book` - A single canonical book with its text
* :func:`findBook` - Find a canonical book
* :func:`parseBookTokensGreedily` - Parse adjacent book tokens
* :func:`parseBookToken` - Parse a single book token

Internals
======================================================================

* :class:`_Bible` - All the canonical books
'''

# Standard imports:
import collections
import inspect
import itertools
import os
import sys

# Local imports:
import locs

# For the moment, assume that the text is in '../../myclemtext'.
_thisFilePath = inspect.getfile(inspect.currentframe())
_projectFolderPath = os.path.dirname(os.path.dirname(_thisFilePath))
_textFolderPath = os.path.join(_projectFolderPath, 'myclemtext')

class Book(object):
    '''
    Represents a single scriptural 'book'.
    '''

    def __init__(self, name, abbreviations=[], hasChapters=False):
        self.name = name
        self.abbreviations = abbreviations
        self._text = collections.OrderedDict()
        self._hasChapters = hasChapters

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

    @property
    def hasChapters(self):
        '''
        ``True`` if the book has chapters, otherwise ``False``.  (Some
        of the smaller books don't.)

        We currently defer assignment of this property until the text
        is loaded.  That may not be the best strategy.
        '''

        return self._hasChapters

    def matchesToken(self, token):
        '''
        Return ``True`` if `token` can refer to this book.
        '''

        token = ''.join(token.lower().split())
        return token in [self.normalName] + self.normalAbbreviations

    def __str__(self):
        return '%s (%s)' % (
            self.name,
            ', '.join(self.abbreviations))

    def __repr__(self):
        return '<bible.Book object "%s" at 0x%x>' % (
            self, id(self))

    def loadTextFromFile(self):
        '''
        Load the text of this book from a file of known name and
        location.
        '''

        textFileName = '%s.txt' % self.normalName
        textFilePath = os.path.join(_textFolderPath, textFileName)
        with open(textFilePath, 'r') as inputFile:
            for line in inputFile.readlines():
                self._loadLineOfText(line)

    def loadTextFromString(self, text):
        '''
        Load the text of this book from a string.  (To support unit
        testing.)
        '''

        for line in text.splitlines():
            self._loadLineOfText(line)

    def _loadLineOfText(self, line):
        '''
        This method supports the other load methods by loading a
        single verse.
        '''

        verseAddrToken, verseText = line.split(' ', 1)
        verseAddrList = locs.parseLocsToken(verseAddrToken)
        verseAddr = verseAddrList[0]
        chapterIndex, verseIndex = verseAddr.first, verseAddr.second
        if chapterIndex not in self._text:
            self._text[chapterIndex] = collections.OrderedDict()
        self._text[chapterIndex][verseIndex] = verseText.strip()

    def getVerse(self, point):
        '''
        Return an object representation of the text indicated by
        `point`.
        '''

        if point.dimensionality == 2:
            # This is a chapter-and-verse reference to a single verse.
            chapterIndex, verseIndex = point.first, point.second
            return [(
                    (chapterIndex, verseIndex),
                    self._text[chapterIndex][verseIndex]
                    )]
        else:
            if self.hasChapters:
                # This is a whole-chapter reference.  Add
                # every single verse in the chapter to the
                # returned result.
                chapterIndex = point.first
                return [
                    ((chapterIndex, verseIndex), verseText)
                    for verseIndex, verseText in \
                        self._text[chapterIndex].iteritems()
                    ]
            else:
                # This is a single-verse reference.
                verseIndex = point.first
                return [(
                        (verseIndex),
                        self._text[1][verseIndex]
                        )]

    def getRangeOfVerses(self, addrRange):
        '''
        Return an object representation of the text indicated by
        `addrRange`.
        '''

        firstChapter = addrRange.first.first
        firstVerse = addrRange.first.second

        lastChapter = addrRange.last.first
        lastVerse = addrRange.last.second

        if firstChapter == lastChapter:
            # The entire range of text is in the same book.
            if (firstVerse is None) and (lastVerse is None):
                return self._allVersesInChapter(firstChapter)
            else:
                return self._middleVersesInChapter(
                    firstChapter, firstVerse, lastVerse)

        # Add the verses from the first chapter in the range.
        result = []
        if firstVerse is None:
            result.extend(self._allVersesInChapter(firstChapter))
        else:
            result.extend(self._lastVersesInChapter(firstChapter, firstVerse))

        # Add all the verses from any interior chapters.
        for chapter in range(firstChapter + 1, lastChapter):
            result.extend(
                self._allVersesInChapter(
                    chapter))

        # Add the verses from the last chapter in the range.
        if lastVerse is None:
            result.extend(self._allVersesInChapter(lastChapter))
        else:
            result.extend(self._firstVersesInChapter(lastChapter, lastVerse))

        return result

    def _visitAllVersesInChapter(self, chapter):
        '''
        Return a visitor onto every verse object in a `chapter`.
        '''

        return (
            ((chapter, verseIndex), verseText)
            for verseIndex, verseText in self._text[chapter].iteritems()
            )

    def _allVersesInChapter(self, chapter):
        return list(self._visitAllVersesInChapter(chapter))

    def _visitLastVersesInChapter(self, chapter, firstVerse):
        '''
        Return a visitor onto every verse object in a `chapter`
        starting with `firstVerse`.
        '''

        def isExcluded(item):
            verseAddr, verseText = item
            chapterIndex, verseIndex = verseAddr
            return verseIndex < firstVerse

        return itertools.dropwhile(
            isExcluded, self._visitAllVersesInChapter(chapter))

    def _lastVersesInChapter(self, chapter, firstVerse):
        return list(self._visitLastVersesInChapter(chapter, firstVerse))

    def _visitFirstVersesInChapter(self, chapter, lastVerse):
        '''
        Return a visitor onto every verse object in a `chapter` up to
        an including `lastVerse`.
        '''

        def isIncluded(item):
            verseAddr, verseText = item
            chapterIndex, verseIndex = verseAddr
            return verseIndex <= lastVerse

        return itertools.takewhile(
            isIncluded, self._visitAllVersesInChapter(chapter))

    def _firstVersesInChapter(self, chapter, lastVerse):
        return list(self._visitFirstVersesInChapter(chapter, lastVerse))

    def _visitMiddleVersesInChapter(self, chapter, firstVerse, lastVerse):
        '''
        Return a visitor onto the inclusive range of verses,
        [`firstVerse`, `lastVerse`] in `chapter`.
        '''

        def isIncluded(item):
            verseAddr, verseText = item
            chapterIndex, verseIndex = verseAddr
            return (verseIndex >= firstVerse) and (verseIndex <= lastVerse)

        return itertools.ifilter(
            isIncluded, self._visitAllVersesInChapter(chapter))

    def _middleVersesInChapter(self, chapter, firstVerse, lastVerse):
        return list(
            self._visitMiddleVersesInChapter(
                chapter, firstVerse, lastVerse))

    def getAllVerses(self):
        '''
        Return an object representation of every verse in the book.
        '''

        verses = []
        for chapterIndex, chapterVerses in self._text.iteritems():
            for verseIndex, verseText in chapterVerses.iteritems():
                verses.append(((chapterIndex, verseIndex), verseText))
        return verses

    def writeText(self, outputFile=sys.stdout):
        '''
        Write the entire text of the book to `outputFile` in a format
        that resembles the original input.
        '''

        for chapterIndex, verses in self._text.iteritems():
            for verseIndex, verseText in verses.iteritems():
                outputFile.write(
                    '%s %s\n' % (Addr(chapterIndex, verseIndex), verseText))

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
        All books.
        '''

        return self._allBooks

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
            book.loadTextFromFile()

_bible = _Bible()

def findBook(bookToken):
    '''
    Return the :class:`Book` object that goes with `bookToken`.
    '''

    return _bible.findBook(bookToken)

def parseBookTokensGreedily(tokens):
    '''
    Return the book represented by the leading tokens and the number
    of tokens consumed.  If no book can be parsed out of the tokens,
    return ``(None, 0)``.

    This function parses in a 'greedy' fashion, trying to consume as
    many tokens as possible.  This is key to parsing 'Song of Songs',
    whose abbreviations include 'Song'.
    '''

    for index in reversed(range(len(tokens))):
        superToken = ''.join(tokens[:index + 1])
        book = parseBookToken(superToken)
        if book is not None:
            return book, index + 1
    return None, 0

def parseBookToken(token):
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
