#!/usr/bin/env python
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
        self._text = _Text(self.normalName, self.hasChapters)

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

    def __str__(self):
        return '%s (%s)' % (
            self.name,
            ', '.join(self.abbreviations))

    def __repr__(self):
        return '<bible.Book object "%s" at 0x%x>' % (
            self, id(self))

class _Text(object):

    def __init__(self, normalName, hasChapters):
        self.normalName = normalName
        self.hasChapters = hasChapters
        self._text = collections.OrderedDict()

    @property
    def chapterKeys(self):
        '''
        The list of keys for referring to particular chapters.
        '''

        return self._text.keys()

    def loadFromFile(self):
        '''
        Load the text of this book from a file of known name and
        location.
        '''

        textFileName = '%s.txt' % self.normalName
        textFilePath = os.path.join(_textFolderPath, textFileName)
        with open(textFilePath, 'r') as inputFile:
            for line in inputFile.readlines():
                self._loadLineOfText(line)

    def loadFromString(self, text):
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
        verseAddrList = locs.parse(verseAddrToken)
        verseAddr = verseAddrList[0]
        chapterKey, verseKey = verseAddr.first, verseAddr.second
        if chapterKey not in self._text:
            self._text[chapterKey] = collections.OrderedDict()
        self._text[chapterKey][verseKey] = verseText.strip()

    def _validateChapterKey(self, chapterKey):
        '''
        Raise ``KeyError`` if `chapterKey` is out of range.
        '''

        if chapterKey not in self._text:
            raise KeyError(
                'There is no chapter "%s" in book "%s"!' % (
                    chapterKey, self.normalName))

    def _validateChapterAndVerseKeys(self, chapterKey, verseKey):
        '''
        Raise ``KeyError`` if either `chapterKey` or `verseKey` are
        out of range.
        '''

        self._validateChapterKey(chapterKey)
        if verseKey not in self._text[chapterKey]:
            raise KeyError(
                'There is no verse "%s" in chapter "%s" of book "%s"!' % (
                    verseKey, chapterKey, self.normalName))

    def _validateVerseKey(self, verseKey):
        '''
        Raise ``KeyError`` if `verseKey` is out of range, or if this
        book has chapters.
        '''

        if self.hasChapters:
            raise KeyError(
                'There are chapters in book "%s"!' % (
                    self.normalName))
        self._validateChapterAndVerseKeys(1, verseKey)

    def getVerse(self, addr):
        '''
        Return an object representation of the verse indicated by
        `addr`.
        '''

        if addr.dimensionality == 2:
            # This is a chapter-and-verse reference to a single verse.
            chapterKey, verseKey = addr.first, addr.second
            self._validateChapterAndVerseKeys(chapterKey, verseKey)
            return [(
                    (chapterKey, verseKey),
                    self._text[chapterKey][verseKey]
                    )]
        else:
            if self.hasChapters:
                # This is a whole-chapter reference.  Add every single
                # verse in the chapter to the returned result.
                chapterKey = addr.first
                self._validateChapterKey(chapterKey)
                return [
                    ((chapterKey, verseKey), verseText)
                    for verseKey, verseText in \
                        self._text[chapterKey].iteritems()
                    ]
            else:
                # This is a single-verse reference.
                verseKey = addr.first
                self._validateVerseKey(verseKey)
                return [(
                        (verseKey),
                        self._text[1][verseKey]
                        )]

    def getRangeOfVerses(self, addrRange):
        '''
        Return an object representation of the verses indicated by
        `addrRange`.
        '''

        # TODO: Move this logic into AddrRange itself.
        if (addrRange.first.second is None) \
                and (addrRange.last.second is None):
            # Both seconds in the address range are ``None``, so the
            # interpretation depends upon whether or not the book has
            # chapters.
            if not self.hasChapters:
                # The book does not have chapters, so normalize the
                # chapter index to 1.
                firstChapterKey, firstVerseKey = 1, addrRange.first.first
                lastChapterKey, lastVerseKey = 1, addrRange.last.first
                self._validateVerseKey(firstVerseKey)
                self._validateVerseKey(lastVerseKey)
            else:
                # The book chapters, to treat the address range as a
                # range of chapters.
                firstChapterKey, lastChapterKey = \
                    addrRange.first.first, addrRange.last.first
                self._validateChapterKey(firstChapterKey)
                self._validateChapterKey(lastChapterKey)
                firstVerseKey, lastVerseKey = None, None
        else:
            firstChapterKey = addrRange.first.first
            firstVerseKey = addrRange.first.second
            lastChapterKey = addrRange.last.first
            lastVerseKey = addrRange.last.second
            if firstVerseKey is None:
                self._validateChapterKey(firstChapterKey)
            else:
                self._validateChapterAndVerseKeys(
                    firstChapterKey, firstVerseKey)
            if lastVerseKey is None:
                self._validateChapterKey(lastChapterKey)
            else:
                self._validateChapterAndVerseKeys(lastChapterKey, lastVerseKey)

        if firstChapterKey == lastChapterKey:
            # The entire range of text is in the same book.
            if (firstVerseKey is None) and (lastVerseKey is None):
                return self._allVersesInChapter(firstChapterKey)
            else:
                return self._middleVersesInChapter(
                    firstChapterKey, firstVerseKey, lastVerseKey)

        # Add the verses from the first chapter in the range.
        result = []
        if firstVerseKey is None:
            result.extend(self._allVersesInChapter(firstChapterKey))
        else:
            result.extend(
                self._lastVersesInChapter(firstChapterKey, firstVerseKey))

        # Add all the verses from any interior chapters.
        for chapter in range(firstChapterKey + 1, lastChapterKey):
            result.extend(
                self._allVersesInChapter(
                    chapter))

        # Add the verses from the last chapter in the range.
        if lastVerseKey is None:
            result.extend(self._allVersesInChapter(lastChapterKey))
        else:
            result.extend(
                self._firstVersesInChapter(lastChapterKey, lastVerseKey))

        return result

    def _visitAllVersesInChapter(self, chapterKey):
        '''
        Return a visitor onto every verse object associated with
        `chapterKey`.
        '''

        return (
            ((chapterKey, verseKey), verseText)
            for verseKey, verseText in self._text[chapterKey].iteritems()
            )

    def _allVersesInChapter(self, chapterKey):
        return list(self._visitAllVersesInChapter(chapterKey))

    def _visitLastVersesInChapter(self, chapterKey, firstVerseKey):
        '''
        Return a visitor onto every verse object associated with
        `chapterKey` starting with `firstVerseKey`.
        '''

        def isExcluded(item):
            verseAddr, verseText = item
            chapterKey, verseKey = verseAddr
            return verseKey < firstVerseKey

        return itertools.dropwhile(
            isExcluded, self._visitAllVersesInChapter(chapterKey))

    def _lastVersesInChapter(self, chapterKey, firstVerseKey):
        return list(self._visitLastVersesInChapter(chapterKey, firstVerseKey))

    def _visitFirstVersesInChapter(self, chapterKey, lastVerseKey):
        '''
        Return a visitor onto every verse object associated with
        `chapterKey` up to an including `lastVerseKey`.
        '''

        def isIncluded(item):
            verseAddr, verseText = item
            chapterKey, verseKey = verseAddr
            return verseKey <= lastVerseKey

        return itertools.takewhile(
            isIncluded, self._visitAllVersesInChapter(chapterKey))

    def _firstVersesInChapter(self, chapterKey, lastVerseKey):
        return list(self._visitFirstVersesInChapter(chapterKey, lastVerseKey))

    def _visitMiddleVersesInChapter(self,
                                    chapterKey,
                                    firstVerseKey,
                                    lastVerseKey):
        '''
        Return a visitor onto the inclusive range of verses,
        [`firstVerseKey`, `lastVerseKey`] in the chapter having
        `chapterKey`.
        '''

        def isIncluded(item):
            verseAddr, verseText = item
            chapterKey, verseKey = verseAddr
            return (verseKey >= firstVerseKey) and (verseKey <= lastVerseKey)

        return itertools.ifilter(
            isIncluded, self._visitAllVersesInChapter(chapterKey))

    def _middleVersesInChapter(self, chapterKey, firstVerseKey, lastVerseKey):
        return list(
            self._visitMiddleVersesInChapter(
                chapterKey, firstVerseKey, lastVerseKey))

    def getAllVerses(self):
        '''
        Return an object representation of every verse in the book.
        '''

        verses = []
        for chapterKey, chapterVerses in self._text.iteritems():
            for verseKey, verseText in chapterVerses.iteritems():
                verses.append(((chapterKey, verseKey), verseText))
        return verses

    def write(self, outputFile=sys.stdout):
        '''
        Write the entire text of the book to `outputFile` in a format
        that resembles the original input.
        '''

        for chapterKey, verses in self._text.iteritems():
            for verseKey, verseText in verses.iteritems():
                outputFile.write(
                    '%s %s\n' % (locs.Addr(chapterKey, verseKey), verseText))

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
