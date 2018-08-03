#!/usr/bin/env python
'''
Tests for :mod:`viewtools`
'''

# Standard imports:
import unittest

# Local imports:
import viewtools

class columnizedListTestCase(unittest.TestCase):

    def test_specialLecationaryInTwoColumns(self):
        '''
        This is the case where I first noticed the error: 21 items
        spread across two columns.
        '''

        specialMasses = (
            'trinity-sunday',
            'corpus-christi',
            'sacred-heart-of-jesus',
            'mary-mother-of-god',
            'presentation-of-the-lord',
            'joseph-husband-of-mary',
            'annunciation',
            'john-the-baptist-vigil',
            'john-the-baptist',
            'peter-and-paul-vigil',
            'peter-and-paul',
            'transfiguration',
            'assumption-vigil',
            'assumption',
            'triumph-of-the-cross',
            'all-saints',
            'all-souls-1',
            'all-souls-2',
            'all-souls-3',
            'dedication-of-st-john-lateran',
            'immaculate-conception',
            )
        expectedFirstColumn = (
            'trinity-sunday',
            'corpus-christi',
            'sacred-heart-of-jesus',
            'mary-mother-of-god',
            'presentation-of-the-lord',
            'joseph-husband-of-mary',
            'annunciation',
            'john-the-baptist-vigil',
            'john-the-baptist',
            'peter-and-paul-vigil',
            'peter-and-paul',
            )
        expectedSecondColumn = (
            'transfiguration',
            'assumption-vigil',
            'assumption',
            'triumph-of-the-cross',
            'all-saints',
            'all-souls-1',
            'all-souls-2',
            'all-souls-3',
            'dedication-of-st-john-lateran',
            'immaculate-conception',
            )

        columns = list(viewtools.columnizedList(specialMasses, 2))
        self.assertEquals(expectedFirstColumn, columns[0])
        self.assertEquals(expectedSecondColumn, columns[1])

if __name__ == '__main__':
    unittest.main()
