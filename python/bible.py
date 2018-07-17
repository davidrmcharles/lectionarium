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
* :class:`Bible` - The whole canon of Sacrd Scripture
* :funce:`getBible` - A singleton instance of :class:`Bible`
* :class:`Book` - A single book with all its text

* :func:`getVerses` - Get an object representation of some verses
* :func:`formatVersesForConsole` - Format verses for display on the console

Reference
======================================================================
'''

# Standard imports:
import argparse
import itertools
import os
import re
import sys
import textwrap

# Local imports:
import addrs
import citations
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

class FormattingError(RuntimeError):
    '''
    An error that occurred during formatting
    '''

    def __init__(self, s):
        RuntimeError.__init__(self, s)

class Paragraph(object):
    '''
    A paragraph of text, either prose or poetry, and the means to
    format it for either the console or the browser.
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

    def __init__(self, formatting, useColor=True):
        self.formatting = formatting
        self.useColor = useColor
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
                if self.useColor:
                    addrToken = '%s%d:%d%s' % (
                        self.DIM, chapter, verse, self.NORMAL)
                else:
                    addrToken = '[%d:%d]' % (chapter, verse)
            return '%s %s' % (addrToken, text)

        if isFirst:
            textWrapper = self.textWrapperForProse1
        else:
            textWrapper = self.textWrapperForProse2

        return textWrapper.fill(
            ' '.join([
                    formatLineOfProse(addr, text)
                    for addr, text in self.lines
                    ]))

    def _formatPoetryForConsole(self):

        def formatLineOfPoetry(addr, text, isFirst):
            if addr is None:
                addrToken = ''
            else:
                chapter, verse = addr
                addrToken = '[%d:%d]' % (chapter, verse)

            indentSize = (12 if isFirst else 16)
            addrToken = '%-*s' % (indentSize, addrToken)

            if self.useColor:
                addrToken = addrToken.replace('[', self.DIM)
                addrToken = addrToken.replace(']', self.NORMAL + '  ')

            return '%s%s' % (addrToken, text)

        return '\n'.join([
                formatLineOfPoetry(addr, text, index == 0)
                for index, (addr, text) in enumerate(self.lines)
                ])

    def formatForBrowser(self, isFirst=True):
        if self.formatting == 'prose':
            return self._formatProseForBrowser(isFirst)
        elif self.formatting == 'poetry':
            return self._formatPoetryForBrowser()

    def _formatProseForBrowser(self, isFirst):
        # TODO: Why do we have an empty paragraph in the first place?
        if len(self.lines) == 0:
            return ''

        def formatLineOfProse(addr, text):
            if addr is None:
                addrToken = ''
            else:
                chapter, verse = addr
                addrToken = '''\
<a name="%s"><sup class="prose-verse-number">%d</sup></a>''' % (
                    '%s:%s' % (chapter, verse), verse)
            return '%s %s' % (addrToken, text)

        return '<p>%s</p>' % '\n'.join([
                formatLineOfProse(addr, text)
                for addr, text in self.lines
                ])

    def _formatPoetryForBrowser(self):
        htmlLines = []

        for index, (addr, text) in enumerate(self.lines):
            if index == 0:
                htmlLines.append('<p class="first-verse-of-poetry">')
            elif addr is not None:
                htmlLines.append('</p>')
                htmlLines.append('<p class="non-first-verse-of-poetry">')

            if addr is not None:
                chapter, verse = addr
                htmlLines.append('''\
  <a name="%s"><sup class="poetry-verse-number">%d</sup></a>''' % (
                        '%s:%s' % (chapter, verse), verse))

            htmlLines.append('  %s<br/>' % text)

        htmlLines.append('</p>\n')
        return '\n'.join(htmlLines)

class VerseFormatter(object):
    '''
    Converts a list of `verses` to a formatted string that is readable
    in either the console or browser.

    The expected format of `verses` is the same as that returned by
    :func:`getVerses`.
    '''

    def __init__(self):
        self._useColor = True
        self.paragraphs = []
        self.verseAddr = None

    @property
    def useColor(self):
        '''
        ``True`` to insert color escape sequences, otherwise ``False``
        '''

        return self._useColor

    @useColor.setter
    def useColor(self, newValue):
        self._useColor = newValue

    @property
    def currentParagraphIsProse(self):
        '''
        ``True`` if the current paragraph is formatted as prose.
        '''

        return len(self.paragraphs) > 0 and \
            self.paragraphs[-1].formatting == 'prose'

    @property
    def currentParagraphIsNotProse(self):
        '''
        ``True`` if the current paragraph is formatted as prose.
        '''

        return len(self.paragraphs) > 0 and \
            self.paragraphs[-1].formatting != 'prose'

    @property
    def currentParagraphIsPoetry(self):
        '''
        ``True`` if the current paragraph is formatted as poetry.
        '''

        return len(self.paragraphs) > 0 and \
            self.paragraphs[-1].formatting == 'poetry'

    @property
    def currentParagraphIsNotPoetry(self):
        '''
        ``True`` if the current paragraph is formatted as poetry.
        '''

        return len(self.paragraphs) > 0 and \
            self.paragraphs[-1].formatting != 'poetry'

    def addTextToCurrentParagraph(self, text):
        '''
        Add `text` to the current paragraph.

        Unless `text` is the empty string, then do nothing.

        If there is no current paragraph, create a new paragraph of
        prose and add the text there.

        Forget `verseAddr` so we don't add more than once.
        '''

        if len(text) > 0:
            if len(self.paragraphs) == 0:
                self.paragraphs.append(Paragraph('prose', self.useColor))
            self.paragraphs[-1].addText(self.verseAddr, text)
            self.verseAddr = None

    def formatVerses(self, verses):
        '''
        Return the `verses` as a formatted, ready-to-display string.
        '''

        self.paragraphs = []

        # Allocate the verses to paragraphs.
        for verseAddr, verseText in verses:
            self.verseAddr = verseAddr
            self._formatVerse(verseText)

        # Trim the trailing empty paragraph (if there is one).
        if self.paragraphs[-1].isEmpty:
            self.paragraphs.pop()

    @property
    def consoleFormattedText(self):
        return '\n'.join([
                paragraph.formatForConsole(index == 0)
                for index, paragraph in enumerate(self.paragraphs)
                ]) + '\n'

    @property
    def htmlFormattedText(self):
        return '\n'.join([
                paragraph.formatForBrowser(index == 0)
                for index, paragraph in enumerate(self.paragraphs)
                ])

    def _formatVerse(self, verseText):
        '''
        Update `paragraphs` with the content of `verseAddr` and
        `verseText` while observing formatting metacharacters that appear
        in the `verseText`.
        '''

        metaCharRegex = r'[\[\]/\\]'

        matchResult = re.search(metaCharRegex, verseText)
        while matchResult is not None:
            # Capture everything up to the metacharacter in
            # `verseTextSegment`.
            verseTextSegment = verseText[:matchResult.start()].strip()

            metaChar = verseText[matchResult.start()]
            if metaChar == '[':
                self._handlePoetryBegin(verseTextSegment)
            elif metaChar == ']':
                self._handlePoetryEnd(verseTextSegment)
            elif metaChar == '/':
                self._handlePoetryLineBreak(verseTextSegment)
            elif metaChar == '\\':
                self._handleParagraphBreak(verseTextSegment)

            # Discard the portion of `verseText` up to and including
            # the metacharacter (the part we just handled) and attempt
            # to match again.
            verseText = verseText[matchResult.start() + 1:].strip()
            matchResult = re.search(metaCharRegex, verseText)

        # Everything that remains of the current `verseText` should be
        # committed to the current paragraph.
        self.addTextToCurrentParagraph(verseText)

    def _handlePoetryBegin(self, verseTextSegment):
        # This is a request to commit the current `verseTextSegment`
        # to the current paragraph and start a new paragraph with
        # poetry formatting.
        if self.currentParagraphIsPoetry:
            raise FormattingError(
                'Saw "[" inside of poetry!')

        self.addTextToCurrentParagraph(verseTextSegment)

        # This is here for the transition from Baruch 3:38 to 4:1.
        # Verse 3:38 terminates a paragraph of poetry, causing us to
        # add an empty paragraph of prose.  Then we see the beginning
        # of poetry in verse 4:1 and start a new paragraph of poetry.
        # We don't want the interleaving paragraph of prose.
        if len(self.paragraphs) > 0:
            if self.paragraphs[-1].isEmpty:
                self.paragraphs.pop()

        self.paragraphs.append(Paragraph('poetry', self.useColor))

    def _handlePoetryEnd(self, verseTextSegment):
        # This is a request to commit the current `verseTextSegment`
        # to the current paragraph, to start a new paragraph, and to
        # exit poetry formatting.
        if self.currentParagraphIsProse:
            raise FormattingError(
                'Saw "]" inside of prose!')

        self.addTextToCurrentParagraph(verseTextSegment)

        self.paragraphs.append(Paragraph('prose', self.useColor))

    def _handlePoetryLineBreak(self, verseTextSegment):
        # Assuming poetry formatting, this means a line break.  Add
        # the `verseTextSegment` to the current paragraph.
        if self.currentParagraphIsNotPoetry:
            # The first reading for all-souls-1 (Jb 19:1,23-27) has
            # precisely this thing, so it must be legit.
            #
            # raise FormattingError(
            #     'Saw "/" outside of poetry!')
            self.paragraphs.append(Paragraph('poetry', self.useColor))

        self.addTextToCurrentParagraph(verseTextSegment)

    def _handleParagraphBreak(self, verseTextSegment):
        # Assuming prose formatting, this means a paragraph break.
        # Commit the current `verseTextSegment` to the current
        # paragraph and start a new paragraph.
        if self.currentParagraphIsNotProse:
            # This appear in Obadiah, verse 16, so it must be legit.
            #
            # raise FormattingError(
            #     'Saw "\\" outside of prose!\n' +
            #     '    %s' % verseTextSegment)
            pass  # self.paragraphs.append(Paragraph('poetry', self.useColor))

        self.addTextToCurrentParagraph(verseTextSegment)

        # This is conditional for the sake of Baruch 4:4, which ends
        # poetry AND a paragraph with ']\'.  We don't two empty
        # paragraphs on the end.  One is enough.
        if not self.paragraphs[-1].isEmpty:
            self.paragraphs.append(Paragraph('prose', self.useColor))

def formatVersesForConsole(verses):
    '''
    Convert a list of `verses` to a formatted string that is readable
    on the console.

    The expected format of `verses` is the same as that returned by
    :func:`getVerses`.
    '''

    verseFormatter = VerseFormatter()
    verseFormatter.formatVerses(verses)
    return verseFormatter.consoleFormattedText

def main():
    '''
    This is the entry point to the command-line interface.
    '''

    args = _CommandLineParser().parse()

    if len(args.citations) > 0:
        verses = getVerses(' '.join(args.citations))
        sys.stdout.write(formatVersesForConsole(verses))
    elif args.exportFolderPath is not None:
        _HTMLBibleExporter(args.exportFolderPath).export()

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
                '\nCitations and the --export command are mutually exclusive.\n')
            raise SystemExit(1)

class _HTMLBibleExporter(object):

    def __init__(self, outputFolderPath):
        self._outputFolderPath = outputFolderPath
        self.indexExporter = _HTMLBibleIndexExporter(outputFolderPath)
        self.bookExporter = _HTMLBibleBookExporter(outputFolderPath)

    def export(self):
        '''
        Export the entire bible as HTML, with index, to
        `outputFolderPath`.
        '''

        self.indexExporter.export()
        self.bookExporter.export()
        self._exportStylesheet()

    def _exportStylesheet(self):
        outputFilePath = os.path.join(self._outputFolderPath, 'bible.css')
        with open(outputFilePath, 'w') as outputFile:
            self._writeStylesheet(outputFile)

    def _writeStylesheet(self, outputFile):
        outputFile.write('''\
.index-table-data {
  vertical-align: top;
}

.first-verse-of-poetry {
  padding-left: 60px;
  text-indent: -30px;
}

.non-first-verse-of-poetry {
  padding-left: 60px;
  text-indent: -30px;
  margin-top: -15px;
}

.prose-verse-number {
  color: red;
}

.poetry-verse-number {
  position: absolute;
  color: red;
}
''')

class _HTMLBibleIndexExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath

    def export(self):
        outputFilePath = os.path.join(self.outputFolderPath, 'index.html')

        with open(outputFilePath, 'w') as outputFile:
            self._writeIndexHead(outputFile)
            self._writeIndexBody(outputFile)
            self._writeIndexFoot(outputFile)

    def _writeIndexHead(self, outputFile):
        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="The Clemintine Vulgate Bible"/>
    <meta name="keywords" content="Catholic,Bible,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>Vulgata Clementina</title>
    <link rel="stylesheet" href="bible.css"/>
  </head>
  <body>
    <h1>Vulgata Clementina</h1>
    <hr>
''')

    def _writeIndexBody(self, outputFile):
        self._writeIndexOfTestament(
            outputFile, getBible().otBooks, 'Vetus Testamentum')
        self._writeIndexOfTestament(
            outputFile, getBible().ntBooks, 'Novum Testamentum')

    def _writeIndexOfTestament(self, outputFile, books, title):
        outputFile.write('''\
    <h2>%s</h2>
''' % title)

        outputFile.write('''\
    <table>
      <tr>
''')

        def columnizedList(things, columnCount):
            q, r = divmod(len(things), columnCount)
            begins = [x * q for x in range(columnCount)]
            counts = [q + int(bool(x)) for x in reversed(range(r + 1))]
            for begin, count in itertools.izip_longest(
                begins, counts, fillvalue=q):
                yield things[begin : begin + count]

        for columnOfBooks in columnizedList(books, 2):
            self._writeColumnOfIndexEntries(outputFile, columnOfBooks)

        outputFile.write('''\
      </tr>
    </table>
''')

    def _writeColumnOfIndexEntries(self, outputFile, books):
        outputFile.write('''\
        <td class="index-table-data">
          <ul>
''')
        for book in books:
            self._writeIndexOfBook(outputFile, book)
        outputFile.write('''\
          </ul>
        </td>
''')

    def _writeIndexOfBook(self, outputFile, book):
        outputFile.write('''\
            <li>''')

        outputFile.write(
            '<a href="%s.html">%s</a>' % (book.normalName, book.name))

        outputFile.write('</li>\n')

    def _writeIndexFoot(self, outputFile):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

class _HTMLBibleBookExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath
        self.formatter = VerseFormatter()
        self.formatter.useColor = False

    def export(self):
        for book in getBible().allBooks:
            self._exportBook(book)
            self._exportConcordance(book)

    def _exportBook(self, book):
        outputFilePath = os.path.join(
            self.outputFolderPath, '%s.html' % book.normalName)

        with open(outputFilePath, 'w') as outputFile:
            self._writeBookHead(outputFile, book)
            self._writeBookBody(outputFile, book)
            self._writeBookFoot(outputFile, book)

    def _writeBookHead(self, outputFile, book):
        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="The Clemintine Vulgate Bible"/>
    <meta name="keywords" content="Catholic,Bible,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>%s</title>
    <link rel="stylesheet" href="bible.css"/>
  </head>
  <body>
''' % book.name)

        outputFile.write('''\
    <h1>%s</h1>
    <a href="index.html">Index</a>
''' % book.name)

        if book.hasChapters:
            outputFile.write('''\
    |
''')
            chapterNumbers = [
                '<a href="#chapter-%s">%s</a>' % (chapterKey, chapterKey)
                for chapterKey in book.text.chapterKeys
                ]
            outputFile.write('''\
    %s
''' % ' | '.join(chapterNumbers))

        outputFile.write('''\
    | <a href="%s-concordance.html">Concordance</a>
''' % book.normalName)

        outputFile.write('''\
''')

    def _writeBookBody(self, outputFile, book):
        for chapterKey in book.text._text.keys():
            if book.hasChapters:
                outputFile.write('''\
    <h2><a name="chapter-%d">%d</a></h2>
''' % (chapterKey, chapterKey))

            verses = book.text._allVersesInChapter(chapterKey)
            self.formatter.formatVerses(verses)
            outputFile.write(self.formatter.htmlFormattedText)

    def _writeBookFoot(self, outputFile, book):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

    def _exportConcordance(self, book):
        outputFilePath = os.path.join(
            self.outputFolderPath, '%s-concordance.html' % book.normalName)

        with open(outputFilePath, 'w') as outputFile:
            self._writeConcordanceHead(outputFile, book)
            self._writeConcordanceBody(outputFile, book)
            self._writeConcordanceFoot(outputFile, book)

    def _writeConcordanceHead(self, outputFile, book):
        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="The Clemintine Vulgate Bible"/>
    <meta name="keywords" content="Catholic,Bible,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>Concordance of %s</title>
    <link rel="stylesheet" href="bible.css"/>
  </head>
  <body>
''' % book.name)

        outputFile.write('''\
    <h1>Concordance of %s</h1>
''' % book.name)

        outputFile.write('''\
    <a href="index.html">Index</a>
''')

        outputFile.write('''\
    | <a href="%s.html">Text</a>
''' % book.normalName)

        outputFile.write('''\
    | %s
''' % ' | '.join([
                    '<a href="#%s">%s</a>' % (letter, letter)
                    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    ]))

    def _writeConcordanceBody(self, outputFile, book):
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            outputFile.write('''\
    <a name="%s"><h2>%s</h2></a>
''' % (letter, letter))
            entries = book.concordance.getEntriesForInitial(letter.lower())
            outputFile.write('''\
      <ul>
''')
            for entry in entries:
                self._writeConcordanceEntry(outputFile, book, entry)
            outputFile.write('''\
      </ul>
''')

    def _writeConcordanceEntry(self, outputFile, book, entry):
        def formatAddr(addr):
            addrToken = '%s:%s' % (addr[0], addr[1])

            return '<a href="%s.html#%s">%s</a>' % (
                book.normalName,
                addrToken,
                addrToken)

        def formatAddrList(addrs):
            return ', '.join([
                    formatAddr(addr)
                    for addr in addrs
                    ])

        outputFile.write('''\
<li>%s - %s</li>
''' % (entry.word, formatAddrList(entry.addrs)))

    def _writeConcordanceFoot(self, outputFile, book):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

if __name__ == '__main__':
    main()
