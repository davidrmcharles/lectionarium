#!/usr/bin/env python
'''
Tests for :mod:`lectionary`
'''

# Standard imports:
import datetime
import unittest

# Local imports:
import lectionary

class MassTestCase(unittest.TestCase):

    def test_isSundayInOrdinaryTime(self):
        self.assertTrue(
            lectionary.Mass('2nd Sunday', [], None).isSundayInOrdinaryTime)
        self.assertTrue(
            lectionary.Mass('22nd Sunday', [], None).isSundayInOrdinaryTime)
        self.assertTrue(
            lectionary.Mass('34th Sunday (Christ the King)', [], None).isSundayInOrdinaryTime)
        self.assertFalse(
            lectionary.Mass('4th Sunday of Lent', [], None).isSundayInOrdinaryTime)

class OFSundayLectionaryTestCase(unittest.TestCase):
    pass  # TODO?

# textTestCase?
# firstChildTestCase?
# childrenTestCase?
# MissingAttrExceptionTestCase?
# attrTestCase?

class nextSundayTestCase(unittest.TestCase):

    def test_badDate(self):
        with self.assertRaises(TypeError):
            lectionary._nextSunday(None, 1)
        with self.assertRaises(TypeError):
            lectionary._nextSunday('', 1)
        with self.assertRaises(TypeError):
            lectionary._nextSunday(1, 1)

    def test_badCount(self):
        with self.assertRaises(TypeError):
            lectionary._nextSunday(datetime.date.today(), None)
        with self.assertRaises(TypeError):
            lectionary._nextSunday(datetime.date.today(), '')
        with self.assertRaises(TypeError):
            lectionary._nextSunday(datetime.date.today(), 0.0)
        with self.assertRaises(ValueError):
            lectionary._nextSunday(datetime.date.today(), 0)

    def test_dates(self):
        aSunday = datetime.date(2017, 9, 10)
        previousSunday1 = datetime.date(2017, 9, 3)
        previousSunday2 = datetime.date(2017, 8, 27)
        previousSunday3 = datetime.date(2017, 8, 20)
        nextSunday1 = datetime.date(2017, 9, 17)
        nextSunday2 = datetime.date(2017, 9, 24)
        nextSunday3 = datetime.date(2017, 10, 1)

        # A Sunday:
        self.assertEqual(previousSunday1, lectionary._nextSunday(aSunday, -1))
        self.assertEqual(previousSunday2, lectionary._nextSunday(aSunday, -2))
        self.assertEqual(previousSunday3, lectionary._nextSunday(aSunday, -3))
        self.assertEqual(nextSunday1, lectionary._nextSunday(aSunday, 1))
        self.assertEqual(nextSunday2, lectionary._nextSunday(aSunday, 2))
        self.assertEqual(nextSunday3, lectionary._nextSunday(aSunday, 3))

        # ...But not just any Monday.
        aMonday = datetime.date(2017, 9, 11)
        self.assertEqual(aSunday, lectionary._nextSunday(aMonday, -1))
        self.assertEqual(previousSunday1, lectionary._nextSunday(aMonday, -2))
        self.assertEqual(previousSunday2, lectionary._nextSunday(aMonday, -3))
        self.assertEqual(nextSunday1, lectionary._nextSunday(aMonday, 1))
        self.assertEqual(nextSunday2, lectionary._nextSunday(aMonday, 2))
        self.assertEqual(nextSunday3, lectionary._nextSunday(aMonday, 3))

        # A Saturday:
        aSaturday = datetime.date(2017, 9, 9)
        self.assertEqual(previousSunday1, lectionary._nextSunday(aSaturday, -1))
        self.assertEqual(previousSunday2, lectionary._nextSunday(aSaturday, -2))
        self.assertEqual(previousSunday3, lectionary._nextSunday(aSaturday, -3))
        self.assertEqual(aSunday, lectionary._nextSunday(aSaturday, 1))
        self.assertEqual(nextSunday1, lectionary._nextSunday(aSaturday, 2))
        self.assertEqual(nextSunday2, lectionary._nextSunday(aSaturday, 3))

class cycleForDateTestCase(unittest.TestCase):

    def test_early_2017(self):
        self.assertEqual(
            'A', lectionary._cycleForDate(
                datetime.date(2017, 1, 1)))

    def test_late_2017(self):
        self.assertEqual(
            'B', lectionary._cycleForDate(
                datetime.date(2017, 12, 31)))

class CalendarTestCase(unittest.TestCase):

    def test_2017(self):
        calendar = lectionary.Calendar(2017)

        testData = [
            # January
            (1, 1, ['a/solemnity-of-mary-mother-of-god']),
            (1, 8, ['a/epiphany']),
            (1, 15, ['a/2nd-sunday']),
            (1, 22, ['a/3rd-sunday']),
            (1, 29, ['a/4th-sunday']),

            # February
            (2, 2, ['presentation-of-the-lord']),
            (2, 5, ['a/5th-sunday']),
            (2, 12, ['a/6th-sunday']),
            (2, 19, ['a/7th-sunday']),
            (2, 26, ['a/8th-sunday']),

            # March
            (3, 5, ['a/1st-sunday-of-lent']),
            (3, 12, ['a/2nd-sunday-of-lent']),
            (3, 19, ['a/3rd-sunday-of-lent']),
            (3, 20, ['joseph-husband-of-mary']),
            (3, 25, ['annunciation']),
            (3, 26, ['a/4th-sunday-of-lent']),

            # April
            (4, 2, ['a/5th-sunday-of-lent']),
            (4, 9, ['a/passion-sunday-palm-sunday']),
            (4, 16, ['a/easter-sunday']),
            (4, 23, ['a/2nd-sunday-of-easter']),
            (4, 30, ['a/3rd-sunday-of-easter']),

            # May
            (5, 7, ['a/4th-sunday-of-easter']),
            (5, 14, ['a/5th-sunday-of-easter']),
            (5, 21, ['a/6th-sunday-of-easter']),
            (5, 28, ['a/7th-sunday-of-easter']),

            # June
            (6, 4, ['a/mass-of-the-day']),
            (6, 11, ['a/trinity-sunday-sunday-after-pentecost']),
            (6, 18, ['a/corpus-christi']),
            (6, 23, ['john-the-baptist-vigil']),
            (6, 24, ['john-the-baptist-mass-of-the-day']),
            (6, 25, ['a/12th-sunday']),
            (6, 28, ['peter-and-paul-vigil']),
            (6, 29, ['peter-and-paul-mass-of-the-day']),

            # July
            (7, 2, ['a/13th-sunday']),
            (7, 9, ['a/14th-sunday']),
            (7, 16, ['a/15th-sunday']),
            (7, 23, ['a/16th-sunday']),
            (7, 30, ['a/17th-sunday']),

            # August
            (8, 6, ['transfiguration']),
            (8, 13, ['a/19th-sunday']),
            (8, 14, ['assumption-vigil']),
            (8, 15, ['assumption-mass-of-the-day']),
            (8, 20, ['a/20th-sunday']),
            (8, 27, ['a/21st-sunday']),

            # September
            (9, 3, ['a/22nd-sunday']),
            (9, 10, ['a/23rd-sunday']),
            (9, 14, ['triumph-of-the-cross']),
            (9, 17, ['a/24th-sunday']),
            (9, 24, ['a/25th-sunday']),

            # October
            (10, 1, ['a/26th-sunday']),
            (10, 8, ['a/27th-sunday']),
            (10, 15, ['a/28th-sunday']),
            (10, 22, ['a/29th-sunday']),
            (10, 29, ['a/30th-sunday']),

            # November
            (11, 1, ['all-saints']),
            (11, 2, ['all-souls-first-mass', 'all-souls-second-mass', 'all-souls-third-mass']),
            (11, 5, ['a/31st-sunday']),
            (11, 9, ['dedication-of-st-john-lateran']),
            (11, 12, ['a/32nd-sunday']),
            (11, 19, ['a/33rd-sunday']),
            (11, 26, ['a/34th-sunday-christ-the-king']),

            # December
            (12, 3, ['b/1st-sunday-of-advent']),
            (12, 8, ['immaculate-conception']),
            (12, 10, ['b/2nd-sunday-of-advent']),
            (12, 17, ['b/3rd-sunday-of-advent']),
            (12, 24, ['b/4th-sunday-of-advent', 'b/christmas-vigil']),
            (12, 25, ['b/christmas-at-midnight', 'b/christmas-at-dawn', 'b/christmas-during-the-day']),
            ]

        for month, day, expectedMassIDs in testData:
            self.assertEqual(
                expectedMassIDs,
                [mass.uniqueID for mass in calendar.massesByDate(month, day)])

class parseTestCase(unittest.TestCase):

    def test_nonStrings(self):
        with self.assertRaises(TypeError):
            lectionary.parse(None)
        with self.assertRaises(TypeError):
            lectionary.parse(123)
        with self.assertRaises(TypeError):
            lectionary.parse(object())

    def test_emptyString(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('')

    def test_spacesOnly(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse(' ')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('  ')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('   ')

    def test_tooManySlashes(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('//')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('///')

    def test_badYear(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('/')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('d/')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('7/')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('#/')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('abc/')

class getReadingsTestCase(unittest.TestCase):

    def test_zeroResults(self):
        with self.assertRaises(lectionary.NonSingularResultsError):
            lectionary.getReadings('k')

    def test_multipleResults(self):
        with self.assertRaises(lectionary.NonSingularResultsError):
            lectionary.getReadings('a/i')

    def test_easterVigilYearA(self):
        massName, readings = lectionary.getReadings('a/easter-vigil')
        self.assertEqual('Easter Vigil', massName)
        self.assertEqual(9, len(readings))
        self.assertIn('Gn 1:1-2:2', readings)
        self.assertIn('Gn 22:1-18', readings)
        self.assertIn('Ex 14:15-15:1', readings)
        self.assertIn('Is 54:5-14', readings)
        self.assertIn('Is 55:1-11', readings)
        self.assertIn('Bar 3:9-15,32-4:4', readings)
        self.assertIn('Ez 36:16-17a,18-28', readings)
        self.assertIn('Rom 6:3-11', readings)
        self.assertIn('Mt 28:1-10', readings)

if __name__ == '__main__':
    unittest.main()

