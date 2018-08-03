#!/usr/bin/env python
'''
Tests for :mod:`masses`
'''

# Standard imports:
import unittest
import xml.dom.minidom

# Local imports:
import masses

class XMLDecoderTestCase(unittest.TestCase):

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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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
        mass = masses._XMLDecoder._decode_mass(doc.documentElement)
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

class MassTestCase(unittest.TestCase):

    def test_isSundayInOrdinaryTime(self):
        mass = masses.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-2'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = masses.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-22'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = masses.Mass([])
        mass.id = 'sunday-christ-the-king'
        mass.weekid = 'week-34'
        mass.seasonid = 'ordinary'
        self.assertTrue(mass.isSundayInOrdinaryTime)

        mass = masses.Mass([])
        mass.id = 'sunday'
        mass.weekid = 'week-4'
        mass.seasonid = 'lent'
        self.assertFalse(mass.isSundayInOrdinaryTime)

    def test_title(self):
       mass_doc = xml.dom.minidom.parseString('''\
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
       mass = masses._XMLDecoder._decode_mass(mass_doc.documentElement)
       optionalReading1Of2 = mass.allReadings[5]
       self.assertEqual(
           'Luke 2:22-2:40 (Option 1 of 2)',
           optionalReading1Of2.title)
       optionalReading2Of2 = mass.allReadings[6]
       self.assertEqual(
           'Luke 2:22,2:39-2:40 (Option 2 of 2)',
           optionalReading2Of2.title)


if __name__ == '__main__':
    unittest.main()
