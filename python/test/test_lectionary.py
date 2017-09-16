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
    pass  # TODO?

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

