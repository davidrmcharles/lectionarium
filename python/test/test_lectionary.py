#!/usr/bin/env python
'''
Tests for :mod:`lectionary`
'''

# Standard imports:
import datetime
import sys
import traceback
import unittest

# Local imports:
import lectionary
import citations

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

class LectionaryTestCase(unittest.TestCase):
    '''
    This is not really a unit test for :class:`Lectionary`, but
    something to prove that we can parse all the citations that appear
    in our XML representation of the lectionaries and that we find the
    right number of them.
    '''

    def test_parseSundayCitations(self):
        readingCount = 0
        for mass in lectionary._lectionary.allSundayMasses:
            for reading in mass.readings:
                readingCount += 1
                citations.parse(reading)

        # $ grep --count /reading sunday-lectionary.xml
        self.assertEqual(659, readingCount)

    def test_parseWeekdayCitations(self):
        readingCount = 0
        for mass in lectionary._lectionary._weekdayMasses:
            for reading in mass.readings:
                readingCount += 1
                # TODO: Here is one we cannot parse yet!
                if reading == 'Est C:12,14-16,23-25':
                    continue
                citations.parse(reading)

        # $ grep --count /reading weekday-lectionary.xml
        self.assertEqual(861, readingCount)

    def test_parseSpecialCitations(self):
        readingCount = 0
        for mass in lectionary._lectionary._fixedDateMasses:
            for reading in mass.readings:
                readingCount += 1
                citations.parse(reading)

        # $ grep --count /reading special-lectionary.xml
        self.assertEqual(54, readingCount)

    def test_weekdayMassesInWeek(self):
        lectionary._lectionary.weekdayMassesInWeek(None, 'week-1')

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

class sundayCycleForDateTestCase(unittest.TestCase):

    def test_early_2017(self):
        self.assertEqual(
            'A', lectionary._sundayCycleForDate(
                datetime.date(2017, 1, 1)))

    def test_late_2017(self):
        self.assertEqual(
            'B', lectionary._sundayCycleForDate(
                datetime.date(2017, 12, 31)))

class CalendarTestCase(unittest.TestCase):

    def test_2017(self):
        calendar = lectionary.Calendar(2017)

        testData = [
            # January
            (1, 1, ['a/mary-mother-of-god']),
            (1, 2, ['01-02']),
            (1, 3, ['01-03']),
            (1, 4, ['01-04']),
            (1, 5, ['01-05']),
            (1, 6, ['01-06']),
            # (1, 7, ['???']),

            (1, 8, ['a/epiphany']),
            (1, 9, ['a/baptism-of-the-lord']),
            (1, 10, ['week-1-tuesday']),
            (1, 11, ['week-1-wednesday']),
            (1, 12, ['week-1-thursday']),
            (1, 13, ['week-1-friday']),
            (1, 14, ['week-1-saturday']),

            (1, 15, ['a/2nd-sunday']),
            (1, 16, ['week-2-monday']),
            (1, 17, ['week-2-tuesday']),
            (1, 18, ['week-2-wednesday']),
            (1, 19, ['week-2-thursday']),
            (1, 20, ['week-2-friday']),
            (1, 21, ['week-2-saturday']),

            (1, 22, ['a/3rd-sunday']),
            (1, 23, ['week-3-monday']),
            (1, 24, ['week-3-tuesday']),
            (1, 25, ['week-3-wednesday']),
            (1, 26, ['week-3-thursday']),
            (1, 27, ['week-3-friday']),
            (1, 28, ['week-3-saturday']),

            (1, 29, ['a/4th-sunday']),
            (1, 30, ['week-4-monday']),
            (1, 31, ['week-4-tuesday']),

            # February
            (2, 1, ['week-4-wednesday']),
            (2, 2, ['presentation-of-the-lord']),
            (2, 3, ['week-4-friday']),
            (2, 4, ['week-4-saturday']),

            (2, 5, ['a/5th-sunday']),
            (2, 6, ['week-5-monday']),
            (2, 7, ['week-5-tuesday']),
            (2, 8, ['week-5-wednesday']),
            (2, 9, ['week-5-thursday']),
            (2, 10, ['week-5-friday']),
            (2, 11, ['week-5-saturday']),

            (2, 12, ['a/6th-sunday']),
            (2, 13, ['week-6-monday']),
            (2, 14, ['week-6-tuesday']),
            (2, 15, ['week-6-wednesday']),
            (2, 16, ['week-6-thursday']),
            (2, 17, ['week-6-friday']),
            (2, 18, ['week-6-saturday']),

            (2, 19, ['a/7th-sunday']),
            (2, 20, ['week-7-monday']),
            (2, 21, ['week-7-tuesday']),
            (2, 22, ['week-7-wednesday']),
            (2, 23, ['week-7-thursday']),
            (2, 24, ['week-7-friday']),
            (2, 25, ['week-7-saturday']),

            (2, 26, ['a/8th-sunday']),
            (2, 27, ['week-8-monday']),
            (2, 28, ['week-8-tuesday']),

            # March
            (3, 1, ['lent-week-of-ash-wednesday-ash-wednesday']),
            (3, 2, ['lent-week-of-ash-wednesday-thursday-after-ash-wednesday']),
            (3, 3, ['lent-week-of-ash-wednesday-friday-after-ash-wednesday']),
            (3, 4, ['lent-week-of-ash-wednesday-saturday-after-ash-wednesday']),

            (3, 5, ['a/1st-sunday-of-lent']),
            (3, 6, ['lent-week-1-monday']),
            (3, 7, ['lent-week-1-tuesday']),
            (3, 8, ['lent-week-1-wednesday']),
            (3, 9, ['lent-week-1-thursday']),
            (3, 10, ['lent-week-1-friday']),
            (3, 11, ['lent-week-1-saturday']),

            (3, 12, ['a/2nd-sunday-of-lent']),
            (3, 13, ['lent-week-2-monday']),
            (3, 14, ['lent-week-2-tuesday']),
            (3, 15, ['lent-week-2-wednesday']),
            (3, 16, ['lent-week-2-thursday']),
            (3, 17, ['lent-week-2-friday']),
            (3, 18, ['lent-week-2-saturday']),

            (3, 19, ['a/3rd-sunday-of-lent']),
            # (3, 20, ['lent-week-3-monday']),
            (3, 20, ['joseph-husband-of-mary']),
            (3, 21, ['lent-week-3-tuesday']),
            (3, 22, ['lent-week-3-wednesday']),
            (3, 23, ['lent-week-3-thursday']),
            (3, 24, ['lent-week-3-friday']),
            # (3, 25, ['lent-week-3-saturday']),
            (3, 25, ['annunciation']),

            (3, 26, ['a/4th-sunday-of-lent']),
            (3, 27, ['lent-week-4-monday']),
            (3, 28, ['lent-week-4-tuesday']),
            (3, 29, ['lent-week-4-wednesday']),
            (3, 30, ['lent-week-4-thursday']),
            (3, 31, ['lent-week-4-friday']),

            # April
            (4, 1, ['lent-week-4-saturday']),

            (4, 2, ['a/5th-sunday-of-lent']),
            (4, 3, ['lent-week-5-monday']),
            (4, 4, ['lent-week-5-tuesday']),
            (4, 5, ['lent-week-5-wednesday']),
            (4, 6, ['lent-week-5-thursday']),
            (4, 7, ['lent-week-5-friday']),
            (4, 8, ['lent-week-5-saturday']),

            (4, 9, ['a/palm-sunday']),
            (4, 10, ['lent-holy-week-monday']),
            (4, 11, ['lent-holy-week-tuesday']),
            (4, 12, ['lent-holy-week-wednesday']),
            (4, 13, ['lent-holy-week-thursday-chrism-mass', 'a/mass-of-lords-supper']),

            (4, 16, ['a/easter-sunday']),
            (4, 17, ['easter-octave-monday']),
            (4, 18, ['easter-octave-tuesday']),
            (4, 19, ['easter-octave-wednesday']),
            (4, 20, ['easter-octave-thursday']),
            (4, 21, ['easter-octave-friday']),
            (4, 22, ['easter-octave-saturday']),

            (4, 23, ['a/2nd-sunday-of-easter']),
            (4, 24, ['easter-week-2-monday']),
            (4, 25, ['easter-week-2-tuesday']),
            (4, 26, ['easter-week-2-wednesday']),
            (4, 27, ['easter-week-2-thursday']),
            (4, 28, ['easter-week-2-friday']),
            (4, 29, ['easter-week-2-saturday']),

            (4, 30, ['a/3rd-sunday-of-easter']),

            # May
            (5, 1, ['easter-week-3-monday']),
            (5, 2, ['easter-week-3-tuesday']),
            (5, 3, ['easter-week-3-wednesday']),
            (5, 4, ['easter-week-3-thursday']),
            (5, 5, ['easter-week-3-friday']),
            (5, 6, ['easter-week-3-saturday']),

            (5, 7, ['a/4th-sunday-of-easter']),
            (5, 8, ['easter-week-4-monday']),
            (5, 9, ['easter-week-4-tuesday']),
            (5, 10, ['easter-week-4-wednesday']),
            (5, 11, ['easter-week-4-thursday']),
            (5, 12, ['easter-week-4-friday']),
            (5, 13, ['easter-week-4-saturday']),

            (5, 14, ['a/5th-sunday-of-easter']),
            (5, 15, ['easter-week-5-monday']),
            (5, 16, ['easter-week-5-tuesday']),
            (5, 17, ['easter-week-5-wednesday']),
            (5, 18, ['easter-week-5-thursday']),
            (5, 19, ['easter-week-5-friday']),
            (5, 20, ['easter-week-5-saturday']),

            (5, 21, ['a/6th-sunday-of-easter']),
            (5, 22, ['easter-week-6-monday']),
            (5, 23, ['easter-week-6-tuesday']),
            (5, 24, ['easter-week-6-wednesday']),
            (5, 25, ['easter-week-6-thursday']),
            (5, 26, ['easter-week-6-friday']),
            (5, 27, ['easter-week-6-saturday']),

            (5, 28, ['a/7th-sunday-of-easter']),
            (5, 29, ['easter-week-7-monday']),
            (5, 30, ['easter-week-7-tuesday']),
            (5, 31, ['easter-week-7-wednesday']),

            # June
            (6, 1, ['easter-week-7-thursday']),
            (6, 2, ['easter-week-7-friday']),
            (6, 3, ['easter-week-7-saturday']),

            (6, 4, ['a/pentecost']),
            (6, 11, ['a/trinity-sunday']),
            (6, 18, ['a/corpus-christi']),
            (6, 23, ['john-the-baptist-vigil']),
            (6, 24, ['john-the-baptist']),
            (6, 25, ['a/12th-sunday']),
            (6, 28, ['peter-and-paul-vigil']),
            (6, 29, ['peter-and-paul']),

            # July
            (7, 2, ['a/13th-sunday']),
            (7, 3, ['week-13-monday']),
            (7, 4, ['week-13-tuesday']),
            (7, 5, ['week-13-wednesday']),
            (7, 6, ['week-13-thursday']),
            (7, 7, ['week-13-friday']),
            (7, 8, ['week-13-saturday']),

            (7, 9, ['a/14th-sunday']),
            (7, 10, ['week-14-monday']),
            (7, 11, ['week-14-tuesday']),
            (7, 12, ['week-14-wednesday']),
            (7, 13, ['week-14-thursday']),
            (7, 14, ['week-14-friday']),
            (7, 15, ['week-14-saturday']),

            (7, 16, ['a/15th-sunday']),
            (7, 17, ['week-15-monday']),
            (7, 18, ['week-15-tuesday']),
            (7, 19, ['week-15-wednesday']),
            (7, 20, ['week-15-thursday']),
            (7, 21, ['week-15-friday']),
            (7, 22, ['week-15-saturday']),

            (7, 23, ['a/16th-sunday']),
            (7, 24, ['week-16-monday']),
            (7, 25, ['week-16-tuesday']),
            (7, 26, ['week-16-wednesday']),
            (7, 27, ['week-16-thursday']),
            (7, 28, ['week-16-friday']),
            (7, 29, ['week-16-saturday']),

            (7, 30, ['a/17th-sunday']),
            (7, 31, ['week-17-monday']),

            # August
            (8, 1, ['week-17-tuesday']),
            (8, 2, ['week-17-wednesday']),
            (8, 3, ['week-17-thursday']),
            (8, 4, ['week-17-friday']),
            (8, 5, ['week-17-saturday']),

            (8, 6, ['transfiguration']),
            (8, 7, ['week-18-monday']),
            (8, 8, ['week-18-tuesday']),
            (8, 9, ['week-18-wednesday']),
            (8, 10, ['week-18-thursday']),
            (8, 11, ['week-18-friday']),
            (8, 12, ['week-18-saturday']),

            (8, 13, ['a/19th-sunday']),
            # (8, 14, ['week-19-monday']),
            (8, 14, ['assumption-vigil']),
            # (8, 15, ['week-19-tuesday']),
            (8, 15, ['assumption']),
            (8, 16, ['week-19-wednesday']),
            (8, 17, ['week-19-thursday']),
            (8, 18, ['week-19-friday']),
            (8, 19, ['week-19-saturday']),

            (8, 20, ['a/20th-sunday']),
            (8, 21, ['week-20-monday']),
            (8, 22, ['week-20-tuesday']),
            (8, 23, ['week-20-wednesday']),
            (8, 24, ['week-20-thursday']),
            (8, 25, ['week-20-friday']),
            (8, 26, ['week-20-saturday']),

            (8, 27, ['a/21st-sunday']),
            (8, 28, ['week-21-monday']),
            (8, 29, ['week-21-tuesday']),
            (8, 30, ['week-21-wednesday']),
            (8, 31, ['week-21-thursday']),

            # September
            (9, 1, ['week-21-friday']),
            (9, 2, ['week-21-saturday']),

            (9, 3, ['a/22nd-sunday']),
            (9, 4, ['week-22-monday']),
            (9, 5, ['week-22-tuesday']),
            (9, 6, ['week-22-wednesday']),
            (9, 7, ['week-22-thursday']),
            (9, 8, ['week-22-friday']),
            (9, 9, ['week-22-saturday']),

            (9, 10, ['a/23rd-sunday']),
            (9, 11, ['week-23-monday']),
            (9, 12, ['week-23-tuesday']),
            (9, 13, ['week-23-wednesday']),
            (9, 14, ['triumph-of-the-cross']),
            (9, 15, ['week-23-friday']),
            (9, 16, ['week-23-saturday']),

            (9, 17, ['a/24th-sunday']),
            (9, 18, ['week-24-monday']),
            (9, 19, ['week-24-tuesday']),
            (9, 20, ['week-24-wednesday']),
            (9, 21, ['week-24-thursday']),
            (9, 22, ['week-24-friday']),
            (9, 23, ['week-24-saturday']),

            (9, 24, ['a/25th-sunday']),
            (9, 25, ['week-25-monday']),
            (9, 26, ['week-25-tuesday']),
            (9, 27, ['week-25-wednesday']),
            (9, 28, ['week-25-thursday']),
            (9, 29, ['week-25-friday']),
            (9, 30, ['week-25-saturday']),

            # October
            (10, 1, ['a/26th-sunday']),
            (10, 2, ['week-26-monday']),
            (10, 3, ['week-26-tuesday']),
            (10, 4, ['week-26-wednesday']),
            (10, 5, ['week-26-thursday']),
            (10, 6, ['week-26-friday']),
            (10, 7, ['week-26-saturday']),

            (10, 8, ['a/27th-sunday']),
            (10, 9, ['week-27-monday']),
            (10, 10, ['week-27-tuesday']),
            (10, 11, ['week-27-wednesday']),
            (10, 12, ['week-27-thursday']),
            (10, 13, ['week-27-friday']),
            (10, 14, ['week-27-saturday']),

            (10, 15, ['a/28th-sunday']),
            (10, 16, ['week-28-monday']),
            (10, 17, ['week-28-tuesday']),
            (10, 18, ['week-28-wednesday']),
            (10, 19, ['week-28-thursday']),
            (10, 20, ['week-28-friday']),
            (10, 21, ['week-28-saturday']),

            (10, 22, ['a/29th-sunday']),
            (10, 23, ['week-29-monday']),
            (10, 24, ['week-29-tuesday']),
            (10, 25, ['week-29-wednesday']),
            (10, 26, ['week-29-thursday']),
            (10, 27, ['week-29-friday']),
            (10, 28, ['week-29-saturday']),

            (10, 29, ['a/30th-sunday']),
            (10, 30, ['week-30-monday']),
            (10, 31, ['week-30-tuesday']),

            # November
            (11, 1, ['all-saints']),
            (11, 2, ['all-souls-first-mass', 'all-souls-second-mass', 'all-souls-third-mass']),
            (11, 3, ['week-30-friday']),
            (11, 4, ['week-30-saturday']),

            (11, 5, ['a/31st-sunday']),
            (11, 6, ['week-31-monday']),
            (11, 7, ['week-31-tuesday']),
            (11, 8, ['week-31-wednesday']),
            (11, 9, ['dedication-of-st-john-lateran']),
            (11, 10, ['week-31-friday']),
            (11, 11, ['week-31-saturday']),

            (11, 12, ['a/32nd-sunday']),
            (11, 13, ['week-32-monday']),
            (11, 14, ['week-32-tuesday']),
            (11, 15, ['week-32-wednesday']),
            (11, 16, ['week-32-thursday']),
            (11, 17, ['week-32-friday']),
            (11, 18, ['week-32-saturday']),

            (11, 19, ['a/33rd-sunday']),
            (11, 20, ['week-33-monday']),
            (11, 21, ['week-33-tuesday']),
            (11, 22, ['week-33-wednesday']),
            (11, 23, ['week-33-thursday']),
            (11, 24, ['week-33-friday']),
            (11, 25, ['week-33-saturday']),

            (11, 26, ['a/34th-sunday-christ-the-king']),
            (11, 27, ['week-34-monday']),
            (11, 28, ['week-34-tuesday']),
            (11, 29, ['week-34-wednesday']),
            (11, 30, ['week-34-thursday']),

            # December
            (12, 1, ['week-34-friday']),
            (12, 2, ['week-34-saturday']),

            (12, 3, ['b/1st-sunday-of-advent']),
            (12, 4, ['advent-week-1-monday']),
            (12, 5, ['advent-week-1-tuesday']),
            (12, 6, ['advent-week-1-wednesday']),
            (12, 7, ['advent-week-1-thursday']),
            # (12, 8, ['advent-week-1-friday']),
            (12, 8, ['immaculate-conception']),
            (12, 9, ['advent-week-1-saturday']),

            (12, 10, ['b/2nd-sunday-of-advent']),
            (12, 11, ['advent-week-2-monday']),
            (12, 12, ['advent-week-2-tuesday']),
            (12, 13, ['advent-week-2-wednesday']),
            (12, 14, ['advent-week-2-thursday']),
            (12, 15, ['advent-week-2-friday']),
            (12, 16, ['advent-week-2-saturday']),

            (12, 17, ['b/3rd-sunday-of-advent']),
            # TODO

            (12, 24, ['b/4th-sunday-of-advent', 'b/christmas-vigil']),
            (12, 25, ['b/christmas-at-midnight',
                      'b/christmas-at-dawn',
                      'b/christmas-during-the-day']),
            (12, 26, ['christmas-octave-second-day-st-stephen']),
            (12, 27, ['christmas-octave-third-day-st-john']),
            (12, 28, ['christmas-octave-fourth-day-holy-innocents']),
            (12, 29, ['christmas-octave-fifth-day']),
            (12, 30, ['christmas-octave-sixth-day']),
            # (12, 31, ['christmas-octave-seventh-day']),
            (12, 31, ['b/holy-family']),
            ]

        for month, day, expectedMassIDs in testData:
            try:
                self.assertEqual(
                    expectedMassIDs,
                    [mass.uniqueID for mass in calendar.massesByDate(month, day)])
            except:
                sys.stderr.write(
                    'Failure Case: month=%d day=%d expected=%s\n' % (
                        month, day, expectedMassIDs))
                raise

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

