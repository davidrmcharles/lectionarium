#!/usr/bin/env python
'''
For rendering the lectionary as HTML or console text

Summary of Library Interface
======================================================================

* :func:`writeReadingsAsText`
* :func:`exportLectionaryAsHTML` - Export the whole Lectionary as HTML

Reference
======================================================================
'''

# Standard imports:
import os
import sys

# Local imports:
import bibleviews
import lectionary
import viewtools

def writeReadingsAsText(massTitle, readings, options, outputFile=sys.stdout):
    '''
    Write readings for console viewing.
    '''

    outputFile.write('%s\n' % ('=' * 80))
    outputFile.write('Readings for %s\n' % (massTitle))
    outputFile.write('%s\n' % ('=' * 80))

    for reading, verses in readings.iteritems():
        outputFile.write('\n%s\n' % reading.title)
        outputFile.write('\n%s' % bibleviews.formatVersesForConsole(verses))

def exportLectionaryAsHTML(outputFolderPath):
    '''
    Export the whole lectionary as HTML.
    '''

    _HTMLLectionaryExporter(outputFolderPath).export()

class _HTMLLectionaryExporter(object):

    def __init__(self, outputFolderPath):
        self._outputFolderPath = outputFolderPath
        self._indexExporter = _HTMLLectionaryIndexExporter(outputFolderPath)
        self._massExporter = _HTMLMassReadingsExporter(outputFolderPath)

    def export(self):
        '''
        Export the entire lectionary as HTML, with index, to
        `outputFolderPath`.
        '''

        self._indexExporter.export()
        self._massExporter.export()
        self._exportStylesheet()

    def _exportStylesheet(self):
        outputFilePath = os.path.join(self._outputFolderPath, 'lectionary.css')
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

class _HTMLLectionaryIndexExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath

    def export(self):
        '''
        Export an index of the lectionary as HTML.
        '''

        outputFolderPath = os.path.join(self.outputFolderPath, 'index.html')

        with open(outputFolderPath, 'w') as outputFile:
            self._writeIndexHead(outputFile)
            self._writeIndexBody(outputFile)
            self._writeIndexFoot(outputFile)

    def _writeIndexHead(self, outputFile):
        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="The Lectionary for Mass with Clemintine Vulgate Text"/>
    <meta name="keywords" content="Catholic,Bible,Lectionary,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>The Lectionary for Mass with Celementine Vulgate Text</title>
    <link rel="stylesheet" href="lectionary.css"/>
  </head>
  <body>
    <h1>The Lectionary for Mass with Celementine Vulgate Text</h1>
''')

    def _writeIndexBody(self, outputFile):
        self._writeIndexOfSomeMasses(
            outputFile,
            'Sunday Lectionary',
            lectionary.getLectionary().allSundayMasses)
        self._writeIndexOfSomeMasses(
            outputFile,
            'Weekday Lectionary',
            lectionary.getLectionary().allWeekdayMasses)
        self._writeIndexOfSomeMasses(
            outputFile,
            'Special Lectionary',
            lectionary.getLectionary().allSpecialMasses)

    def _writeIndexOfSomeMasses(self, outputFile, title, masses):
        outputFile.write('''\
    <h2>%s</h2>
''' % title)

        outputFile.write('''\
    <table>
      <tr>
''')

        for columnOfMasses in viewtools.columnizedList(masses, 2):
            self._writeColumnOfIndexEntries(outputFile, columnOfMasses)

        outputFile.write('''\
      </tr>
    </table>
''')

    def _writeColumnOfIndexEntries(self, outputFile, masses):
        outputFile.write('''\
        <td class="index-table-data">
          <ul>
''')
        for mass in masses:
            self._writeIndexOfMass(outputFile, mass)
        outputFile.write('''\
          </ul>
        </td>
''')

    def _writeIndexOfMass(self, outputFile, mass):
        outputFile.write('''\
            <li><a href="%s.html">%s</a></li>
''' % (mass.fqid, mass.displayName))

    def _writeIndexFoot(self, outputFile):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

class _HTMLMassReadingsExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath

    def export(self):
        '''
        Export the readings for mass as HTML.
        '''

        for mass in lectionary.getLectionary().allMasses:
            self._exportMass(mass)

    def _exportMass(self, mass):
        outputFilePath = os.path.join(
            self.outputFolderPath, '%s.html' % mass.fqid)

        outputFolderPath, outputFileName = os.path.split(outputFilePath)
        if len(outputFolderPath) > 0:
            if not os.path.exists(outputFolderPath):
                os.makedirs(outputFolderPath)

        with open(outputFilePath, 'w') as outputFile:
            self._writeMassHead(outputFile, mass)
            self._writeMassBody(outputFile, mass)
            self._writeMassFoot(outputFile, mass)

    def _writeMassHead(self, outputFile, mass):

        pathToIndex = 'index.html'
        lengthOfPath = _lengthOfPath(mass.fqid)
        if lengthOfPath > 1:
            parentStepsToIndex = '/'.join([
                    '..' for index in range(lengthOfPath - 1)])
            pathToIndex = '%s/index.html' % (parentStepsToIndex)

        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="Readings for %s"/>
    <meta name="keywords" content="Catholic,Bible,Lectionary,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>%s</title>
    <link rel="stylesheet" href="lectionary.css"/>
  </head>
  <body>
    <h1>%s</h1>
    <a href="%s">Index</a>
''' % (mass.displayName, mass.displayName, mass.displayName, pathToIndex))

    def _writeMassBody(self, outputFile, mass):
        pass

    def _writeMassFoot(self, outputFile, mass):
        outputFile.write('''\
    <hr/>
    Text by <a href="http://vulsearch.sourceforge.net/index.html">The Clementine Vulgate Project</a> |
    Formatting by <a href="https://github.com/davidrmcharles/lectionarium">lectionarium</a>
  </body>
</html>
''')

def _lengthOfPath(path):
    head, tail = os.path.split(path)
    if head == '':
        return 1
    else:
        return 1 + _lengthOfPath(head)
