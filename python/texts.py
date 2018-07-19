# -*- coding: utf-8 -*-
'''
For working with text content and markup

Reference
======================================================================
'''

# Standard imports:
import collections
import inspect
import itertools
import os
import re
import sys

# Local imports:
import addrs

# For the moment, assume that the text is in '../../myclemtext'.
_thisFilePath = inspect.getfile(inspect.currentframe())
_projectFolderPath = os.path.dirname(os.path.dirname(_thisFilePath))
_textFolderPath = os.path.join(_projectFolderPath, 'myclemtext')

class Text(object):
    '''
    A Text divided into verses (and probably chapters too).
    '''

    def __init__(self, normalName, hasChapters=True):
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
        verseAddrList = addrs.parse(verseAddrToken)
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

    def getAllWords(self):
        '''
        Return each word (no punctuation, no formatting) in lowercase
        with its location.
        '''

        for verse in self.getAllVerses():
            verseAddr, verseText = verse
            for word in self._stripNonWordNonSpaceCharacters(verseText).split():
                yield verseAddr, word.lower()

    def _stripNonWordNonSpaceCharacters(self, text):
        return re.sub('[^A-Za-zÆŒæœë ]', '', text)

    def write(self, outputFile=sys.stdout):
        '''
        Write the entire text of the book to `outputFile` in a format
        that resembles the original input.
        '''

        for chapterKey, verses in self._text.iteritems():
            for verseKey, verseText in verses.iteritems():
                outputFile.write(
                    '%s %s\n' % (addrs.Addr(chapterKey, verseKey), verseText))

class Concordance(object):
    '''
    An alphabetical list of each word appearing in a text with the
    context in which each word appears.
    '''

    def __init__(self):
        self._entries = {}

    def addWords(self, words):
        for addr, word in words:
            wordEntry = self._ensureEntryForWord(word)
            wordEntry.addAddr(addr)
        self._sortEntries()

    def _ensureEntryForWord(self, word):
        initial = self._getInitialOfWord(word)
        if initial not in self._entries:
            self._entries[initial] = []

        for wordEntry in self._entries[initial]:
            if wordEntry.word == word:
                return wordEntry

        wordEntry = ConcordanceEntry(word)
        self._entries[initial].append(wordEntry)
        return wordEntry

    def _getInitialOfWord(self, word):
        initial = word[0]
        if initial in 'Ææ':
            return 'a'
        elif initial in 'Œœ':
            return 'o'
        return initial

    def _sortEntries(self):
        for wordEntries in self._entries.itervalues():
            wordEntries.sort(key=lambda wordEntry: wordEntry.sortableWord)

    def getEntries(self):
        return sorted(self._entries.iteritems())

    def getEntriesForInitial(self, initial):
        if initial not in self._entries:
            return []
        return self._entries[initial]

class ConcordanceEntry(object):

    def __init__(self, word, addrs=None):
        self.word = word
        self._sortableWord = None
        self.addrs = [] if addrs is None else addrs

    @property
    def sortableWord(self):
        if self._sortableWord is None:
            self._sortableWord = self.word. \
            replace('Æ', 'AE'). \
            replace('æ', 'ae'). \
            replace('Œœ', 'Oe'). \
            replace('œ', 'oe'). \
            replace('ë', 'e')
        return self._sortableWord

    def addAddr(self, addr):
        self.addrs.append(addr)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.word != other.word:
            return False
        if self.addrs != other.addrs:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        if self.word != other.word:
            return True
        if self.addrs != other.addrs:
            return True
        return False

    def __str__(self):
        return '%s - %s' % (self.word, self.addrs)

