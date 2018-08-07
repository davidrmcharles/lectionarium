#!/usr/bin/env python
'''
The Lectionary of the Ordinary Form of the Mass of the Roman Rite

Summary of Library Interface
======================================================================

* :func:`getReadings` - Get an object representation of the readings
* :func:`parse` - Parse a query for a certain mass
* :class:`Lectionary` - The lectionary for mass
* :class:`Calendar` - All the readings for a single calendar year
* :class:`MalformedQueryError` - Raised when we cannot parse a query string
* :class:`NonSingularResultsError` - Raised for empty or ambiguous results
* :class:`MalformedDateError` - Raised when we cannot parse a date
* :class:`InvalidDateError` - Raised when we can parse the date, but it makes no sense

Reference
======================================================================
'''

# Standard imports:
import collections
import datetime
import inspect
import itertools
import os
import re
import sys
import traceback

# Local imports:
import bible
import citations
import datetools
import masses

class Lectionary(object):
    '''
    The lectionary for mass
    '''

    _instance = None

    @classmethod
    def _getInstance(cls):
        if cls._instance is None:
            cls._instance = Lectionary()
        return cls._instance

    def __init__(self):
        # Initialize the list of masses from sunday-lectionary.xml.
        self._allMasses = []
        self._allSundayMasses = []
        self._sundaysInOrdinaryTime = []

        self._allSundayMasses = masses.getSundayMasses()
        self._allMasses.extend(self._allSundayMasses)
        self._sundaysInOrdinaryTime = [
            mass
            for mass in self._allSundayMasses
            if mass.isSundayInOrdinaryTime
            ]

        self._allWeekdayMasses = masses.getWeekdayMasses()
        self._allMasses.extend(self._allWeekdayMasses)

        self._allSpecialMasses = masses.getSpecialMasses()
        self._allMasses.extend(self._allSpecialMasses)

    @property
    def allMasses(self):
        '''
        All the masses as a list.
        '''

        return self._allMasses

    @property
    def allSundayMasses(self):
        '''
        All Sunday masses.
        '''

        return self._allSundayMasses

    @property
    def sundaysInOrdinaryTime(self):
        '''
        All Sunday masses in Ordinary Time.
        '''

        return self._sundaysInOrdinaryTime

    @property
    def allSpecialMasses(self):
        '''
        All the fixed-date masses as a list.
        '''

        return self._allSpecialMasses


    @property
    def allWeekdayMasses(self):
        '''
        All the masses in the weekday lectionary.
        '''

        return self._allWeekdayMasses

    def weekdayMassesInWeek(self, seasonid, weekid):
        '''
        Return all the weekday masses having the given `seasonid` and
        `weekid`.
        '''

        return [
            mass
            for mass in self._allWeekdayMasses
            if (mass.seasonid == seasonid) and (mass.weekid == weekid)
            ]

    @property
    def weekdayMassSeasonIDs(self):
        seen = set()
        return [
            mass.seasonid
            for mass in self._allWeekdayMasses
            if not (mass.seasonid in seen or seen.add(mass.seasonid))
            ]

    def weekdayMassWeekIDs(self, seasonid):
        seen = set()
        return [
            mass.weekid
            for mass in self._allWeekdayMasses
            if (mass.seasonid == seasonid) and not (
                mass.weekid in seen or seen.add(mass.weekid)
                )
            ]

    def findMass(self, fqid):
        '''
        Return the mass having `fqid`, otherwise return ``None``.
        '''

        for mass in self._allMasses:
            if mass.fqid == fqid:
                return mass
        return None

    @staticmethod
    def _formattedIDsForRelatedMasses(masses, title):
        '''
        Return the fqids of all the `masses` as a list of lines
        with a centered `title`.
        '''

        lines = []
        lines.append('=' * 80)
        lines.append(title.center(80))
        lines.append('=' * 80)
        for index in range(0, len(masses), 2):
            mass1 =  masses[index]
            mass1Token = '* %s' % mass1.fqid
            mass2Token = ''
            if (index + 1) < len(masses):
                mass2 = masses[index + 1]
                mass2Token = '* %s' % mass2.fqid
            lines.append(
                '%-37s %-37s' % (
                    mass1Token, mass2Token))
        return lines

    @property
    def weekdayIDsFormatted(self):
        return '\n'.join(
            self._formattedIDsForRelatedMasses(
                self._allWeekdayMasses,
                'Weekday Mass Readings'))

    @property
    def sundayIDsFormatted(self):
        return '\n'.join(
            self._formattedIDsForRelatedMasses(
                self._allSundayMasses,
                'Sunday Mass Readings'))

    @property
    def specialIDsFormatted(self):
        return '\n'.join(
            self._formattedIDsForRelatedMasses(
                self._allSpecialMasses,
                'Mass Readings for Certain Special Feasts'))

    @property
    def allIDsFormatted(self):
        return '\n'.join([
                self.weekdayIDsFormatted,
                self.sundayIDsFormatted,
                self.specialIDsFormatted
                ])

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
            return datetools.nextSunday(self.dateOfPreviousChristmas, +2)
        else:
            return datetools.nextSunday(self.dateOfPreviousChristmas, +3)

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

        return datetools.dateOfEaster(self._year)

    @property
    def dateOfPentecost(self):
        '''
        The date of Pentecost Sunday
        '''

        return datetools.nextSunday(self.dateOfEaster, +7)

    @property
    def dateOfFirstSundayOfAdvent(self):
        '''
        The date of the First Sunday of Advent
        '''

        return datetools.nextSunday(self.dateOfChristmas, -4)

    @property
    def dateOfChristmas(self):
        '''
        The date of Christmas
        '''

        return datetime.date(self._year, 12, 25)

    def _initMassesByDate(self):
        self._massesByDate = {}
        self._allocateOrdinaryTime()
        self._allocateEarlyChristmasSeason()
        self._allocateLentenSeason()
        self._allocateHolyWeekAndEasterSeason()
        self._allocateAdventSeason()
        self._allocateLateChristmasSeason()
        self._allocateSpecialMasses()

    def _allocateEarlyChristmasSeason(self):
        '''
        Allocate the masses of the Christmas season that started in
        the previous year.
        '''

        # The Octave of Christmas.
        massDates = datetools.followingDays(self.dateOfPreviousChristmas, 6)
        massKeys = (
            'day-2-st-stephen',
            'day-3-st-john',
            'day-4-holy-innocents',
            'day-5',
            'day-6',
            'day-7',
            )
        for massDate, massKey in zip(massDates, massKeys):
            if massDate.year < self._year:
                continue
            self._assignMass(
                massDate,
                getLectionary().findmass('christmas/%s' % massKey))

        # Fixed-date weekday masses following Christmas.
        massDates = datetools.inclusiveDateRange(
            datetime.date(self._year, 1, 2),
            datetime.date(self._year, 1, 7))
        massKeys = [
            'christmas/01-%02d' % day
            for day in range(2, 8)
            ]
        for massDate, massKey in zip(massDates, massKeys):
            self._assignMass(
                massDate,
                getLectionary().findMass(massKey))

        # The solemnity of Mary, Mother of God.
        self._assignMass(
            datetime.date(self._year, 1, 1),
            'mary-mother-of-god')

        if self.dateOfPreviousChristmas.weekday() == 6:
            # Make adjustments for when Christmas falls on a Sunday.
            self._assignMass(
                self.dateOfEndOfPreviousChristmas,
                'christmas/epiphany')
            self._assignMass(
                datetime.date(self._year, 1, 9),
                'christmas/baptism-of-the-lord')
        else:
            self._assignMass(
                datetools.nextSunday(self.dateOfPreviousChristmas, +1),
                'christmas/holy-family')
            self._assignMass(
                datetools.nextSunday(self.dateOfPreviousChristmas, +2),
                'christmas/2nd-sunday-after-christmas')
            self._assignMass(
                datetime.date(self._year, 1, 6),
                'christmas/epiphany')
            self._assignMass(
                self.dateOfEndOfPreviousChristmas,
                'christmas/baptism-of-the-lord')

        # FIXME: Week After Epiphany.  None of these masses were said
        # in the US in 2017, but they were, or will be used in other
        # years.

    def _allocateLentenSeason(self):
        '''
        Allocate the masses of the Lenten season.
        '''

        # Week of Ash Wednesday
        massDates = [self.dateOfAshWednesday] + \
            datetools.followingDays(self.dateOfAshWednesday, 3)
        massKeys = (
            'ash-wednesday',
            'thursday',
            'friday',
            'saturday',
            )
        for massDate, massKey in zip(massDates, massKeys):
            self._assignMass(
                massDate, 'lent/week-of-ash-wednesday/%s' % massKey)

        sundayDates = (
            datetools.nextSunday(self.dateOfEaster, -6),
            datetools.nextSunday(self.dateOfEaster, -5),
            datetools.nextSunday(self.dateOfEaster, -4),
            datetools.nextSunday(self.dateOfEaster, -3),
            datetools.nextSunday(self.dateOfEaster, -2),
            )

        for sundayIndex, sundayDate in enumerate(sundayDates):
            # Assign the Sunday mass.
            self._assignMass(
                sundayDate,
                'lent/week-%d/sunday' % (sundayIndex + 1))

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                datetools.followingDays(sundayDate, 6),
                getLectionary().weekdayMassesInWeek(
                    'lent', 'week-%d' % (sundayIndex + 1))):
                self._assignMass(weekdayDate, weekdayMass)

    def _allocateHolyWeekAndEasterSeason(self):
        '''
        Allocate the masses of Holy Week and the Easter Season.
        '''

        # Holy Week
        dateOfPalmSunday = datetools.nextSunday(self.dateOfEaster, -1)
        self._assignMass(dateOfPalmSunday, 'holy-week/palm-sunday')

        massDates = datetools.followingDays(dateOfPalmSunday, 4)
        massKeys = (
            'monday', 'tuesday', 'wednesday', 'thursday-chrism-mass'
            )
        for massDate, massKey in zip(massDates, massKeys):
            mass = getLectionary().findMass('holy-week/%s' % massKey)
            self._assignMass(
                massDate,
                mass)

        self._appendMass(
            self.dateOfEaster - datetime.timedelta(days=3),
            'holy-week/mass-of-the-lords-supper')
        self._assignMass(
            self.dateOfEaster - datetime.timedelta(days=2),
            'holy-week/good-friday')
        self._assignMass(
            self.dateOfEaster - datetime.timedelta(days=1),
            'easter/easter-vigil')

        sundayDates = (
            self.dateOfEaster,
            datetools.nextSunday(self.dateOfEaster, 1),
            datetools.nextSunday(self.dateOfEaster, 2),
            datetools.nextSunday(self.dateOfEaster, 3),
            datetools.nextSunday(self.dateOfEaster, 4),
            datetools.nextSunday(self.dateOfEaster, 5),
            datetools.nextSunday(self.dateOfEaster, 6),
            )
        for sundayIndex, sundayDate in enumerate(sundayDates):
            # Assign the Sunday mass.
            if sundayIndex == 0:
                self._assignMass(
                    sundayDate,
                    'easter/week-1/easter-sunday')
            else:
                self._assignMass(
                    sundayDate,
                    'easter/week-%d/sunday' % (sundayIndex + 1))

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                datetools.followingDays(sundayDate, 6),
                getLectionary().weekdayMassesInWeek(
                    'easter', 'week-%d' % (sundayIndex + 1))):
                self._assignMass(weekdayDate, weekdayMass)

        self._appendMass(
            self.dateOfPentecost - datetime.timedelta(days=1),
            'easter/pentecost-vigil')
        self._assignMass(
            self.dateOfPentecost,
            'easter/pentecost')

    def _allocateAdventSeason(self):
        '''
        Allocate the masses of the Advent season.
        '''

        sundayDates = (
            self.dateOfFirstSundayOfAdvent,
            datetools.nextSunday(self.dateOfChristmas, -3),
            datetools.nextSunday(self.dateOfChristmas, -2),
            datetools.nextSunday(self.dateOfChristmas, -1),
            )
        for sundayIndex, sundayDate in enumerate(sundayDates):
            # Assign the Sunday mass.
            self._assignMass(
                sundayDate,
                'advent/week-%d/sunday' % (sundayIndex + 1))

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                datetools.followingDays(sundayDate, 6),
                getLectionary().weekdayMassesInWeek(
                    'advent', 'week-%d' % (sundayIndex + 1))):
                self._assignMass(weekdayDate, weekdayMass)

        # Handle the fixed-date masses in Advent starting on December
        # 17th.  These override the other weekday masses of Advent,
        # but not the Sunday masses of Advent.
        massDates = datetools.inclusiveDateRange(
            datetime.date(self._year, 12, 17),
            datetime.date(self._year, 12, 24))
        massKeys = [
            'advent/12-%02d' % day
            for day in range(17, 25)
            ]
        for massDate, massKey in zip(massDates, massKeys):
            if massDate.weekday() == 6:
                continue
            self._assignMass(massDate, massKey)

    def _allocateLateChristmasSeason(self):
        '''
        Allocate the masses of the Christmas season that comes at the
        end of the year.
        '''

        self._appendMass(
            datetools.nextSunday(self.dateOfChristmas, -1),
            'christmas/christmas-vigil')

        # Octave of Christmas
        self._appendMass(
            self.dateOfChristmas,
            'christmas/christmas-at-midnight')
        self._appendMass(
            self.dateOfChristmas,
            'christmas/christmas-at-dawn')
        self._appendMass(
            self.dateOfChristmas,
            'christmas/christmas-during-the-day')

        massDates = datetools.inclusiveDateRange(
            self.dateOfChristmas + datetime.timedelta(days=1),
            datetime.date(self._year, 12, 31))
        massKeys = (
            'day-2-st-stephen',
            'day-3-st-john',
            'day-4-holy-innocents',
            'day-5',
            'day-6',
            'day-7',
            )
        for massDate, massKey in zip(massDates, massKeys):
            self._assignMass(
                massDate,
                getLectionary().findMass('christmas/%s' % massKey))

        dateOfHolyFamily = datetools.nextSunday(self.dateOfChristmas, 1)
        if dateOfHolyFamily.year == self._year:
            self._assignMass(
                dateOfHolyFamily, 'christmas/holy-family')

    def _allocateOrdinaryTime(self):
        '''
        Allocate the masses of Ordinary Time.
        '''

        # Ordinary Time Before Lent: Calculate and record the masses
        # of Ordinary Time that come between the end of Christmas and
        # Ash Wednesday.
        sundaysInOrdinaryTime = list(getLectionary().sundaysInOrdinaryTime)
        weekdaysInOrdinaryTime = [
            getLectionary().weekdayMassesInWeek(
                'ordinary', 'week-%d' % weekIndex)
            for weekIndex in range(1, 35)
            ]

        # Handle the weekday masses for the first week of ordinary
        # time as a special case.
        for weekdayDate, weekdayMass in zip(
            datetools.followingDays(self.dateOfEndOfPreviousChristmas, 6),
            weekdaysInOrdinaryTime.pop(0)):
            self._assignMass(weekdayDate, weekdayMass)

        sundayDate = datetools.nextSunday(self.dateOfEndOfPreviousChristmas, +1)
        while sundayDate < self.dateOfAshWednesday:
            # Assign the Sunday mass.
            try:
                self._assignMass(sundayDate, sundaysInOrdinaryTime.pop(0))
            except IndexError:
                print '***', sundayDate
                raise

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                datetools.followingDays(sundayDate, 6), weekdaysInOrdinaryTime.pop(0)):
                self._assignMass(weekdayDate, weekdayMass)

            sundayDate = datetools.nextSunday(sundayDate, +1)

        # Ordinary Time After Easter: Calculate and record the masses
        # of Ordinary Time that come between the end of Easter and
        # Advent.
        sundayDate = datetools.nextSunday(self.dateOfFirstSundayOfAdvent, -1)
        while sundayDate > datetools.nextSunday(self.dateOfPentecost, -1):
            # Assign the Sunday mass.
            self._assignMass(sundayDate, sundaysInOrdinaryTime.pop())

            # Assign the weekday masses.
            for weekdayDate, weekdayMass in zip(
                datetools.followingDays(sundayDate, 6), weekdaysInOrdinaryTime.pop()):
                self._assignMass(weekdayDate, weekdayMass)

            sundayDate = datetools.nextSunday(sundayDate, -1)

        # These special feasts in Ordinary Time have priority over
        # whatever else is being celebrated that day.
        self._assignMass(
            datetools.nextSunday(self.dateOfEaster, +8),
            'trinity-sunday')

        corpusChristiDate = self.dateOfEaster + datetime.timedelta(days=60)
        if corpusChristiDate.weekday() in (5, 4, 3):
            corpusChristiDate += datetime.timedelta(
                days=6 - corpusChristiDate.weekday())
        self._assignMass(
            corpusChristiDate,
            'corpus-christi')

        self._assignMass(
            self.dateOfEaster + datetime.timedelta(days=68),
            'sacred-heart-of-jesus')

    def _allocateSpecialMasses(self):
        '''
        Allocate the 'special' masses with fixed dates.
        '''

        for mass in getLectionary().allSpecialMasses:
            if mass.fixedMonth is None or mass.fixedDay is None:
                continue
            d = datetime.date(self._year, mass.fixedMonth, mass.fixedDay)

            if (mass.id == 'joseph-husband-of-mary') and \
                    (d.weekday() == 6):
                d += datetime.timedelta(days=1)

            if mass.id in (
                'all-souls-2', 'all-souls-3'):
                self._appendMass(d, mass.id)
            else:
                self._assignMass(d, mass.id)

    def _assignMass(self, d, mass):
        '''
        Assign `mass` to date `d`, replacing any other masses that may
        already be there.
        '''

        if isinstance(mass, basestring):
            massid = mass
            mass = getLectionary().findMass(massid)
            if mass is None:
                raise ValueError('No mass with id "%s"!' % massid)

        self._massesByDate[d] = [mass]

    def _appendMass(self, d, mass):
        '''
        Apppend `mass` to the list of masses already associated with
        date `d`.
        '''
        
        if isinstance(mass, basestring):
            massid = mass
            mass = getLectionary().findMass(mass)
            if mass is None:
                raise ValueError('No mass with id "%s"!' % massid)

        if d not in self._massesByDate:
            self._massesByDate[d] = []
        self._massesByDate[d].append(mass)

class MalformedQueryError(ValueError):
    '''
    A failure to parse a query string
    '''

    def __init__(self, query, s):
        self.query = query
        ValueError.__init__(self, s)

def parse(query):
    '''
    Parse `query` and return all possible matches as a list of fqids,
    the desired ``sundayCycle``, and the desired ``weekdayCycle``.

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

    # Split the query at the sharp, if any, and fail if there is more
    # than one sharp.
    sharp_tokens = query.split('#')
    if len(sharp_tokens) > 2:
        raise MalformedQueryError(
            query,
            'Too many sharps in query "%s"!' % (query))

    # Isolate the cycle (if any) and the id substring.
    if len(sharp_tokens) == 2:
        idSubstring, cycle = sharp_tokens
        if len(idSubstring) == 0:
            raise MalformedQueryError(
                query,
                'The id portion of the query is an empty string!')

        if len(cycle) == 0:
            # A cycle indicator that is the empty string means all
            # readings regardless of cycle.
            sundayCycle, weekdayCycle = None, None
        elif cycle.upper() in ('A', 'B', 'C'):
            sundayCycle, weekdayCycle = cycle.upper(), None
        elif cycle.upper() in ('I', 'II'):
            sundayCycle, weekdayCycle = None, cycle.upper()
        else:
            raise MalformedQueryError(
                query,
                'Cycle is "%s", but must be one of A, B, C, I, or II'
                ' (in either case)!' % (
                    cycle))
    elif len(sharp_tokens) == 1:
        # No cycle indicator means the sunday cycle and weekday cycle
        # for the current date.
        idSubstring = sharp_tokens[0]

    try:
        massDate = _parseDate(idSubstring)
        if len(sharp_tokens) == 1:
            sundayCycle = datetools.sundayCycleForDate(massDate)
            weekdayCycle = datetools.weekdayCycleForDate(massDate)

        calendar = Calendar(massDate.year)
        masses = calendar.massesByDate(massDate.month, massDate.day)
        return [mass.fqid for mass in masses], sundayCycle, weekdayCycle
    except MalformedDateError:
        if len(sharp_tokens) == 1:
            sundayCycle = datetools.sundayCycleForDate(datetime.date.today())
            weekdayCycle = datetools.weekdayCycleForDate(datetime.date.today())
        return [
            mass.fqid
            for mass in getLectionary().allMasses
            if idSubstring in mass.fqid
            ], sundayCycle, weekdayCycle

class NonSingularResultsError(ValueError):
    '''
    A query failed because it either returned no
    result, or multiple results, when all we really wanted was a
    single result
    '''

    def __init__(self, query, fqids):
        self.query = query
        self.fqids = fqids
        if len(self.fqids) == 0:
            message = 'Query "%s" doesn\'t match anything!' % self.query
        else:
            message = '''\
Query "%s" matches multiple masses.  Did you mean?

%s

Provide additional query text to disambiguate.
''' % (self.query, '\n'.join([
                        '* %s' % fqid
                        for fqid in self.fqids
                        ]))
        ValueError.__init__(self, message)

def _parseDate(token):
    '''
    Parse `token` and return a ``datetime.date`` object.

    Interpret ``today`` to mean today's date.  Otherwise, expect the
    date to be at most three decimal-integer subtokens, separated by
    hyphens, in the form::

        YYYY-MM-DD

    If YYYY is missing, assume the caller means the current year.

    If the MM is missing, assume the caller means the current month.
    '''

    if not isinstance(token, basestring):
        raise TypeError(
            'Non-string (%s, %s) was passed to _parseDate()!' % (
                type(token), token))

    # Handle the special date token ``today``.
    today = datetime.date.today()
    if token == 'today':
        return today

    # Split the date into subtokens at the hypens.  There must be at
    # least one subtoken, but no more than three.
    subtokens = token.split('-')
    if len(subtokens) < 1 or len(subtokens) > 3:
        raise MalformedDateError(token)

    # Initialize the year and month to today's year and month as
    # defaults.  These values may be overridden if we find them in the
    # `token`.
    year, month = today.year, today.month

    def parseSubtoken(subtoken):
        '''
        Parse the date `subtoken` by interpreting it as a decimal
        integer.  If this fails, consider the date token malformed.
        '''

        try:
            return int(subtoken)
        except ValueError:
            raise MalformedDateError(token)

    # Parse the day subtoken.  Parse the month and year subtokens if
    # they are available.
    day = parseSubtoken(subtokens[-1])
    if len(subtokens) > 1:
        month = parseSubtoken(subtokens[-2])
    if len(subtokens) > 2:
        year = parseSubtoken(subtokens[-3])

    # Convert and return the date as a ``datetime.date`` object.
    try:
        return datetime.date(year, month, day)
    except ValueError:
        raise InvalidDateError(token)

class MalformedDateError(ValueError):
    '''
    A failure to parse a date token
    '''

    def __init__(self, token):
        self.token = token
        ValueError.__init__(self, 'Date "%s" is malformed!')

class InvalidDateError(ValueError):
    '''
    The case of a date token that can be parsed, but makes
    no sense because the year, month, or day are out of range
    '''

    def __init__(self, token):
        self.token = token
        ValueError.__init__(self, 'Date "%s" is invalid!')

def getReadings(query):
    '''
    Return an object representation of the readings for the single
    mass indicated by `query`.
    '''

    # Parse the query and fail if it returns anything but exactly one
    # result, unless the query is an exact match for something.
    fqids, sundayCycle, weekdayCycle = parse(query)
    if len(fqids) != 1 and query not in fqids:
        raise NonSingularResultsError(query, fqids)

    fqid = fqids[0]
    mass = getLectionary().findMass(fqid)

    # Compose a title for the mass.
    if sundayCycle is None and weekdayCycle is None:
        massTitle = '%s (All Cycles)' % mass.displayName
    elif sundayCycle is not None and weekdayCycle is None:
        massTitle = '%s (Cycle %s)' % (mass.displayName, sundayCycle)
    elif sundayCycle is None and weekdayCycle is not None:
        massTitle = '%s (Cycle %s)' % (mass.displayName, weekdayCycle)
    elif sundayCycle is not None and weekdayCycle is not None:
        massTitle = '%s (Cycle %s, %s)' % (
            mass.displayName, sundayCycle, weekdayCycle)

    # Collect the texts that go with the applicable readings.
    readings = collections.OrderedDict()
    for reading in mass.applicableReadings(sundayCycle, weekdayCycle):
        readings[reading] = bible.getVerses(reading.citation)

    return massTitle, readings

def getLectionary():
    '''
    Return a singleton instance of :class:`Lectionary`.
    '''

    return Lectionary._getInstance()
