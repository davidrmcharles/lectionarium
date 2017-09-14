#!/usr/bin/env python
'''
Tests for :mod:`lectionary`
'''

# Standard imports:
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

