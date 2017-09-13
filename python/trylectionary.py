#!/usr/bin/env python
'''
Test-parse ``lectionary.txt``

This is just a quick and dirty way to find errors in
``lectionary.txt`` and expand the set of test cases.
'''

# Standard imports:
import traceback

# Local imports:
import bible
import citations

celebs = []
with open('lectionary.txt', 'r') as inputFile:
    waitingForCeleb = True
    celebName, readings = None, []
    for line in inputFile.readlines():
        line = line.strip()
        if ('READINGS' in line) or \
                ('Year' in line) or \
                ('Season' in line) or \
                (len(line) == 0):
            # These are all the reset conditions.  The line is either
            # categorical, or completely blank.  Getting here causes
            # us to commit a celebration object.
            if celebName is not None:
                celebs.append((celebName, readings))
                celebName, readings = None, []
            waitingForCeleb = True
            continue

        if waitingForCeleb:
            # Here is the name of the celebration
            waitingForCeleb = False
            celebName = line
            continue

        readings.append(line)

if celebName is not None:
    celebs.append((celebName, readings))
    celebName, readings = None, []

for celeb in celebs:
    readings = celeb[1]
    for reading in readings:
        if '(A)' in reading:
            continue
        for reading_ in reading.split(' or '):
            try:
                bible.getVerses(reading_)
            except Exception:
                traceback.print_exc()
                print 'Failed to parse:', reading_
                raise SystemExit()
