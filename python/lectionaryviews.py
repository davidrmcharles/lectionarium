#!/usr/bin/env python
'''
For rendering the lectionary as HTML or console text

Summary of Library Interface
======================================================================

* :func:`writeReadingsAsText`

Reference
======================================================================
'''

# Standard imports:
import sys

# Local imports:
import bibleviews

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
