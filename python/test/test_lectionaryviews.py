#!/usr/bin/env python
'''
Tests for :mod:`lectionaryviews`
'''

# Standard imports:
import StringIO
import sys
import unittest

# Local imports:
import lectionary
import lectionaryviews

class mainTestCase(unittest.TestCase):

    def test_noArguments(self):
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        with self.assertRaises(SystemExit):
            lectionaryviews.main([])
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

class lengthOfPathTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(1, lectionaryviews._lengthOfPath('foo'))
        self.assertEqual(2, lectionaryviews._lengthOfPath('foo/bar'))
        self.assertEqual(3, lectionaryviews._lengthOfPath('foo/bar/zod'))

class massShortDisplayNameTestCase(unittest.TestCase):

    def test_december17(self):
        self.assertEqual(
            'December 17',
            lectionaryviews._massShortDisplayName(
                self._findMass('advent/end-of-advent/12-17')))

    def test_palmSunday(self):
        self.assertEqual(
            'Palm Sunday',
            lectionaryviews._massShortDisplayName(
                self._findMass('holy-week/palm-sunday')))

    def _findMass(self, massID):
        return lectionary.getLectionary().findMass(massID)

class massLongDisplayNameTestCase(unittest.TestCase):

    def test_firstSundayOfAdvent(self):
        self.assertEqual(
            '1st Sunday of Advent',
            lectionaryviews._massLongDisplayName(
                self._findMass('advent/week-1/sunday')))

    def test_thirdSundayOfOrdinaryTime(self):
        self.assertEqual(
            '3rd Sunday of Ordinary Time',
            lectionaryviews._massLongDisplayName(
                self._findMass('ordinary/week-3/sunday')))

    def test_mondayInTheSecondWeekOfAdvent(self):
        self.assertEqual(
            'Monday in the Second Week of Advent',
            lectionaryviews._massLongDisplayName(
                self._findMass('advent/week-2/monday')))

    def test_december17(self):
        self.assertEqual(
            'December 17',
            lectionaryviews._massLongDisplayName(
                self._findMass('advent/end-of-advent/12-17')))

    def test_fridayInTheFourthWeekOfLent(self):
        self.assertEqual(
            'Friday in the Fourth Week of Lent',
            lectionaryviews._massLongDisplayName(
                self._findMass('lent/week-4/friday')))

    def test_thursdayAfterAshWednesday(self):
        self.assertEqual(
            'Thursday After Ash Wednesday',
            lectionaryviews._massLongDisplayName(
                self._findMass('lent/week-of-ash-wednesday/thursday')))

    def test_palmSunday(self):
        self.assertEqual(
            'Palm Sunday',
            lectionaryviews._massLongDisplayName(
                self._findMass('holy-week/palm-sunday')))

    def test_palmSunday(self):
        self.assertEqual(
            'Mass of the Lord\'s Supper',
            lectionaryviews._massLongDisplayName(
                self._findMass('holy-week/mass-of-the-lords-supper')))

    def test_goodFriday(self):
        self.assertEqual(
            'Good Friday',
            lectionaryviews._massLongDisplayName(
                self._findMass('holy-week/good-friday')))

    def test_easterSunday(self):
        self.assertEqual(
            'Easter Sunday',
            lectionaryviews._massLongDisplayName(
                self._findMass('easter/week-1/easter-sunday')))

    def test_seventhDayOfChristmas(self):
        self.assertEqual(
            'Seventh Day of Christmas',
            lectionaryviews._massLongDisplayName(
                self._findMass('christmas/day-7')))

    def test_stStephen(self):
        self.assertEqual(
            'Second Day of Christmas (St. Stephen)',
            lectionaryviews._massLongDisplayName(
                self._findMass('christmas/day-2-st-stephen')))

    def test_ashWednesday(self):
        self.assertEqual(
            'Ash Wednesday',
            lectionaryviews._massLongDisplayName(
                self._findMass('lent/week-of-ash-wednesday/ash-wednesday')))

    def test_wednesdayInHolyWeek(self):
        self.assertEqual(
            'Wednesday in Holy Week',
            lectionaryviews._massLongDisplayName(
                self._findMass('holy-week/wednesday')))

    def test_thursdayChrismMass(self):
        self.assertEqual(
            'Thursday Chrism Mass',
            lectionaryviews._massLongDisplayName(
                self._findMass('holy-week/thursday-chrism-mass')))

    def test_saturdayInTheSeventhWeekOfEaster(self):
        self.assertEqual(
            'Saturday in the Seventh Week of Easter',
            lectionaryviews._massLongDisplayName(
                self._findMass('easter/week-7/saturday')))

    def test_mondayInTheFirstWeekOfOrdinaryTime(self):
        self.assertEqual(
            'Monday in the First Week of Ordinary Time',
            lectionaryviews._massLongDisplayName(
                self._findMass('ordinary/week-1/monday')))

    def _findMass(self, massID):
        return lectionary.getLectionary().findMass(massID)

if __name__ == '__main__':
    unittest.main()
