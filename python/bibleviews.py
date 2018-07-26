#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
For rendering books and verses as HTML or console text

Summary of Command-Line Interface
======================================================================

Provide a scripture citation and :mod:`bibleviwes` will write it to
``stdout``.  For example:

.. code-block:: none

    $ bible.py john 3:16
    [3:16] Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret : ut omnis
    qui credit in eum, non pereat, sed habeat vitam æternam.

Summary of Library Interface
======================================================================

* :func:`formatVersesForConsole` - Format verses for display on the console
* :func:`exportBibleAsHTML` - Export the whole Bible as HTML
* :class:`FormattingError` - Something went wrong with formatting

Reference
======================================================================
'''

# Standard imports:
import argparse
import os
import re
import sys
import textwrap

# Local imports:
import bible
import viewtools

def main():
    '''
    This is the entry point to the command-line interface.
    '''

    args = _CommandLineParser().parse()

    if len(args.citations) > 0:
        verses = bible.getVerses(' '.join(args.citations))
        sys.stdout.write(formatVersesForConsole(verses))
    elif args.exportFolderPath is not None:
        exportBibleAsHTML(args.exportFolderPath)

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

def formatVersesForConsole(verses):
    '''
    Convert a list of `verses` to a formatted string that is readable
    on the console.

    The expected format of `verses` is the same as that returned by
    :func:`getVerses`.
    '''

    verseFormatter = _VerseFormatter()
    verseFormatter.formatVerses(verses)
    return verseFormatter.consoleFormattedText

class _VerseFormatter(object):
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
                self.paragraphs.append(_Paragraph('prose', self.useColor))
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

        self.paragraphs.append(_Paragraph('poetry', self.useColor))

    def _handlePoetryEnd(self, verseTextSegment):
        # This is a request to commit the current `verseTextSegment`
        # to the current paragraph, to start a new paragraph, and to
        # exit poetry formatting.
        if self.currentParagraphIsProse:
            raise FormattingError(
                'Saw "]" inside of prose!')

        self.addTextToCurrentParagraph(verseTextSegment)

        self.paragraphs.append(_Paragraph('prose', self.useColor))

    def _handlePoetryLineBreak(self, verseTextSegment):
        # Assuming poetry formatting, this means a line break.  Add
        # the `verseTextSegment` to the current paragraph.
        if self.currentParagraphIsNotPoetry:
            # The first reading for all-souls-1 (Jb 19:1,23-27) has
            # precisely this thing, so it must be legit.
            #
            # raise FormattingError(
            #     'Saw "/" outside of poetry!')
            self.paragraphs.append(_Paragraph('poetry', self.useColor))

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
            self.paragraphs.append(_Paragraph('prose', self.useColor))

def exportBibleAsHTML(outputFolderPath):
    '''
    Export the whole Bible as HTML.
    '''

    _HTMLBibleExporter(outputFolderPath).export()

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
''')

    def _writeIndexBody(self, outputFile):
        self._writeIndexOfTestament(
            outputFile, bible.getBible().otBooks, 'Vetus Testamentum')
        self._writeIndexOfTestament(
            outputFile, bible.getBible().ntBooks, 'Novum Testamentum')

    def _writeIndexOfTestament(self, outputFile, books, title):
        outputFile.write('''\
    <h2>%s</h2>
''' % title)

        outputFile.write('''\
    <table>
      <tr>
''')

        for columnOfBooks in viewtools.columnizedList(books, 2):
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
        self.formatter = _VerseFormatter()
        self.formatter.useColor = False

    def export(self):
        for book in bible.getBible().allBooks:
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

        def formatDictionaryLink(word):
            return '''\
<a target="_blank" href="http://en.wiktionary.org/wiki/%s#Latin">Wiktionary</a>''' % (
                word)

        outputFile.write('''\
<li>%s - %s - %s</li>
''' % (
                entry.word,
                formatAddrList(entry.addrs),
                formatDictionaryLink(entry.word)))

    def _writeConcordanceFoot(self, outputFile, book):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

class _Paragraph(object):
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

class FormattingError(RuntimeError):
    '''
    An error that occurred during formatting
    '''

    def __init__(self, s):
        RuntimeError.__init__(self, s)

if __name__ == '__main__':
    main()
