#!/usr/bin/env python
'''
Tests for :mod:`lectionary`
'''

# Standard imports:
import datetime
import sys
import traceback
import unittest
import xml.dom.minidom

# Local imports:
import lectionary
import citations

class MassTestCase(unittest.TestCase):

    def test_isSundayInOrdinaryTime(self):

        mass = lectionary.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-2'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = lectionary.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-22'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = lectionary.Mass([])
        mass.id = 'sunday-christ-the-king'
        mass.weekid = 'week-34'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = lectionary.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-4'
        mass.seasonid = 'lent'
        self.assertFalse(mass.isSundayInOrdinaryTime)

class LectionaryTestCase(unittest.TestCase):
    '''
    This is not really a unit test for :class:`Lectionary`, but
    something to prove that we can parse all the citations that appear
    in our XML representation of the lectionaries and that we find the
    right number of them.
    '''

    def test_parseSundayCitations(self):
        '''
        Prove that the number of readings we find in the Sunday
        Lectionary by invoking ``grep`` on the XML equals the number
        of readings we find in our object representation of the Sunday
        Lectionary.  Furthermore, prove that we can parse every one of
        the citations.
        '''

        readingCount = 0
        for mass in lectionary._lectionary.allSundayMasses:
            for reading in mass.allReadings:
                readingCount += 1
                citations.parse(reading.citation)

        # $ grep --count /reading sunday-lectionary.xml
        self.assertEqual(565, readingCount)

    def test_parseWeekdayCitations(self):
        readingCount = 0
        for mass in lectionary._lectionary._allWeekdayMasses:
            for reading in mass.allReadings:
                readingCount += 1
                # TODO: Here is one we cannot parse yet!
                if reading.citation == 'Est C:12,14-16,23-25':
                    continue
                citations.parse(reading.citation)

        # $ grep --count /reading weekday-lectionary.xml
        self.assertEqual(863, readingCount)

    def test_parseSpecialCitations(self):
        readingCount = 0
        for mass in lectionary._lectionary._allSpecialMasses:
            for reading in mass.allReadings:
                readingCount += 1
                citations.parse(reading.citation)

        # $ grep --count /reading special-lectionary.xml
        self.assertEqual(54, readingCount)

    def test_weekdayMassesInWeek(self):
        lectionary._lectionary.weekdayMassesInWeek(None, 'week-1')

class decodeMassTestCase(unittest.TestCase):

    @staticmethod
    def citations(readings):
        '''
        Convert a list of :class:`Reading` objects to its citation
        strings.
        '''

        return [reading.citation for reading in readings]

    def test_christmasAtMidnight(self):
        '''
        Prove that we can decode the pattern exemplified by Christmass
        At Midnight.

        Notice this mass has three readings that do not change with
        the Sunday cycle and there are no options.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass name="Christmas (At Midnight)">
  <reading>Is 9:1-6</reading>
  <reading>Ti 2:11-14</reading>
  <reading>Lk 2:1-14</reading>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Christmas (At Midnight)', mass.name)
        self.assertEqual('christmas-at-midnight', mass.id)
        self.assertEqual(3, len(mass.allReadings))

        for sundayCycle in ('A', 'B', 'C'):
            for weekdayCycle in ('I', 'II'):
                self.assertEqual(
                    ['Is 9:1-6', 'Ti 2:11-14', 'Lk 2:1-14'],
                    self.citations(
                        mass.applicableReadings(sundayCycle, weekdayCycle)))

    def test_firstSundayOfAdvent(self):
        '''
        Prove that we can decode the pattern exemplified by the 1st
        Sunday of Advent.

        Notice this mass has three variations, one for each Sunday
        cycle, and no options.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass weekid="week-1" id="sunday" name="1st Sunday of Advent">
  <variation cycles="A">
    <reading>Is 2:1-5</reading>
    <reading>Rom 13:11-14</reading>
    <reading>Mt 24:37-44</reading>
  </variation>
  <variation cycles="B">
    <reading>Is 63:16b-17,19b,64:2b-7</reading>
    <reading>1 Cor 1:3-9</reading>
    <reading>Mk 13:33-37</reading>
  </variation>
  <variation cycles="C">
    <reading>Jer 33:14-16</reading>
    <reading>1 Thes 3:12-4:2</reading>
    <reading>Lk 21:25-28,34-36</reading>
  </variation>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('1st Sunday of Advent', mass.name)
        self.assertEqual('sunday', mass.id)
        self.assertEqual('week-1', mass.weekid)
        self.assertEqual(9, len(mass.allReadings))

        for weekdayCycle in ('I', 'II'):
            self.assertEqual(
                ['Is 2:1-5', 'Rom 13:11-14', 'Mt 24:37-44'],
                self.citations(mass.applicableReadings('A', weekdayCycle)))
            self.assertEqual(
                ['Is 63:16b-17,19b,64:2b-7', '1 Cor 1:3-9', 'Mk 13:33-37'],
                self.citations(mass.applicableReadings('B', weekdayCycle)))
            self.assertEqual(
                ['Jer 33:14-16', '1 Thes 3:12-4:2', 'Lk 21:25-28,34-36'],
                self.citations(mass.applicableReadings('C', weekdayCycle)))

    def test_holyFamily(self):
        '''
        Prove that we can decode the pattern exemplified by Holy
        Family.

        Notice this mass has the typical cycle variations, with the
        added complexity of options in cycle B.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass name="Holy Family">
  <variation cycles="A">
    <reading>Sir 3:3-7,14-17a</reading>
    <reading>Col 3:12-21</reading>
    <reading>Mt 2:13-15,19-23</reading>
  </variation>
  <variation cycles="B">
    <reading>Gn 15:1-6,21:1-3</reading>
    <reading>Heb 11:8,11-12,17-19</reading>
    <option>
      <reading>Lk 2:22-40</reading>
      <reading>Lk 2:22,39-40</reading>
    </option>
  </variation>
  <variation cycles="C">
    <reading>1 Sm 1:20-22,24-28</reading>
    <reading>1 Jn 3:1-2,21-24</reading>
    <reading>Lk 2:41-52</reading>
  </variation>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Holy Family', mass.name)
        self.assertEqual('holy-family', mass.id)
        self.assertEqual(10, len(mass.allReadings))

        for weekdayCycle in ('I', 'II'):
            self.assertEqual(
                ['Sir 3:3-7,14-17a', 'Col 3:12-21', 'Mt 2:13-15,19-23'],
                self.citations(mass.applicableReadings('A', weekdayCycle)))
            self.assertEqual(
                ['Gn 15:1-6,21:1-3',
                 'Heb 11:8,11-12,17-19',
                 'Lk 2:22-40',
                 'Lk 2:22,39-40'],
                self.citations(mass.applicableReadings('B', weekdayCycle)))
            self.assertEqual(
                ['1 Sm 1:20-22,24-28', '1 Jn 3:1-2,21-24', 'Lk 2:41-52'],
                self.citations(mass.applicableReadings('C', weekdayCycle)))

    def test_easterSunday(self):
        '''
        Prove that we can decode the pattern exemplified by Easter
        Sunday.

        Notice that the first reading does not vary, the second
        reading has cycle-independent options, and the third reading
        is one of three different sets of options that depend upon the
        cycle.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass weekid="week-1" id="sunday" name="Easter Sunday">
  <reading>Acts 10:34a,37-43</reading>
  <variation>
    <reading>Col 3:1-4</reading>
    <reading>1 Cor 5:6b-8</reading>
  </variation>
  <variation cycles="A">
    <option>
      <reading>Jn 20:1-9</reading>
      <reading>Mt 28:1-10</reading>
      <reading>Lk 24:13-35</reading>
    </option>
  </variation>
  <variation cycles="B">
    <option>
      <reading>Jn 20:1-8</reading>
      <reading>Mk 16:1-8</reading>
      <reading>Lk 24:13-35</reading>
    </option>
  </variation>
  <variation cycles="C">
    <option>
      <reading>Jn 20:1-9</reading>
      <reading>Lk 24:1-12</reading>
      <reading>Lk 24:13-35</reading>
    </option>
  </variation>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Easter Sunday', mass.name)
        self.assertEqual(12, len(mass.allReadings))

        for weekdayCycle in ('I', 'II'):
            self.assertEqual(
                ['Acts 10:34a,37-43',
                 'Col 3:1-4',
                 '1 Cor 5:6b-8',
                 'Jn 20:1-9',
                 'Mt 28:1-10',
                 'Lk 24:13-35'],
                self.citations(mass.applicableReadings('A', weekdayCycle)))
            self.assertEqual(
                ['Acts 10:34a,37-43',
                 'Col 3:1-4',
                 '1 Cor 5:6b-8',
                 'Jn 20:1-8',
                 'Mk 16:1-8',
                 'Lk 24:13-35'],
                self.citations(mass.applicableReadings('B', weekdayCycle)))
            self.assertEqual(
                ['Acts 10:34a,37-43',
                 'Col 3:1-4',
                 '1 Cor 5:6b-8',
                 'Jn 20:1-9',
                 'Lk 24:1-12',
                 'Lk 24:13-35'],
                self.citations(mass.applicableReadings('C', weekdayCycle)))

    def test_mondayInTheFirstWeekOfOrdinaryTime(self):
        '''
        Prove that we can decode the pattern exemplified by the Monday
        in the 1st Week of Ordinary Time.

        Notice that the first reading varies with the weekday cycle
        while the second reading never changes.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass name="Monday">
  <reading cycles="I">Heb 1:1-6</reading>
  <reading cycles="II">1 Sm 1:1-8</reading>
  <reading>Mk 1:14-20</reading>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Monday', mass.name)

        for sundayCycle in ('A', 'B', 'C'):
            self.assertEqual(
                ['Heb 1:1-6', 'Mk 1:14-20'],
                self.citations(mass.applicableReadings(sundayCycle, 'I')))
            self.assertEqual(
                ['1 Sm 1:1-8', 'Mk 1:14-20'],
                self.citations(mass.applicableReadings(sundayCycle, 'II')))

    def test_mondayInTheFirstWeekOfAdvent(self):
        '''
        Prove that we can decode the pattern exemplified by Monday in
        the 1st Week of Advent.

        Notice that the first reading actually depends upon the Sunday
        cycle.  The second reading does not change.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
<mass name="Monday">
  <reading cycles="A">Is 4:2-6</reading>
  <reading cycles="BC">Is 2:1-5</reading>
  <reading>Mt 8:5-11</reading>
</mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Monday', mass.name)

        for weekdayCycle in ('I', 'II'):
            self.assertEqual(
                ['Is 4:2-6', 'Mt 8:5-11'],
                self.citations(mass.applicableReadings('A', weekdayCycle)))
            self.assertEqual(
                ['Is 2:1-5', 'Mt 8:5-11'],
                self.citations(mass.applicableReadings('B', weekdayCycle)))
            self.assertEqual(
                ['Is 2:1-5', 'Mt 8:5-11'],
                self.citations(mass.applicableReadings('C', weekdayCycle)))

    def test_mondayInTheFifthWeekOfLent(self):
        '''
        Prove that we can decode the pattern exemplified by Monday in
        the 5th Week of Lent.

        Notice that the second reading actually depends upon the
        Sunday cycle.  The first reading does not change.
        '''

        doc = xml.dom.minidom.parseString('''\
<?xml version="1.0"?>
  <mass name="Monday">
    <reading>Dn 13:1-9,15-17,19-30,33-62</reading>
    <reading cycles="AB">Jn 8:1-11</reading>
    <reading cycles="C">Jn 8:12-20</reading>
  </mass>
''')
        mass = lectionary._decode_mass(doc.documentElement)
        self.assertEqual('Monday', mass.name)

        for weekdayCycle in ('I', 'II'):
            self.assertEqual(
                ['Dn 13:1-9,15-17,19-30,33-62', 'Jn 8:1-11'],
                self.citations(mass.applicableReadings('A', weekdayCycle)))
            self.assertEqual(
                ['Dn 13:1-9,15-17,19-30,33-62', 'Jn 8:1-11'],
                self.citations(mass.applicableReadings('B', weekdayCycle)))
            self.assertEqual(
                ['Dn 13:1-9,15-17,19-30,33-62', 'Jn 8:12-20'],
                self.citations(mass.applicableReadings('C', weekdayCycle)))

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
            (1, 1, ['christmas/mary-mother-of-god']),  # FIXME
            (1, 2, ['01-02']),
            (1, 3, ['01-03']),
            (1, 4, ['01-04']),
            (1, 5, ['01-05']),
            (1, 6, ['01-06']),
            (1, 7, ['01-07']),

            (1, 8, ['christmas/epiphany']),
            (1, 9, ['christmas/baptism-of-the-lord']),
            (1, 10, ['ordinary/week-1/tuesday']),
            (1, 11, ['ordinary/week-1/wednesday']),
            (1, 12, ['ordinary/week-1/thursday']),
            (1, 13, ['ordinary/week-1/friday']),
            (1, 14, ['ordinary/week-1/saturday']),

            (1, 15, ['ordinary/week-2/sunday']),
            (1, 16, ['ordinary/week-2/monday']),
            (1, 17, ['ordinary/week-2/tuesday']),
            (1, 18, ['ordinary/week-2/wednesday']),
            (1, 19, ['ordinary/week-2/thursday']),
            (1, 20, ['ordinary/week-2/friday']),
            (1, 21, ['ordinary/week-2/saturday']),

            (1, 22, ['ordinary/week-3/sunday']),
            (1, 23, ['ordinary/week-3/monday']),
            (1, 24, ['ordinary/week-3/tuesday']),
            (1, 25, ['ordinary/week-3/wednesday']),
            (1, 26, ['ordinary/week-3/thursday']),
            (1, 27, ['ordinary/week-3/friday']),
            (1, 28, ['ordinary/week-3/saturday']),

            (1, 29, ['ordinary/week-4/sunday']),
            (1, 30, ['ordinary/week-4/monday']),
            (1, 31, ['ordinary/week-4/tuesday']),

            # February
            (2, 1, ['ordinary/week-4/wednesday']),
            (2, 2, ['presentation-of-the-lord']),
            (2, 3, ['ordinary/week-4/friday']),
            (2, 4, ['ordinary/week-4/saturday']),

            (2, 5, ['ordinary/week-5/sunday']),
            (2, 6, ['ordinary/week-5/monday']),
            (2, 7, ['ordinary/week-5/tuesday']),
            (2, 8, ['ordinary/week-5/wednesday']),
            (2, 9, ['ordinary/week-5/thursday']),
            (2, 10, ['ordinary/week-5/friday']),
            (2, 11, ['ordinary/week-5/saturday']),

            (2, 12, ['ordinary/week-6/sunday']),
            (2, 13, ['ordinary/week-6/monday']),
            (2, 14, ['ordinary/week-6/tuesday']),
            (2, 15, ['ordinary/week-6/wednesday']),
            (2, 16, ['ordinary/week-6/thursday']),
            (2, 17, ['ordinary/week-6/friday']),
            (2, 18, ['ordinary/week-6/saturday']),

            (2, 19, ['ordinary/week-7/sunday']),
            (2, 20, ['ordinary/week-7/monday']),
            (2, 21, ['ordinary/week-7/tuesday']),
            (2, 22, ['ordinary/week-7/wednesday']),
            (2, 23, ['ordinary/week-7/thursday']),
            (2, 24, ['ordinary/week-7/friday']),
            (2, 25, ['ordinary/week-7/saturday']),

            (2, 26, ['ordinary/week-8/sunday']),
            (2, 27, ['ordinary/week-8/monday']),
            (2, 28, ['ordinary/week-8/tuesday']),

            # March
            (3, 1, ['lent/week-of-ash-wednesday/ash-wednesday']),
            (3, 2, ['lent/week-of-ash-wednesday/thursday']),
            (3, 3, ['lent/week-of-ash-wednesday/friday']),
            (3, 4, ['lent/week-of-ash-wednesday/saturday']),

            (3, 5, ['lent/week-1/sunday']),
            (3, 6, ['lent/week-1/monday']),
            (3, 7, ['lent/week-1/tuesday']),
            (3, 8, ['lent/week-1/wednesday']),
            (3, 9, ['lent/week-1/thursday']),
            (3, 10, ['lent/week-1/friday']),
            (3, 11, ['lent/week-1/saturday']),

            (3, 12, ['lent/week-2/sunday']),
            (3, 13, ['lent/week-2/monday']),
            (3, 14, ['lent/week-2/tuesday']),
            (3, 15, ['lent/week-2/wednesday']),
            (3, 16, ['lent/week-2/thursday']),
            (3, 17, ['lent/week-2/friday']),
            (3, 18, ['lent/week-2/saturday']),

            (3, 19, ['lent/week-3/sunday']),
            # (3, 20, ['lent/week-3/monday']),
            (3, 20, ['joseph-husband-of-mary']),
            (3, 21, ['lent/week-3/tuesday']),
            (3, 22, ['lent/week-3/wednesday']),
            (3, 23, ['lent/week-3/thursday']),
            (3, 24, ['lent/week-3/friday']),
            # (3, 25, ['lent/week-3/saturday']),
            (3, 25, ['annunciation']),

            (3, 26, ['lent/week-4/sunday']),
            (3, 27, ['lent/week-4/monday']),
            (3, 28, ['lent/week-4/tuesday']),
            (3, 29, ['lent/week-4/wednesday']),
            (3, 30, ['lent/week-4/thursday']),
            (3, 31, ['lent/week-4/friday']),

            # April
            (4, 1, ['lent/week-4/saturday']),

            (4, 2, ['lent/week-5/sunday']),
            (4, 3, ['lent/week-5/monday']),
            (4, 4, ['lent/week-5/tuesday']),
            (4, 5, ['lent/week-5/wednesday']),
            (4, 6, ['lent/week-5/thursday']),
            (4, 7, ['lent/week-5/friday']),
            (4, 8, ['lent/week-5/saturday']),

            (4, 9, ['holy-week/palm-sunday']),
            (4, 10, ['holy-week/monday']),
            (4, 11, ['holy-week/tuesday']),
            (4, 12, ['holy-week/wednesday']),
            (4, 13, ['holy-week/thursday-chrism-mass',
                     'holy-week/mass-of-the-lords-supper']),
            (4, 14, ['holy-week/good-friday']),
            (4, 15, ['easter/easter-vigil']),

            (4, 16, ['easter/week-1/sunday']),
            (4, 17, ['easter/week-1/monday']),
            (4, 18, ['easter/week-1/tuesday']),
            (4, 19, ['easter/week-1/wednesday']),
            (4, 20, ['easter/week-1/thursday']),
            (4, 21, ['easter/week-1/friday']),
            (4, 22, ['easter/week-1/saturday']),

            (4, 23, ['easter/week-2/sunday']),
            (4, 24, ['easter/week-2/monday']),
            (4, 25, ['easter/week-2/tuesday']),
            (4, 26, ['easter/week-2/wednesday']),
            (4, 27, ['easter/week-2/thursday']),
            (4, 28, ['easter/week-2/friday']),
            (4, 29, ['easter/week-2/saturday']),

            (4, 30, ['easter/week-3/sunday']),

            # May
            (5, 1, ['easter/week-3/monday']),
            (5, 2, ['easter/week-3/tuesday']),
            (5, 3, ['easter/week-3/wednesday']),
            (5, 4, ['easter/week-3/thursday']),
            (5, 5, ['easter/week-3/friday']),
            (5, 6, ['easter/week-3/saturday']),

            (5, 7, ['easter/week-4/sunday']),
            (5, 8, ['easter/week-4/monday']),
            (5, 9, ['easter/week-4/tuesday']),
            (5, 10, ['easter/week-4/wednesday']),
            (5, 11, ['easter/week-4/thursday']),
            (5, 12, ['easter/week-4/friday']),
            (5, 13, ['easter/week-4/saturday']),

            (5, 14, ['easter/week-5/sunday']),
            (5, 15, ['easter/week-5/monday']),
            (5, 16, ['easter/week-5/tuesday']),
            (5, 17, ['easter/week-5/wednesday']),
            (5, 18, ['easter/week-5/thursday']),
            (5, 19, ['easter/week-5/friday']),
            (5, 20, ['easter/week-5/saturday']),

            (5, 21, ['easter/week-6/sunday']),
            (5, 22, ['easter/week-6/monday']),
            (5, 23, ['easter/week-6/tuesday']),
            (5, 24, ['easter/week-6/wednesday']),
            (5, 25, ['easter/week-6/thursday']),
            (5, 26, ['easter/week-6/friday']),
            (5, 27, ['easter/week-6/saturday']),

            (5, 28, ['easter/week-7/sunday']),
            (5, 29, ['easter/week-7/monday']),
            (5, 30, ['easter/week-7/tuesday']),
            (5, 31, ['easter/week-7/wednesday']),

            # June
            (6, 1, ['easter/week-7/thursday']),
            (6, 2, ['easter/week-7/friday']),
            (6, 3, ['easter/week-7/saturday', 'easter/pentecost-vigil']),

            (6, 4, ['easter/pentecost']),
            (6, 5, ['ordinary/week-9/monday']),
            (6, 6, ['ordinary/week-9/tuesday']),
            (6, 7, ['ordinary/week-9/wednesday']),
            (6, 8, ['ordinary/week-9/thursday']),
            (6, 9, ['ordinary/week-9/friday']),
            (6, 10, ['ordinary/week-9/saturday']),

            (6, 11, ['ordinary/trinity-sunday']),  # FIXME
            (6, 12, ['ordinary/week-10/monday']),
            (6, 13, ['ordinary/week-10/tuesday']),
            (6, 14, ['ordinary/week-10/wednesday']),
            (6, 15, ['ordinary/week-10/thursday']),
            (6, 16, ['ordinary/week-10/friday']),
            (6, 17, ['ordinary/week-10/saturday']),

            (6, 18, ['ordinary/corpus-christi']),  # FIXME
            (6, 19, ['ordinary/week-11/monday']),
            (6, 20, ['ordinary/week-11/tuesday']),
            (6, 21, ['ordinary/week-11/wednesday']),
            (6, 22, ['ordinary/week-11/thursday']),
            (6, 23, ['john-the-baptist-vigil']),
            (6, 24, ['john-the-baptist']),

            (6, 25, ['ordinary/week-12/sunday']),
            (6, 26, ['ordinary/week-12/monday']),
            (6, 27, ['ordinary/week-12/tuesday']),
            (6, 28, ['peter-and-paul-vigil']),
            (6, 29, ['peter-and-paul']),
            (6, 30, ['ordinary/week-12/friday']),

            # July
            (7, 1, ['ordinary/week-12/saturday']),

            (7, 2, ['ordinary/week-13/sunday']),
            (7, 3, ['ordinary/week-13/monday']),
            (7, 4, ['ordinary/week-13/tuesday']),
            (7, 5, ['ordinary/week-13/wednesday']),
            (7, 6, ['ordinary/week-13/thursday']),
            (7, 7, ['ordinary/week-13/friday']),
            (7, 8, ['ordinary/week-13/saturday']),

            (7, 9, ['ordinary/week-14/sunday']),
            (7, 10, ['ordinary/week-14/monday']),
            (7, 11, ['ordinary/week-14/tuesday']),
            (7, 12, ['ordinary/week-14/wednesday']),
            (7, 13, ['ordinary/week-14/thursday']),
            (7, 14, ['ordinary/week-14/friday']),
            (7, 15, ['ordinary/week-14/saturday']),

            (7, 16, ['ordinary/week-15/sunday']),
            (7, 17, ['ordinary/week-15/monday']),
            (7, 18, ['ordinary/week-15/tuesday']),
            (7, 19, ['ordinary/week-15/wednesday']),
            (7, 20, ['ordinary/week-15/thursday']),
            (7, 21, ['ordinary/week-15/friday']),
            (7, 22, ['ordinary/week-15/saturday']),

            (7, 23, ['ordinary/week-16/sunday']),
            (7, 24, ['ordinary/week-16/monday']),
            (7, 25, ['ordinary/week-16/tuesday']),
            (7, 26, ['ordinary/week-16/wednesday']),
            (7, 27, ['ordinary/week-16/thursday']),
            (7, 28, ['ordinary/week-16/friday']),
            (7, 29, ['ordinary/week-16/saturday']),

            (7, 30, ['ordinary/week-17/sunday']),
            (7, 31, ['ordinary/week-17/monday']),

            # August
            (8, 1, ['ordinary/week-17/tuesday']),
            (8, 2, ['ordinary/week-17/wednesday']),
            (8, 3, ['ordinary/week-17/thursday']),
            (8, 4, ['ordinary/week-17/friday']),
            (8, 5, ['ordinary/week-17/saturday']),

            (8, 6, ['transfiguration']),
            (8, 7, ['ordinary/week-18/monday']),
            (8, 8, ['ordinary/week-18/tuesday']),
            (8, 9, ['ordinary/week-18/wednesday']),
            (8, 10, ['ordinary/week-18/thursday']),
            (8, 11, ['ordinary/week-18/friday']),
            (8, 12, ['ordinary/week-18/saturday']),

            (8, 13, ['ordinary/week-19/sunday']),
            # (8, 14, ['ordinary/week-19/monday']),
            (8, 14, ['assumption-vigil']),
            # (8, 15, ['ordinary/week-19/tuesday']),
            (8, 15, ['assumption']),
            (8, 16, ['ordinary/week-19/wednesday']),
            (8, 17, ['ordinary/week-19/thursday']),
            (8, 18, ['ordinary/week-19/friday']),
            (8, 19, ['ordinary/week-19/saturday']),

            (8, 20, ['ordinary/week-20/sunday']),
            (8, 21, ['ordinary/week-20/monday']),
            (8, 22, ['ordinary/week-20/tuesday']),
            (8, 23, ['ordinary/week-20/wednesday']),
            (8, 24, ['ordinary/week-20/thursday']),
            (8, 25, ['ordinary/week-20/friday']),
            (8, 26, ['ordinary/week-20/saturday']),

            (8, 27, ['ordinary/week-21/sunday']),
            (8, 28, ['ordinary/week-21/monday']),
            (8, 29, ['ordinary/week-21/tuesday']),
            (8, 30, ['ordinary/week-21/wednesday']),
            (8, 31, ['ordinary/week-21/thursday']),

            # September
            (9, 1, ['ordinary/week-21/friday']),
            (9, 2, ['ordinary/week-21/saturday']),

            (9, 3, ['ordinary/week-22/sunday']),
            (9, 4, ['ordinary/week-22/monday']),
            (9, 5, ['ordinary/week-22/tuesday']),
            (9, 6, ['ordinary/week-22/wednesday']),
            (9, 7, ['ordinary/week-22/thursday']),
            (9, 8, ['ordinary/week-22/friday']),
            (9, 9, ['ordinary/week-22/saturday']),

            (9, 10, ['ordinary/week-23/sunday']),
            (9, 11, ['ordinary/week-23/monday']),
            (9, 12, ['ordinary/week-23/tuesday']),
            (9, 13, ['ordinary/week-23/wednesday']),
            (9, 14, ['triumph-of-the-cross']),
            (9, 15, ['ordinary/week-23/friday']),
            (9, 16, ['ordinary/week-23/saturday']),

            (9, 17, ['ordinary/week-24/sunday']),
            (9, 18, ['ordinary/week-24/monday']),
            (9, 19, ['ordinary/week-24/tuesday']),
            (9, 20, ['ordinary/week-24/wednesday']),
            (9, 21, ['ordinary/week-24/thursday']),
            (9, 22, ['ordinary/week-24/friday']),
            (9, 23, ['ordinary/week-24/saturday']),

            (9, 24, ['ordinary/week-25/sunday']),
            (9, 25, ['ordinary/week-25/monday']),
            (9, 26, ['ordinary/week-25/tuesday']),
            (9, 27, ['ordinary/week-25/wednesday']),
            (9, 28, ['ordinary/week-25/thursday']),
            (9, 29, ['ordinary/week-25/friday']),
            (9, 30, ['ordinary/week-25/saturday']),

            # October
            (10, 1, ['ordinary/week-26/sunday']),
            (10, 2, ['ordinary/week-26/monday']),
            (10, 3, ['ordinary/week-26/tuesday']),
            (10, 4, ['ordinary/week-26/wednesday']),
            (10, 5, ['ordinary/week-26/thursday']),
            (10, 6, ['ordinary/week-26/friday']),
            (10, 7, ['ordinary/week-26/saturday']),

            (10, 8, ['ordinary/week-27/sunday']),
            (10, 9, ['ordinary/week-27/monday']),
            (10, 10, ['ordinary/week-27/tuesday']),
            (10, 11, ['ordinary/week-27/wednesday']),
            (10, 12, ['ordinary/week-27/thursday']),
            (10, 13, ['ordinary/week-27/friday']),
            (10, 14, ['ordinary/week-27/saturday']),

            (10, 15, ['ordinary/week-28/sunday']),
            (10, 16, ['ordinary/week-28/monday']),
            (10, 17, ['ordinary/week-28/tuesday']),
            (10, 18, ['ordinary/week-28/wednesday']),
            (10, 19, ['ordinary/week-28/thursday']),
            (10, 20, ['ordinary/week-28/friday']),
            (10, 21, ['ordinary/week-28/saturday']),

            (10, 22, ['ordinary/week-29/sunday']),
            (10, 23, ['ordinary/week-29/monday']),
            (10, 24, ['ordinary/week-29/tuesday']),
            (10, 25, ['ordinary/week-29/wednesday']),
            (10, 26, ['ordinary/week-29/thursday']),
            (10, 27, ['ordinary/week-29/friday']),
            (10, 28, ['ordinary/week-29/saturday']),

            (10, 29, ['ordinary/week-30/sunday']),
            (10, 30, ['ordinary/week-30/monday']),
            (10, 31, ['ordinary/week-30/tuesday']),

            # November
            (11, 1, ['all-saints']),
            (11, 2, ['all-souls-1',
                     'all-souls-2',
                     'all-souls-3']),
            (11, 3, ['ordinary/week-30/friday']),
            (11, 4, ['ordinary/week-30/saturday']),

            (11, 5, ['ordinary/week-31/sunday']),
            (11, 6, ['ordinary/week-31/monday']),
            (11, 7, ['ordinary/week-31/tuesday']),
            (11, 8, ['ordinary/week-31/wednesday']),
            (11, 9, ['dedication-of-st-john-lateran']),
            (11, 10, ['ordinary/week-31/friday']),
            (11, 11, ['ordinary/week-31/saturday']),

            (11, 12, ['ordinary/week-32/sunday']),
            (11, 13, ['ordinary/week-32/monday']),
            (11, 14, ['ordinary/week-32/tuesday']),
            (11, 15, ['ordinary/week-32/wednesday']),
            (11, 16, ['ordinary/week-32/thursday']),
            (11, 17, ['ordinary/week-32/friday']),
            (11, 18, ['ordinary/week-32/saturday']),

            (11, 19, ['ordinary/week-33/sunday']),
            (11, 20, ['ordinary/week-33/monday']),
            (11, 21, ['ordinary/week-33/tuesday']),
            (11, 22, ['ordinary/week-33/wednesday']),
            (11, 23, ['ordinary/week-33/thursday']),
            (11, 24, ['ordinary/week-33/friday']),
            (11, 25, ['ordinary/week-33/saturday']),

            (11, 26, ['ordinary/week-34/sunday-christ-the-king']),
            (11, 27, ['ordinary/week-34/monday']),
            (11, 28, ['ordinary/week-34/tuesday']),
            (11, 29, ['ordinary/week-34/wednesday']),
            (11, 30, ['ordinary/week-34/thursday']),

            # December
            (12, 1, ['ordinary/week-34/friday']),
            (12, 2, ['ordinary/week-34/saturday']),

            (12, 3, ['advent/week-1/sunday']),
            (12, 4, ['advent/week-1/monday']),
            (12, 5, ['advent/week-1/tuesday']),
            (12, 6, ['advent/week-1/wednesday']),
            (12, 7, ['advent/week-1/thursday']),
            # (12, 8, ['advent/week-1/friday']),
            (12, 8, ['immaculate-conception']),
            (12, 9, ['advent/week-1/saturday']),

            (12, 10, ['advent/week-2/sunday']),
            (12, 11, ['advent/week-2/monday']),
            (12, 12, ['advent/week-2/tuesday']),
            (12, 13, ['advent/week-2/wednesday']),
            (12, 14, ['advent/week-2/thursday']),
            (12, 15, ['advent/week-2/friday']),
            (12, 16, ['advent/week-2/saturday']),

            (12, 17, ['advent/week-3/sunday']),
            (12, 18, ['12-18']),
            (12, 19, ['12-19']),
            (12, 20, ['12-20']),
            (12, 21, ['12-21']),
            (12, 22, ['12-22']),
            (12, 23, ['12-23']),

            (12, 24, ['advent/week-4/sunday', 'christmas/christmas-vigil']),
            (12, 25, ['christmas/christmas-at-midnight',
                      'christmas/christmas-at-dawn',
                      'christmas/christmas-during-the-day']),
            (12, 26, ['christmas/day-2-st-stephen']),
            (12, 27, ['christmas/day-3-st-john']),
            (12, 28, ['christmas/day-4-holy-innocents']),
            (12, 29, ['christmas/day-5']),
            (12, 30, ['christmas/day-6']),
            # (12, 31, ['christmas/day-7']),
            (12, 31, ['christmas/holy-family']),
            ]

        for month, day, expectedMassIDs in testData:
            try:
                self.assertEqual(
                    expectedMassIDs,
                    [mass.fqid for mass in calendar.massesByDate(month, day)])
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

    def test_tooManySharps(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('##')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('###')

    def test_missingID(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('#')

    def test_badYear(self):
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('#d')
        with self.assertRaises(lectionary.MalformedQueryError):
            lectionary.parse('#abc')

class getReadingsTestCase(unittest.TestCase):

    def test_zeroResults(self):
        '''
        There is no mass with the substing 'bananas' in its name.
        Prove that this request rasies ``NonSingularResultsError``.
        '''

        with self.assertRaises(lectionary.NonSingularResultsError):
            lectionary.getReadings('bananas')

    def test_multipleResults(self):
        '''
        There are multiple masses with the letter 'i' in their names.
        Prove that this request raises ``NonSingularResultsError``.
        '''

        with self.assertRaises(lectionary.NonSingularResultsError):
            lectionary.getReadings('i')

    def test_easterVigil(self):
        '''
        There are 11 unique readings in the lectionary for the Easter
        Vigil.  Prove that we find exactly that many and all the right
        ones.
        '''

        massTitle, readings = lectionary.getReadings('easter-vigil#')
        self.assertEqual('Easter Vigil (All Cycles)', massTitle)
        self.assertEqual(11, len(readings))

        citations = [
            reading.citation
            for reading in readings.iterkeys()
            ]
        self.assertIn('Gn 1:1-2:2', citations)
        self.assertIn('Gn 22:1-18', citations)
        self.assertIn('Ex 14:15-15:1', citations)
        self.assertIn('Is 54:5-14', citations)
        self.assertIn('Is 55:1-11', citations)
        self.assertIn('Bar 3:9-15,32-4:4', citations)
        self.assertIn('Ez 36:16-28', citations)
        self.assertIn('Rom 6:3-11', citations)
        self.assertIn('Mt 28:1-10', citations)
        self.assertIn('Mk 16:1-7', citations)
        self.assertIn('Lk 24:1-12', citations)

class parseDateTestCase(unittest.TestCase):

    def test_nonString(self):
        with self.assertRaises(TypeError):
            lectionary._parseDate(None)
        with self.assertRaises(TypeError):
            lectionary._parseDate(123)
        with self.assertRaises(TypeError):
            lectionary._parseDate(0.123)

    def test_emptyString(self):
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('')

    def test_tooManySubtokens(self):
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('2017-10-17-01')

    def test_malformedSubtokens(self):
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('banana-10-17')
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('2017-banana-17')
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('2017-10-banana')

    def test_missingSubtokens(self):
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('-10-17')
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('2017--17')
        with self.assertRaises(lectionary.MalformedDateError):
            lectionary._parseDate('2017-10-')

    def test_invalidYear(self):
        with self.assertRaises(lectionary.InvalidDateError):
            lectionary._parseDate('0-10-17')

    def test_invalidMonth(self):
        with self.assertRaises(lectionary.InvalidDateError):
            lectionary._parseDate('2017-0-17')
        with self.assertRaises(lectionary.InvalidDateError):
            lectionary._parseDate('2017-13-17')

    def test_invalidDay(self):
        with self.assertRaises(lectionary.InvalidDateError):
            lectionary._parseDate('2017-13-0')
        with self.assertRaises(lectionary.InvalidDateError):
            lectionary._parseDate('2017-13-99')

    def test_today(self):
        today = datetime.date.today()
        result = lectionary._parseDate('today')
        self.assertEqual(today.year, result.year)
        self.assertEqual(today.month, result.month)
        self.assertEqual(today.day, result.day)

    def test_yearMonthDay(self):
        today = datetime.date.today()
        result = lectionary._parseDate('2017-10-17')
        self.assertEqual(2017, result.year)
        self.assertEqual(10, result.month)
        self.assertEqual(17, result.day)

    def test_monthDay(self):
        today = datetime.date.today()
        result = lectionary._parseDate('10-17')
        self.assertEqual(today.year, result.year)
        self.assertEqual(10, result.month)
        self.assertEqual(17, result.day)

    def test_day(self):
        today = datetime.date.today()
        result = lectionary._parseDate('17')
        self.assertEqual(today.year, result.year)
        self.assertEqual(today.month, result.month)
        self.assertEqual(17, result.day)

if __name__ == '__main__':
    unittest.main()

