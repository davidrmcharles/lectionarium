#!/usr/bin/env python
'''
The Lectionary of the Ordinary Form of the Mass of the Roman Rite

Command-Line Interface
======================================================================

Provide the name of a mass and we will write its readings to stdout.

Library Interface
======================================================================

* :func:`getReadings` - Get an object representation of the readings
* :func:`parse` - Parse a query for a certain mass
* :class:`MalformedQueryError` - Raised when we cannot parse a query string
* :class:`NonSingularResultsError` - Raised for empty or ambiguous results

Internals
======================================================================

* :class:`Mass` - A single mass (or Good Friday)
* :class:`Lectionary` - The lectionary for mass
* :func:`_text` - Return the text of an element
* :func:`_firstChild` - Return the first matching child of an element
* :func:`_children` - Return all matching children of an element
* :class:`RaiseIfAttrIsMissing` - Raise if an attribute is missing
* :class:`MissingAttrExceptionTestCase` - An expected attribute is missing
* :func:`_attr` - Return the value of the named attribute
'''

# Standard imports:
import collections
import datetime
import itertools
import re
import sys
import traceback
import xml.dom.minidom

# Local imports:
import bible

class Mass(object):
    '''
    Represents a single mass (or Good Friday, even though it
    technically isn't a mass).
    '''

    def __init__(self, name, readings, fixedMonth=None, fixedDay=None):
        self._name = name
        self._readings = readings
        self._normalName = None
        self._fixedMonth = fixedMonth
        self._fixedDay = fixedDay
        self._cycle = None
        self._weekKey = None

    def __str__(self):
        return self._name

    def __repr__(self):
        return '<lectionary.Mass object %s at 0x%x>' % (
            self.uniqueID, id(self))

    @property
    def name(self):
        '''
        A human-friendly name for the mass.
        '''

        return self._name

    @property
    def readings(self):
        '''
        The readings as a list of scripture citations.
        '''

        return self._readings

    @property
    def normalName(self):
        '''
        An computer-friendly name for the mass, but not necessarily a
        unique identifier:

        * All lowercase
        * All spaces converted to hyphens
        * All other non-alphanumeric characters removed
        '''

        return '-'.join(
            re.sub(
                r'[^[A-Za-z0-9 ]',
                '',
                self._name).lower().split())

    @property
    def uniqueID(self):
        '''
        A unique identifier for the mass that builds upon
        ``normalName``, adding the additional context necessary to
        make it unique.
        '''

        if self._fixedDay is not None:
            return self.normalName
        elif self._weekKey is not None:
            return '%s-%s' % (self.weekKey, self.normalName)
        else:
            return '%s/%s' % (self.cycle, self.normalName)

    @property
    def cycle(self):
        '''
        The year (``a``, ``b``, or ``c``) if the mass is specific to a
        year.  Otherwise, ``None``.
        '''

        return self._cycle

    @cycle.setter
    def cycle(self, newValue):
        self._cycle = newValue.lower()

    @property
    def fixedMonth(self):
        return self._fixedMonth

    @property
    def fixedDay(self):
        return self._fixedDay

    @property
    def isSundayInOrdinaryTime(self):
        '''
        ``True`` if this mass is a Sunday in Ordinary Time.
        '''

        if 'christ-the-king' in self.normalName:
            return True
        else:
            return re.match(
                r'[0-9][0-9]?..-sunday$', self.normalName) is not None

    @property
    def weekKey(self):
        '''
        For weekday masses, a computer-friendly identifier for the
        week.  Otherwise, ``None``.
        '''

        return self._weekKey

    @weekKey.setter
    def weekKey(self, newValue):
        self._weekKey = newValue

class Lectionary(object):
    '''
    Represents the lectionary for mass.
    '''

    def __init__(self):
        # Initialize the list of masses from sunday-lectionary.xml.
        self._masses = []
        self._cycleAMasses = []
        self._cycleBMasses = []
        self._cycleCMasses = []
        self._sundaysInOrdinaryTime = []
        doc = xml.dom.minidom.parse('sunday-lectionary.xml')
        try:
            # Decode the cycle-specific masses.
            masses = self._decode_sunday_lectionary(doc.documentElement)

            # Add all the Sunday masses to the master list.
            self._masses.extend(masses)

            # Pick-out the Sunday masses that are Sundays in ordinary
            # time.
            self._sundaysInOrdinaryTime = [
                mass
                for mass in masses
                if mass.isSundayInOrdinaryTime
                ]

            # Pick out the Sunday masses that belong to particular cycles.
            self._cycleAMasses = [
                mass for mass in self._masses if mass.cycle == 'a'
                ]
            self._cycleBMasses = [
                mass for mass in self._masses if mass.cycle == 'b'
                ]
            self._cycleCMasses = [
                mass for mass in self._masses if mass.cycle == 'c'
                ]
        finally:
            doc.unlink()

        # Further initialize the list of masses by adding the weekday
        # masses.
        doc = xml.dom.minidom.parse('weekday-lectionary.xml')
        try:
            self._weekdayMasses = self._decode_weekday_lectionary(
                doc.documentElement)
        finally:
            doc.unlink()

        # Finish initialization of the list of masses by adding the
        # masses from weekday-lectionary.xml.
        doc = xml.dom.minidom.parse('special-lectionary.xml')
        try:
            # Decode the masses that are not cycle-specific.
            self._fixedDateMasses = self._decode_special_lectionary(
                doc.documentElement)
            self._masses.extend(self._fixedDateMasses)
        finally:
            doc.unlink()

    @property
    def masses(self):
        '''
        All the masses as a list.
        '''

        return self._masses

    @property
    def cycleASundayMasses(self):
        '''
        All Sunday masses in Cycle A
        '''

        return self._cycleAMasses

    @property
    def cycleBSundayMasses(self):
        '''
        All Sunday masses in Cycle B
        '''

        return self._cycleBMasses

    @property
    def cycleCSundayMasses(self):
        '''
        All Sunday masses in Cycle C
        '''

        return self._cycleCMasses

    @property
    def allSundayMasses(self):
        '''
        All Sunday masses that belong to cycles A, B, or C.
        '''

        return itertools.chain(
            self._cycleAMasses, self._cycleBMasses, self._cycleCMasses)

    @property
    def sundaysInOrdinaryTime(self):
        '''
        All masses that are Sundays in Ordinary Time.
        '''

        return self._sundaysInOrdinaryTime

    @property
    def fixedDateMasses(self):
        '''
        All the fixed-date masses as a list.
        '''

        return self._fixedDateMasses


    @property
    def allWeekdayMasses(self):
        '''
        All the masses in the weekday lectionary.
        '''

        return self._weekdayMasses

    def weekdayMassesInWeek(self, weekKey):
        '''
        Return all the weekday masses having the given `weekKey`.
        '''

        return [
            mass
            for mass in self._weekdayMasses
            if mass.weekKey == weekKey
            ]

    def findMass(self, uniqueID):
        '''
        Return the mass having `uniqueID`, otherwise return ``None``.
        '''

        for mass in self._masses:
            if mass.uniqueID == uniqueID:
                return mass
        return None

    @property
    def formattedIDs(self):
        '''
        Return all the mass IDs as a single, formatted string suitable
        for printing to the console.
        '''

        lines = []

        def truncateToken(token, length):
            '''
            Return `token` truncated to `length` characters, and
            ellipsis to indicate truncation occurred.
            '''

            if len(token) <= length:
                return token
            return token[:length - 3] + '...'

        # Format the three-year cycle.
        lines.append('=' * 80)
        lines.append('The Three Year Cycle of Sunday Mass Readings'.center(80))
        lines.append('=' * 80)
        for massA, massB, massC in zip(
            self._cycleAMasses, self._cycleBMasses, self._cycleCMasses):
            massAToken = truncateToken(massA.uniqueID, 24)
            massBToken = truncateToken(massB.uniqueID, 24)
            massCToken = truncateToken(massC.uniqueID, 24)
            lines.append(
                '* %-24s * %-24s * %-24s' % (
                    massAToken, massBToken, massCToken))

        # Format the special feasts.
        lines.append('=' * 80)
        lines.append('Mass Readings for Certain Special Feasts'.center(80))
        lines.append('=' * 80)
        for index in range(0, len(self._fixedDateMasses), 2):
            mass1 = self._fixedDateMasses[index]
            mass1Token = '* %s' % mass1.uniqueID
            mass2Token = ''
            if (index + 1) < len(self._fixedDateMasses):
                mass2 = self.fixedDateMasses[index + 1]
                mass2Token = '* %s' % mass2.uniqueID
            lines.append(
                '     %-28s          %-28s' % (
                    mass1Token, mass2Token))
        return '\n'.join(lines)

    def _decode_sunday_lectionary(self, lectionary_node):
        '''
        Decode a <lectionary> element for the Sunday lectionary and
        return all of its masses as a list.
        '''

        result = []
        for cycle_node in _children(lectionary_node, 'cycle'):
            cycle_id = _attr(cycle_node, 'id')
            masses = self._decode_cycle(cycle_node)
            for mass in masses:
                mass.cycle = cycle_id
                result.append(mass)
        return result

    def _decode_cycle(self, cycle_node):
        '''
        Decode a <cycle> element and return all its masses as a
        list.
        '''

        result = []
        for season_node in _children(cycle_node, 'season'):
            masses = self._decode_season(season_node)
            result.extend(masses)
        return result

    def _decode_season(self, season_node):
        '''
        Decode a <season> element and return all its masses as a
        list.
        '''

        result = []
        for child_node in _children(season_node, ['mass', 'week']):
            if child_node.localName == 'mass':
                result.append(self._decode_mass(child_node))
            elif child_node.localName == 'week':
                result.extend(self._decode_week(child_node))
        return result

    def _decode_weekday_lectionary(self, lectionary_node):
        '''
        Decode the <lectionary> element for the weekday lectionary and
        return all its masses as a list.
        '''

        result = []
        for season_node in _children(lectionary_node, 'season'):
            result.extend(self._decode_season(season_node))
        return result

    def _decode_week(self, week_node):
        '''
        Decode a <week> element and return all its masses as a list.
        '''

        result = []
        for mass_node in _children(week_node, 'mass'):
            mass = self._decode_mass(mass_node)
            mass.weekKey = _attr(week_node, 'key', ifMissing=None)
            result.append(mass)
        return result

    def _decode_choice(self, choice_node):
        '''
        Decode a <choice> element and return all its
        readings as a list.
        '''

        result = []
        for reading_node in _children(choice_node, 'reading'):
            result.append(self._decode_reading(reading_node))
        return result

    def _decode_special_lectionary(self, lectionary_node):
        '''
        Decode the <lectionary> element for the special lectionary
        and return all its masses as a list.
        '''

        result = []
        for mass_node in _children(lectionary_node, 'mass'):
            mass = self._decode_mass(mass_node)
            result.append(mass)
        return result

    def _decode_mass(self, mass_node):
        '''
        Decode a single <mass> element and return it as a
        :class:`Mass` object.
        '''

        fixedMonth, fixedDay = None, None
        fixedDate = _attr(mass_node, 'date', None)
        if fixedDate is not None:
            fixedMonth, fixedDay = fixedDate.split('-')
            fixedMonth, fixedDay = int(fixedMonth), int(fixedDay)

        name = _attr(mass_node, 'name', ifMissing=None)

        readings = []
        for child_node in _children(
            mass_node, ['reading', 'choice']):
            if child_node.localName == 'reading':
                readings.append(self._decode_reading(child_node))
            elif child_node.localName == 'choice':
                readings.extend(self._decode_choice(child_node))

        return Mass(name, readings, fixedMonth, fixedDay)

    def _decode_reading(self, reading_node):
        '''
        Decode a single <reading> element and return it as a string.
        '''

        return _text(reading_node)

# Now, let's fix DOM:

def _text(node):
    '''
    Return the text content of a `node`
    '''

    return node.childNodes[0].nodeValue

def _firstChild(parent_node, localName):
    '''
    Return the first child of `parent_node` having `localName`.
    '''

    for child_node in parent_node.childNodes:
        if child_node.localName == localName:
            return child_node
    return None

def _children(parent_node, localNames):
    '''
    Return all children of `parent_node` having a localName in
    `localNames`.
    '''

    if isinstance(localNames, basestring):
        localNames = [localNames]

    result_nodes = []
    for child_node in parent_node.childNodes:
        if child_node.localName in localNames:
            result_nodes.append(child_node)
    return result_nodes

class RaiseIfAttrIsMissing(object):
    '''
    Represents the intent to raise an exception if an attribute is
    missing.
    '''

    pass

class MissingAttrException(Exception):
    '''
    Represents an unexpectedly missing attribute.
    '''

    pass

def _attr(node, localName, ifMissing=RaiseIfAttrIsMissing):
    '''
    Return the value of the attribute of `node` having `localName`.
    '''

    if not node.hasAttribute(localName):
        if ifMissing is RaiseIfAttrIsMissing:
            raise MissingAttrException()
        else:
            return ifMissing
    return node.getAttribute(localName)

def _nextSunday(d, count):
    '''
    Given a date, `d`, return the date `count`th nearest Sunday.

    A negative value for `count` move back in time to Sundays before.
    A positive value for `count` moves forward in time to following
    Sundays.  We raise `ValueError` if `count` is zero.
    '''

    if not isinstance(d, datetime.date):
        raise TypeError(
            'Non-date (%s, %s) was passed to _nextSunday()!' % (
                type(d), d))
    if not isinstance(count, int):
        raise TypeError(
            'Non-int (%s, %s) was passed as count to _nextSunday()!' % (
                type(count), count))
    if count == 0:
        raise ValueError(
            'Count of zero was passed to _nextSunday()!')

    # Handle a non-Sunday start by advancing a partial week.
    if d.weekday() != 6:
        if count > 0:
            d += datetime.timedelta(
                days=6 - d.weekday())
            count -= 1
        else:
            d -= datetime.timedelta(
                days=d.weekday() + 1)
            count += 1

    # Now that we are on a Sunday, the rest of the way is simple.
    return d + datetime.timedelta(weeks=count)

def _followingDays(d, count):
    '''
    Given a date, `d`, return the date of each day that follows,
    precisely `count` of them.
    '''

    return [
        d + datetime.timedelta(days=index + 1)
        for index in range(count)
        ]

def _dateOfEaster(year):
    '''
    Return the date of Easter for a given `year`.

    http://aa.usno.navy.mil/faq/docs/easter.php
    '''

    y = year
    c = y / 100
    n = y - 19 * ( y / 19 )
    k = ( c - 17 ) / 25
    i = c - c / 4 - ( c - k ) / 3 + 19 \
        * n + 15
    i = i - 30 * ( i / 30 )
    i = i - ( i / 28 ) * ( 1 - ( i / 28 ) \
        * ( 29 / ( i + 1 ) ) \
        * ( ( 21 - n ) / 11 ) )
    j = y + y / 4 + i + 2 - c + c / 4
    j = j - 7 * ( j / 7 )
    l = i - j
    m = 3 + ( l + 40 ) / 44
    d = l + 28 - 31 * ( m / 4 )
    return datetime.date(year, m, d)

def _sundayCycleForDate(d):
    '''
    Return the Sunday cycle for the Gospel reading ('A', 'B', or 'C')
    for a given date, `d`.
    '''

    christmasDate = datetime.date(d.year, 12, 25)
    firstSundayOfAdventDate = _nextSunday(christmasDate, -4)
    if d >= firstSundayOfAdventDate:
        return 'ABC'[d.year % 3]
    else:
        return 'CAB'[d.year % 3]

def _weekdayCycleForDate(d):
    '''
    Return the weekday cycle for the non-Gospel reading ('I' or 'II')
    for a given date, `d`.
    '''

    christmasDate = datetime.date(d.year, 12, 25)
    firstSundayOfAdventDate = _nextSunday(christmasDate, -4)
    if d >= firstSundayOfAdventDate:
        return ['I', 'II'][d.year % 2]
    else:
        return ['II', 'I'][d.year % 2]

class Calendar(object):
    '''
    A liturgical calendar for a given year that links dates to
    particular masses.
    '''

    def __init__(self, year):
        '''
        Initialize this liturgical calendar for a particular year.
        '''

        self._year = year
        self._massesByDate = None
        self._initMassesByDate()

    def massesByDate(self, month, day):
        '''
        Return the list of masses associated with a particular `month`
        and `day` for the `year` given at initialization time.
        '''

        return self._massesByDate[datetime.date(self._year, month, day)]

    def visitMassesByDate(self):
        '''
        Return a visitor onto every ``(date, masses)`` pair starting
        with January 1st, Solemnity of Mary, Mother of God.
        '''

        return sorted(self._massesByDate.iteritems())

    @property
    def dateOfPreviousChristmas(self):
        '''
        The date of Christmas from the previous year
        '''

        return datetime.date(self._year - 1, 12, 25)

    @property
    def dateOfEndOfPreviousChristmas(self):
        '''
        The date of the end of the Christmas Season from the previous
        year.
        '''

        if self.dateOfPreviousChristmas.weekday() == 6:
            return _nextSunday(self.dateOfPreviousChristmas, +2)
        else:
            return _nextSunday(self.dateOfPreviousChristmas, +3)

    @property
    def dateOfAshWednesday(self):
        '''
        The date of Ash Wednesday
        '''

        return self.dateOfEaster - datetime.timedelta(days=46)

    @property
    def dateOfEaster(self):
        '''
        The date of Easter Sunday
        '''

        return _dateOfEaster(self._year)

    @property
    def dateOfPentecost(self):
        '''
        The date of Pentecost Sunday
        '''

        return _nextSunday(self.dateOfEaster, +7)

    @property
    def dateOfFirstSundayOfAdvent(self):
        '''
        The date of the First Sunday of Advent
        '''

        return _nextSunday(self.dateOfChristmas, -4)

    @property
    def dateOfChristmas(self):
        '''
        The date of Christmas
        '''

        return datetime.date(self._year, 12, 25)

    def _initMassesByDate(self):
        self._massesByDate = {}
        self._allocateEarlyChristmasSeason()
        self._allocateLentenSeason()
        self._allocateHolyWeekAndEasterSeason()
        self._allocateAdventSeason()
        self._allocateLateChristmasSeason()
        self._allocateOrdinaryTime()
        self._allocateFixedDateMasses()

    def _allocateEarlyChristmasSeason(self):
        '''
        Allocate the masses of the Christmas season that started in
        the previous year.
        '''

        # TODO: The Octave of Christmas.

        self._assignMass(
            datetime.date(self._year, 1, 1),
            '%s/mary-mother-of-god')

        if self.dateOfPreviousChristmas.weekday() == 6:
            # Make adjustments for when Christmas falls on a Sunday.
            self._assignMass(
                self.dateOfEndOfPreviousChristmas,
                '%s/epiphany')
            self._assignMass(
                datetime.date(self._year, 1, 9),
                '%s/baptism-of-the-lord')
        else:
            self._assignMass(
                _nextSunday(self.dateOfPreviousChristmas, +1),
                '%s/holy-family')
            self._assignMass(
                _nextSunday(self.dateOfPreviousChristmas, +2),
                '%s/2nd-sunday-after-christmas')
            self._assignMass(
                datetime.date(self._year, 1, 6),
                '%s/epiphany')
            self._assignMass(
                self.dateOfEndOfPreviousChristmas,
                '%s/baptism-of-the-lord')

        # TODO: Week After Epiphany

    def _allocateLentenSeason(self):
        '''
        Allocate the masses of the Lenten season.
        '''

        # TODO: Week of Ash Wednesday
        self._assignMass(
            self.dateOfAshWednesday,
            '%s/ash-wednesday')

        # TODO: First Week of Lent
        self._assignMass(
            _nextSunday(self.dateOfEaster, -6),
            '%s/1st-sunday-of-lent')

        # TODO: Second Week of Lent
        self._assignMass(
            _nextSunday(self.dateOfEaster, -5),
            '%s/2nd-sunday-of-lent')

        # TODO: Third Week of Lent
        self._assignMass(
            _nextSunday(self.dateOfEaster, -4),
            '%s/3rd-sunday-of-lent')

        # TODO: Fourth Week of Lent
        self._assignMass(
            _nextSunday(self.dateOfEaster, -3),
            '%s/4th-sunday-of-lent')

        # TODO: Fifth Week of Lent
        self._assignMass(
            _nextSunday(self.dateOfEaster, -2),
            '%s/5th-sunday-of-lent')

    def _allocateHolyWeekAndEasterSeason(self):
        '''
        Allocate the masses of Holy Week and the Easter Season.
        '''

        # TODO: Holy Week
        self._assignMass(
            _nextSunday(self.dateOfEaster, -1),
            '%s/palm-sunday')
        self._assignMass(
            self.dateOfEaster - datetime.timedelta(days=3),
            '%s/mass-of-lords-supper')
        self._assignMass(
            self.dateOfEaster - datetime.timedelta(days=2),
            '%s/good-friday')
        self._assignMass(
            self.dateOfEaster - datetime.timedelta(days=1),
            '%s/easter-vigil')

        # TODO: Octave of Easter
        self._assignMass(
            self.dateOfEaster,
            '%s/easter-sunday')

        # TODO: Second Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +1),
            '%s/2nd-sunday-of-easter')

        # TODO: Third Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +2),
            '%s/3rd-sunday-of-easter')

        # TODO: Fourth Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +3),
            '%s/4th-sunday-of-easter')

        # TODO: Fifth Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +4),
            '%s/5th-sunday-of-easter')

        # TODO: Sixth Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +5),
            '%s/6th-sunday-of-easter')
        self._assignMass(
            self.dateOfEaster + datetime.timedelta(days=40),
            '%s/ascension-of-our-lord')

        # TODO: Seventh Week of Easter
        self._assignMass(
            _nextSunday(self.dateOfEaster, +6),
            '%s/7th-sunday-of-easter')

        self._assignMass(
            self.dateOfEaster + datetime.timedelta(days=49),
            '%s/pentecost-vigil')
        self._assignMass(
            self.dateOfPentecost,
            '%s/pentecost')

    def _allocateAdventSeason(self):
        '''
        Allocate the masses of the Advent season.
        '''

        # TODO: First Week of Advent
        self._assignMass(
            self.dateOfFirstSundayOfAdvent,
            '%s/1st-sunday-of-advent')

        # TODO: Second Week of Advent
        self._assignMass(
            _nextSunday(self.dateOfChristmas, -3),
            '%s/2nd-sunday-of-advent')

        # TODO: Third Week of Advent
        self._assignMass(
            _nextSunday(self.dateOfChristmas, -2),
            '%s/3rd-sunday-of-advent')

        # TODO: Fourth Week of Advent
        self._assignMass(
            _nextSunday(self.dateOfChristmas, -1),
            '%s/4th-sunday-of-advent')

    def _allocateLateChristmasSeason(self):
        '''
        Allocate the masses of the Christmas season that comes at the
        end of the year.
        '''

        self._appendMass(
            _nextSunday(self.dateOfChristmas, -1),
            '%s/christmas-vigil')

        # TODO: Octave of Christmas
        self._appendMass(
            self.dateOfChristmas,
            '%s/christmas-at-midnight')
        self._appendMass(
            self.dateOfChristmas,
            '%s/christmas-at-dawn')
        self._appendMass(
            self.dateOfChristmas,
            '%s/christmas-during-the-day')

    def _allocateOrdinaryTime(self):
        '''
        Allocate the masses of Ordinary Time.
        '''

        # Ordinary Time Before Lent: Calculate and record the masses
        # of Ordinary Time that come between the end of Christmas and
        # Ash Wednesday.
        sundaysInOrdinaryTime = [
            mass
            for mass in _lectionary.sundaysInOrdinaryTime
            if mass.cycle == _sundayCycleForDate(
                datetime.date(self._year, 1, 1)).lower()
            ]

        weekdaysInOrdinaryTime = [
            list(_lectionary.weekdayMassesInWeek('week-%d' % weekIndex))
            for weekIndex in range(1, 35)
            ]

        # Handle the weekday masses for the first week of ordinary
        # time as a special case.
        for weekdayDate, weekdayMass in zip(
            _followingDays(self.dateOfEndOfPreviousChristmas, 6),
            weekdaysInOrdinaryTime.pop(0)):
            # TODO: This condition exists to allow Baptism of the Lord
            # to have priority over Monday of the first week of
            # Ordinary Time, but it doesn't seem to be the best way.
            if weekdayDate not in self._massesByDate:
                self._assignMass(weekdayDate, weekdayMass)

        sundayDate = _nextSunday(self.dateOfEndOfPreviousChristmas, +1)
        while sundayDate < self.dateOfAshWednesday:
            # Assign the Sunday mass.
            self._assignMass(sundayDate, sundaysInOrdinaryTime.pop(0))

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                _followingDays(sundayDate, 6), weekdaysInOrdinaryTime.pop(0)):
                self._assignMass(weekdayDate, weekdayMass)

            sundayDate = _nextSunday(sundayDate, +1)

        # Ordinary Time After Easter: Calculate and record the masses
        # of Ordinary Time that come between the end of Easter and
        # Advent.
        sundayDate = _nextSunday(self.dateOfFirstSundayOfAdvent, -1)
        while sundayDate > self.dateOfPentecost:
            # Assign the Sunday mass.
            self._assignMass(sundayDate, sundaysInOrdinaryTime.pop())

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                _followingDays(sundayDate, 6), weekdaysInOrdinaryTime.pop()):
                self._assignMass(weekdayDate, weekdayMass)

            sundayDate = _nextSunday(sundayDate, -1)

        # These special feasts in Ordinary Time have priority over
        # whatever else is being celebrated that day.
        self._assignMass(
            _nextSunday(self.dateOfEaster, +8),
            '%s/trinity-sunday')

        corpusChristiDate = self.dateOfEaster + datetime.timedelta(days=60)
        if corpusChristiDate.weekday() in (5, 4, 3):
            corpusChristiDate += datetime.timedelta(
                days=6 - corpusChristiDate.weekday())
        self._assignMass(
            corpusChristiDate,
            '%s/corpus-christi')

        self._assignMass(
            self.dateOfEaster + datetime.timedelta(days=68),
            '%s/sacred-heart-of-jesus')

    def _allocateFixedDateMasses(self):
        '''
        Allocate the fixed-date masses.
        '''

        for mass in _lectionary.fixedDateMasses:
            d = datetime.date(self._year, mass.fixedMonth, mass.fixedDay)

            if (mass.normalName == 'joseph-husband-of-mary') and \
                    (d.weekday() == 6):
                d += datetime.timedelta(days=1)

            if mass.normalName in (
                'all-souls-second-mass', 'all-souls-third-mass'):
                self._appendMass(d, mass.normalName)
            else:
                self._assignMass(d, mass.normalName)

    def _assignMass(self, d, mass):
        '''
        Assign `mass` to date `d`, replacing any other masses that may
        already be there.
        '''

        if isinstance(mass, basestring):
            if '%s' in mass:
                mass = mass % _sundayCycleForDate(d).lower()
            mass = _lectionary.findMass(mass)

        self._massesByDate[d] = [mass]

    def _appendMass(self, d, mass):
        '''
        Apppend `mass` to the list of masses already associated with
        date `d`.
        '''
        
        if isinstance(mass, basestring):
            if '%s' in mass:
                mass = mass % _sundayCycleForDate(d).lower()
            mass = _lectionary.findMass(mass)

        if d not in self._massesByDate:
            self._massesByDate[d] = []
        self._massesByDate[d].append(mass)

class MalformedQueryError(ValueError):
    '''
    Represents when we cannot parse a query string.
    '''

    def __init__(self, query, s):
        self.query = query
        ValueError.__init__(self, s)

def parse(query):
    '''
    Parse `query` and return all possible matching masses as a list of
    unique identifiers.

    :raises TypeError: if `query` is not a string
    :raises MalformedQueryError: if `query` cannot be parsed
    '''

    # Fail if `query` is not a string.
    if not isinstance(query, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed lectionary.parse()!' % (
                type(query), query))

    # Discard leading and trailing whitespace and fail if nothing is
    # left.
    query = query.strip()
    if len(query) == 0:
        raise MalformedQueryError(
            query,
            'No non-white characters passed to lectionary.parse()!')

    # Split the query at the slash, if any, and fail if there is more
    # than one slash.
    slash_tokens = query.split('/')
    if len(slash_tokens) > 2:
        raise MalformedQueryError(
            query,
            'Too many slashes in query "%s"!' % (query))

    # Isolate the cycle (if any) and the normal name substring.
    cycle = None
    if len(slash_tokens) == 2:
        cycle, normalNameSubstring = slash_tokens
        if cycle.lower() not in ('a', 'b', 'c'):
            raise MalformedQueryError(
                query,
                'Cycle is "%s", but must be one of A, B, or C (in either case)!' % (
                    cycle))
    elif len(slash_tokens) == 1:
        normalNameSubstring = slash_tokens[0]

    # Collect all matches and return them.
    def isMatch(mass):
        '''
        Return ``True`` if `mass` has a matching `cycle` and contains
        `normalNameSubstring` within its `normalName`.
        '''

        if cycle is None:
            return normalNameSubstring in mass.normalName
        else:
            return (mass.cycle == cycle) and \
                (normalNameSubstring in mass.normalName)

    return [
        mass.uniqueID
        for mass in _lectionary.masses
        if isMatch(mass)
        ]

class NonSingularResultsError(ValueError):
    '''
    Represents a query that failed because it either returned no
    result, or multiple results, when all we really wanted was a
    single result.
    '''

    def __init__(self, query, massUniqueIDs):
        self.query = query
        self.massUniqueIDs = massUniqueIDs
        if len(self.massUniqueIDs) == 0:
            message = 'Query "%s" doesn\'t match anything!' % self.query
        else:
            message = '''\
Query "%s" matches multiple masses.  Did you mean?

%s

Provide additional query text to disambiguate.
''' % (self.query, '\n'.join([
                        '* %s' % uniqueID
                        for uniqueID in self.massUniqueIDs
                        ]))
        ValueError.__init__(self, message)

def getReadings(query):
    '''
    Return an object representation of the readings with the single
    mass indicated by `query`.
    '''

    # Parse the query and fail if it returns anything but exactly one
    # result.
    massUniqueIDs = parse(query)
    if len(massUniqueIDs) != 1:
        raise NonSingularResultsError(query, massUniqueIDs)

    massUniqueID = massUniqueIDs[0]
    mass = _lectionary.findMass(massUniqueID)

    readings = collections.OrderedDict()
    for reading in mass.readings:
        readings[reading] = bible.getVerses(reading)
    return mass.name, readings

def main():
    '''
    The command-line interface.
    '''

    # If the user provided no arguments, print help and quit.
    if len(sys.argv) == 1:
        sys.stderr.write('%s\n' % _lectionary.formattedIDs)
        sys.stderr.write('''\

Provide the name of a mass and we will write its readings to stdout.
''')
        raise SystemExit(1)

    # If the user provided more than one argument, print an error
    # message and quit.
    if len(sys.argv) > 2:
        sys.stderr.write('One mass at a time, please!\n')
        raise SystemExit(1)

    # Parse the query.
    try:
        massName, readings = getReadings(sys.argv[1])
    except NonSingularResultsError as e:
        sys.stderr.write('%s\n' % e.message)
        raise SystemExit(-1)

    # Write all the readings for the mass to stdout.
    sys.stdout.write('Readings for %s\n' % (massName))
    for citation, verses in readings.iteritems():
        sys.stdout.write('\n%s' % citation)
        sys.stdout.write('\n%s' % bible.formatVersesForConsole(verses))
    return

_lectionary = Lectionary()

if __name__ == '__main__':
    main()
