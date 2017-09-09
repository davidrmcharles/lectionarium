#!/usr/bin/env python
'''
Represents the Canon of Scripture

Locations (OUTFACTORME!)
======================================================================

* :class:`Addr`
* :class:`AddrRange`
* :func:`_parseLocsToken`

Library Interface
======================================================================

* :class:`getVerses`

Everything Else
======================================================================

* :class:`Ref`
* :func:`parseRef`
* :func:`_parseBookTokensGreedily`
* :class:`Book`
* :class:`Bible`
* :func:`_parseBookToken`
'''

# Standard imports:
import collections
import inspect
import itertools
import os
import sys
import traceback

# For the moment, assume that the text is in '../../myclemtext'.
_thisFilePath = inspect.getfile(inspect.currentframe())
_projectFolderPath = os.path.dirname(os.path.dirname(_thisFilePath))
_textFolderPath = os.path.join(_projectFolderPath, 'myclemtext')

class Addr(object):
    '''
    Represents a single place in some scriptural book.

    This can be a single value that represents either a chapter or a
    verse (depending upon context).  Or, it can be a pair of values
    that definitely represents a chapter and verse.
    '''

    def __init__(self, first, second=None):
        self.first = first
        self.second = second

    @property
    def dimensionality(self):
        '''
        ``1`` for one-dimensional points, and ``2`` for
        two-dimensional points.
        '''

        return 1 if self.second is None else 2

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.first != other.first:
            return False
        if self.second != other.second:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        if self.first != other.first:
            return True
        if self.second != other.second:
            return True
        return False

    def __hash__(self):
        return hash((self.first, self.second))

    def __str__(self):
        if self.second is None:
            return '%d' % self.first
        else:
            return '%d:%d' % (self.first, self.second)

    def __repr__(self):
        if self.second is None:
            return '<bible.Addr object "%s" at 0x%x>' % (
                self.first, id(self))
        else:
            return '<bible.Addr object "%s:%s" at 0x%x>' % (
                self.first, self.second, id(self))

class AddrRange(object):
    '''
    Represents an range of text in some scriptural book.

    The range is inclusive, and bounded by two :class:`Addr` objects.
    '''

    def __init__(self, first, last):
        self.first = first
        self.last = last

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.first != other.first:
            return False
        if self.last != other.last:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        if self.first != other.first:
            return True
        if self.last != other.last:
            return True
        return False

    def __hash__(self):
        return hash((self.first, self.last))

    def __str__(self):
        return '%s-%s' % (self.first, self.last)

    def __repr__(self):
        return '<bible.AddrRange object "%s-%s" at 0x%x>' % (
            self.first, self.last, id(self))

def _parseLocsToken(token):
    '''
    Parse a chapter and verse token to a list of :class:`Addr` and
    :class:`AddrRange` objects.
    '''

    # Fail if `token` is not a string.
    if not isinstance(token, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to _parseLocsToken()!' % (
                type(token), token))

    token.strip()
    if len(token) == 0:
        raise ValueError(
            'Empty/whitespace-only string passed to'
            ' _parseLocsToken()!')

    prefix = None

    # Parse each of the comma-separated tokens to a list of points and
    # ranges.  There can be an arbitrary number of these.
    result = []
    comma_tokens = token.split(',')
    for comma_token in comma_tokens:
        # Parse each of the hyphen-separated subtokens within the
        # comma-separated token to a list of points and ranges.  There
        # may be only one or two of these subtokens.
        hyphen_tokens = comma_token.split('-')
        if len(hyphen_tokens) > 2:
            raise ValueError('Too many hyphens!')

        points = []
        for hyphen_token in hyphen_tokens:
            # Parse each of the colon-separated subtokens within the
            # hyphen-separated tken to a list of points.  There may be
            # only one or two of these subtokens.
            colon_tokens = hyphen_token.split(':')
            if len(colon_tokens) > 2:
                raise ValueError('Too many colons!')

            if len(colon_tokens) == 1:
                # There are no colons in this subtoken.  Reuse the
                # last prefix we've seen (if there is one).
                # Otherwise, generate a point without a prefix.
                if prefix is not None:
                    points.append(Addr(int(prefix), int(colon_tokens[0])))
                else:
                    points.append(Addr(int(colon_tokens[0])))

            elif len(colon_tokens) == 2:
                # This token has exactly point colon.  Generate a
                # two-dimensional point and remember the prefix for
                # later.
                first, second = colon_tokens
                points.append(Addr(int(first), int(second)))
                prefix = first

        # If parsing the hyphenated subtokens generated a single
        # point, add it to the result as-is.  Otherwise, if parsing
        # the hyphenated subtokens generated two points, wrap them in
        # a range.
        if len(points) == 1:
            result.extend(points)
        elif len(points) == 2:
            first, second = points
            result.append(AddrRange(first, second))

    return result

def getVerses(text):
    '''
    Return an object representation of the text associated with `text`.
    '''

    ref = parseRef(text)
    book = _bible.findBook(ref.book)
    return list(
        itertools.chain.from_iterable(
            book.getRangeOfVerses(addrRange)
            for addrRange in ref.addrRanges
            )
        )

class Ref(object):
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
            if isinstance(loc, AddrRange):
                return loc
            else:
                return AddrRange(loc, loc)

        return [
            normalize(loc)
            for loc in self.locs
            ]

def parseRef(text):
    '''
    Parse a human-readable, single-book bible reference and return the
    result as a :class:`Ref`.
    '''

    # Fail if `text` is not a string.
    if not isinstance(text, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to parseRef()!' % (
                type(text), text))

    # Fail if there are no non-white characters in `text`.
    tokens = text.strip().split()
    if len(tokens) == 0:
        raise ValueError(
            'No non-white characters passed to parseRef()!')

    # Try to parse a book out of the leading tokens in a 'greedy'
    # fashion.
    book, tokensConsumed = _parseBookTokensGreedily(tokens)

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
        verses = _parseLocsToken(remainingToken)

    return Ref(book, verses)

def _parseBookTokensGreedily(tokens):
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
        book = _parseBookToken(superToken)
        if book is not None:
            return book, index + 1
    return None, 0

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
        verseAddrList = _parseLocsToken(verseAddrToken)
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
        return [
            verse
            for verse in self._visitAllVersesInChapter(
                chapter)
            ]

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
        return [
            verse
            for verse in self._visitLastVersesInChapter(
                chapter, firstVerse)
            ]

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
        return [
            verse
            for verse in self._visitFirstVersesInChapter(
                chapter, lastVerse)
            ]

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
        return [
            verse
            for verse in self._visitMiddleVersesInChapter(
                chapter, firstVerse, lastVerse)
            ]

    def writeText(self, outputFile=sys.stdout):
        '''
        Write the entire text of the book to `outputFile` in a format
        that resembles the original input.
        '''

        for chapterIndex, verses in self._text.iteritems():
            for verseIndex, verseText in verses.iteritems():
                outputFile.write(
                    '%s %s\n' % (Addr(chapterIndex, verseIndex), verseText))

class Bible(object):
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
            Book('Jeremiah', ['Jr']),
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

_bible = Bible()

def _parseBookToken(token):
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
