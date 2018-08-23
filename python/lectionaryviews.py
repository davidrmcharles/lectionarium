#!/usr/bin/env python
'''
For rendering the lectionary as HTML or console text

Summary of Command-Line Interface
======================================================================

Provide the name of a mass (or a date) and we will write its readings
to stdout.

Summary of Library Interface
======================================================================

* :func:`writeReadingsAsText`
* :func:`exportLectionaryAsHTML` - Export the whole Lectionary as HTML

Reference
======================================================================
'''

# Standard imports:
import argparse
import calendar
import collections
import itertools
import logging
import os
import sys
import traceback

# Local imports:
import bible
import bibleviews
import lectionary
import masses
import viewtools

def main(args=None):
    '''
    The command-line interface.
    '''

    # Create the command-line parser.
    exampleText = '''\
Examples:

    lectionary.py trinity-sunday
    lectionary.py 2017-10-17
    lectionary.py today

By default, only the cycle-applicable readings are included.  To see
all readings, append '#' to the name of the mass (or date).  For
example:

    lectionary.py trinity-sunday#
    lectionary.py 2017-10-17#
    lectionary.py today#

To see only the readings for a particular cycle, append '#' and the
name of the cycle to the name of the mass (or date).  For example:

    lectionary.py trinity-sunday#C
    lectionary.py 2017-10-17#A
    lectionary.py today#A
'''
    parser = argparse.ArgumentParser(
        description='''\
Provide the name of a mass (or a date) and we will write its readings
to stdout.''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=exampleText)

    parser.add_argument(
        '--list-all-ids',
        action='store_true',
        dest='listAllIDs',
        help='list all mass ids (and exit)')
    parser.add_argument(
        '--list-weekday-ids',
        action='store_true',
        dest='listWeekdayIDs',
        help='list weekday mass ids (and exit)')
    parser.add_argument(
        '--list-sunday-ids',
        action='store_true',
        dest='listSundayIDs',
        help='list weekday mass ids (and exit)')
    parser.add_argument(
        '--list-special-ids',
        action='store_true',
        dest='listSpecialIDs',
        help='list special mass ids (and exit)')
    parser.add_argument(
        '--export',
        dest='exportFolderPath',
        default=None,
        help='export the whole lectionary')

    parser.add_argument(
        'query',
        metavar='QUERY',
        nargs='?',
        help='the id of mass (or a date)')

    # Parse the command-line and handle the list options (if present).
    options = parser.parse_args(args)
    if options.listAllIDs:
        sys.stderr.write('%s\n' % (
                lectionary.getLectionary().allIDsFormatted))
        raise SystemExit(1)
    if options.listWeekdayIDs:
        sys.stderr.write('%s\n' % (
                lectionary.getLectionary().weekdayIDsFormatted))
        raise SystemExit(1)
    if options.listSundayIDs:
        sys.stderr.write('%s\n' % (
                lectionary.getLectionary().sundayIDsFormatted))
        raise SystemExit(1)
    if options.listSpecialIDs:
        sys.stderr.write('%s\n' % (
                lectionary.getLectionary().specialIDsFormatted))
        raise SystemExit(1)

    if options.exportFolderPath is not None:
        exportLectionaryAsHTML(options.exportFolderPath)
        return

    # If no query was provided, print help and exit.
    if options.query is None:
        parser.print_help()
        raise SystemExit(1)

    # Parse the query.
    try:
        massTitle, readings = lectionary.getReadings(options.query)
    except lectionary.NonSingularResultsError as e:
        sys.stderr.write('%s\n' % e.message)
        raise SystemExit(-1)

    # Write all the readings for the mass to stdout.
    writeReadingsAsText(massTitle, readings, options)

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
        self._calendarExporter = _HTMLLectionaryCalendarExporter(
            outputFolderPath)
        self._massExporter = _HTMLMassReadingsExporter(outputFolderPath)

    def export(self):
        '''
        Export the entire lectionary as HTML, with index, to
        `outputFolderPath`.
        '''

        self._indexExporter.export()
        self._calendarExporter.export()
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
    <meta name="description" content="The Lectionary for Mass (Clementine Vulgate Text)"/>
    <meta name="keywords" content="Catholic,Bible,Lectionary,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>The Lectionary for Mass (Clementine Vulgate Text)</title>
    <link rel="stylesheet" href="lectionary.css"/>
  </head>
  <body>
    <h1>The Lectionary for Mass (Clementine Vulgate Text)</h1>
''')

    def _writeIndexBody(self, outputFile):
        self._writeIndexOfSomeMasses(
            outputFile,
            'Sunday Lectionary',
            lectionary.getLectionary().allSundayMasses)
        self._writeIndexOfSomeMasses(
            outputFile,
            'Special Lectionary',
            lectionary.getLectionary().allSpecialMasses)
        self._writeIndexOfWeekdayMasses(
            outputFile,
            lectionary.getLectionary().allWeekdayMasses)

    def _writeIndexOfSomeMasses(self, outputFile, title, masses_):
        outputFile.write('''\
    <h2>%s</h2>
''' % title)

        outputFile.write('''\
    <table>
      <tr>
''')

        for columnOfMasses in viewtools.columnizedList(masses_, 2):
            self._writeColumnOfIndexEntries(outputFile, columnOfMasses)

        outputFile.write('''\
      </tr>
    </table>
''')

    def _writeIndexOfWeekdayMasses(self, outputFile, masses_):
        outputFile.write('''\
    <h2>Weekday Lectionary</h2>
''')

        for seasonid in lectionary.getLectionary().weekdayMassSeasonIDs:
            self._writeIndexOfWeekdayMassesInSeason(
                outputFile, seasonid)

    def _writeIndexOfWeekdayMassesInSeason(self, outputFile, seasonid):
        outputFile.write('''\
    <h3>%s</h3>
''' % masses._seasonLongDisplayName(seasonid))

        for weekid in lectionary.getLectionary().weekdayMassWeekIDs(
            seasonid):
            self._writeIndexOfWeekdayMassesInWeek(
                outputFile, seasonid, weekid)

    def _writeIndexOfWeekdayMassesInWeek(self, outputFile, seasonid, weekid):
        if weekid is not None:
            outputFile.write('''\
    <h4>%s</h4>
''' % masses._weekAndSeasonDisplayName(seasonid, weekid))

        masses_ = lectionary.getLectionary().weekdayMassesInWeek(
            seasonid, weekid)
        outputFile.write('''\
    <ul>
''')
        for mass in masses_:
            self._writeShortIndexEntryForMass(outputFile, mass)
        outputFile.write('''
    </ul>
''')

    def _writeColumnOfIndexEntries(self, outputFile, masses_):
        outputFile.write('''\
        <td class="index-table-data">
          <ul>
''')
        for mass in masses_:
            self._writeLongIndexEntryForMass(outputFile, mass)
        outputFile.write('''\
          </ul>
        </td>
''')

    def _writeLongIndexEntryForMass(self, outputFile, mass):
        outputFile.write('''\
            <li><a href="%s.html">%s</a></li>
''' % (mass.fqid, mass.longDisplayName))

    def _writeShortIndexEntryForMass(self, outputFile, mass):
        outputFile.write('''\
            <li><a href="%s.html">%s</a></li>
''' % (mass.fqid, _massShortDisplayName(mass)))

    def _writeIndexFoot(self, outputFile):
        outputFile.write('''\
    <hr/>
    <a href="../index.html">fideidepositum.org</a>
  </body>
</html>
''')

class _HTMLLectionaryCalendarExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath
        self.year = 2018

    def export(self):
        '''
        Export a lectionary calendar as HTML.
        '''

        outputFolderPath = os.path.join(
            self.outputFolderPath, '%d.html' % self.year)

        with open(outputFolderPath, 'w') as outputFile:
            self._writeCalendarHead(outputFile)
            self._writeCalendarBody(outputFile)
            self._writeCalendarFoot(outputFile)

    def _writeCalendarHead(self, outputFile):
        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="The Lectionary for Mass (Clementine Vulgate Text)"/>
    <meta name="keywords" content="Catholic,Bible,Lectionary,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>%d Lectionary for Mass (Clementine Vulgate Text)</title>
    <link rel="stylesheet" href="lectionary.css"/>
    <style>
      td, th {
        padding: 6px;
        text-align: center;
        vertical-align: top;
      }
    </style>
  </head>
  <body>
    <h1>%d Lectionary for Mass (Clementine Vulgate Text)</h1>
''' % (self.year, self.year))

    def _writeCalendarBody(self, outputFile):
        parser = _LectionaryCalendarHTMLParser()
        parser.feed(
            calendar.HTMLCalendar(
                calendar.SUNDAY).formatyear(self.year))
        outputFile.write(parser.html)

    def _writeCalendarFoot(self, outputFile):
        outputFile.write('''\
    <hr/>
    <a href="../index.html">fideidepositum.org</a>
  </body>
</html>
''')

class _LectionaryCalendarHTMLParser(viewtools.IdentityHTMLParser):
    '''
    Inserts hyperlinks into the calendar generated by
    ``calendar.HTMLCalendar``.
    '''

    def __init__(self):
        viewtools.IdentityHTMLParser.__init__(self)
        self.expectMonth = False
        self.expectDay = False
        self.month = None
        self.calendar = lectionary.Calendar(2018)

    def handle_starttag(self, tag, attrs):
        viewtools.IdentityHTMLParser.handle_starttag(self, tag, attrs)

        attrs = collections.OrderedDict(attrs)
        if self._isMonthStartTag(tag, attrs):
            self.expectMonth = True
        elif self._isDayStartTag(tag, attrs):
            self.expectDay = True

    def _isMonthStartTag(self, tag, attrs):
        return (tag == 'th') and attrs.get('class', None) == 'month'

    def _isDayStartTag(self, tag, attrs):
        days = ('sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat')
        return (tag == 'td') and attrs.get('class', None) in days

    def handle_data(self, data):
        if self.expectMonth:
            self.month = data
            self.tokens.append(data)
            self.expectMonth = False
        elif self.expectDay:
            self.tokens.append(self._makeLink(data))
            self.expectDay = False
        else:
            self.tokens.append(data)

    def _makeLink(self, data):
        month, day = self._parseMonth(self.month), self._parseDay(data)
        try:
            masses = self.calendar.massesByDate(month, day)
        except:
            traceback.print_exc()
            return data

        if len(masses) > 1:
            sys.stderr.write('Multiple masses on %d-%d!\n' % (month, day))

        return '<a href="%s.html">%s</a>' % (masses[0].fqid, data)

    def _parseMonth(self, data):
        return [
            'January', 'February', 'March',
            'April', 'May', 'June',
            'July', 'August', 'September',
            'October', 'November', 'December'
            ].index(data) + 1

    def _parseDay(self, data):
        return int(data)

class _HTMLMassReadingsExporter(object):

    def __init__(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath
        self.formatter = bibleviews._VerseFormatter()
        self.formatter.useColor = False

    def export(self):
        '''
        Export the readings for mass as HTML.
        '''

        for mass in itertools.chain(
            lectionary.getLectionary().allSundayMasses,
            lectionary.getLectionary().allSpecialMasses,
            lectionary.getLectionary().allWeekdayMasses):
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
        pathToStylesheet = 'lectionary.css'
        lengthOfPath = _lengthOfPath(mass.fqid)
        if lengthOfPath > 1:
            parentStepsToIndex = '/'.join([
                    '..' for index in range(lengthOfPath - 1)])
            pathToIndex = '%s/index.html' % (parentStepsToIndex)
            pathToStylesheet = '%s/lectionary.css' % (parentStepsToIndex)

        outputFile.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="description" content="Readings for %s"/>
    <meta name="keywords" content="Catholic,Bible,Lectionary,Latin"/>
    <meta name="author" content="David R M Charles"/>
    <title>%s</title>
    <link rel="stylesheet" href="%s"/>
  </head>
  <body>
    <h1>%s</h1>
    <a href="%s">Index</a>
''' % (
                _massLongDisplayName(mass),
                _massLongDisplayName(mass),
                pathToStylesheet,
                _massLongDisplayName(mass),
                pathToIndex))

    def _writeMassBody(self, outputFile, mass):
        # Collect the readings into categories based upon cycle
        # applicability.
        readingsByCycles = collections.OrderedDict()
        for reading in mass.allReadings:
            if reading.cycles not in readingsByCycles:
                readingsByCycles[reading.cycles] = []
            readingsByCycles[reading.cycles].append(reading)

        for index, (cycles, readings) in enumerate(readingsByCycles.iteritems()):
            if index != 0:
                outputFile.write('''\
    <hr/>
''')
            self._writeMassBodyForCycles(outputFile, cycles, readings)

    def _writeMassBodyForCycles(self, outputFile, cycles, readings):
        self._writeCyclesHeading(outputFile, cycles)
        for reading in readings:
            self._writeReading(outputFile, reading)

    def _writeCyclesHeading(self, outputFile, cycles):
        if cycles in ('I', 'II'):
            outputFile.write('''\
    <h2>Year %s</h2>
''' % cycles)
        elif cycles is not None:
            outputFile.write('''\
    <h2>%s</h2>
''' % ' and '.join(cycles))

    def _writeReading(self, outputFile, reading):
        self._writeReadingTitle(outputFile, reading)
        self._writeReadingVerses(outputFile, reading)

    def _writeReadingTitle(self, outputFile, reading):
        try:
            readingTitle = reading.title
        except Exception as e:
            traceback.print_exc()
            return

        outputFile.write('''\
<h3>%s</h3>
''' % readingTitle)

    def _writeReadingVerses(self, outputFile, reading):
        verses = bible.getVerses(reading.citation)

        try:
            self.formatter.formatVerses(verses)
        except Exception as e:
            traceback.print_exc()
            return

        outputFile.write(self.formatter.htmlFormattedText)
        outputFile.write('\n')

    def _writeMassFoot(self, outputFile, mass):
        pathToIndex = 'index.html'
        lengthOfPath = _lengthOfPath(mass.fqid)
        if lengthOfPath > 1:
            parentStepsToIndex = '/'.join([
                    '..' for index in range(lengthOfPath)])
            pathToIndex = '%s/index.html' % (parentStepsToIndex)

        outputFile.write('''\
    <hr/>
    <a href="%s">fideidepositum.org</a>
  </body>
</html>
''' % pathToIndex)

def _lengthOfPath(path):
    head, tail = os.path.split(path)
    if head == '':
        return 1
    else:
        return 1 + _lengthOfPath(head)

def _massShortDisplayName(mass):
    return mass.displayName

def _massLongDisplayName(mass):
    return mass.longDisplayName

if __name__ == '__main__':
    main()
