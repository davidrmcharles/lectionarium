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
* :class:`OFSundayLectionary` - The Ordinary-Form Lectionary for Sundays
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

    def __init__(self, name, readings, date=None):
        self._name = name
        self._readings = readings
        self._normalName = None
        self._date = date
        self._year = None

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

        if self._date is not None:
            return self.normalName
        else:
            return '%s/%s' % (self._year, self.normalName)

    @property
    def year(self):
        '''
        The year (``a``, ``b``, or ``c``) if the mass is specific to a
        year.  Otherwise, ``None``.
        '''

        return self._year

    @year.setter
    def year(self, newValue):
        self._year = newValue.lower()

class OFSundayLectionary(object):
    '''
    Represents the Ordinary-Form Lectionary for Sunday Mass.
    '''

    def __init__(self):
        # Initialize the list of masses from lectionary.xml.
        self._masses = []
        doc = xml.dom.minidom.parse('lectionary.xml')
        try:
            # Decode the year-specific masses.
            for year_node in _children(doc.documentElement, 'year'):
                year_id = _attr(year_node, 'id')
                masses = self._decode_year(year_node)
                for mass in masses:
                    mass.year = year_id
                self._masses.extend(masses)

            # Decode the masses that are not year-specific.
            everyYear_node = _firstChild(doc.documentElement, 'everyYear')
            self._fixedDateMasses = self._decode_everyYear(everyYear_node)
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
    def fixedDateMasses(self):
        '''
        All the fixed-date masses as a list.
        '''

        return self._fixedDateMasses

    def findMass(self, uniqueID):
        '''
        Return the mass having `uniqueID`, otherwise return ``None``.
        '''

        for mass in self._masses:
            if mass.uniqueID == uniqueID:
                return mass
        return None

    def _decode_year(self, year_node):
        '''
        Decode a <year> element and return all its masses as a
        list.
        '''

        result = []
        for season_node in _children(year_node, 'season'):
            masses = self._decode_season(season_node)
            result.extend(masses)
        return result

    def _decode_season(self, season_node):
        '''
        Decode a <season> element and return all its masses as a
        list.
        '''

        result = []
        for mass_node in _children(season_node, 'mass'):
            mass = self._decode_mass(mass_node)
            result.append(mass)
        return result

    def _decode_everyYear(self, everyYear_node):
        '''
        Decode a <everyYear> element and return all its masses
        as a list.
        '''

        result = []
        for mass_node in _children(everyYear_node, 'mass'):
            mass = self._decode_mass(mass_node)
            result.append(mass)
        return result

    def _decode_mass(self, mass_node):
        '''
        Decode a single <mass> element and return it as a
        :class:`Mass` object.
        '''

        date = _attr(mass_node, 'date', None)
        if date is not None:
            month, day = date.split('-')
            date = int(month), int(day)

        name = _attr(mass_node, 'name')

        readings = []
        for reading_node in _children(mass_node, 'reading'):
            readings.append(self._decode_reading(reading_node))

        return Mass(name, readings, date)

    def _decode_reading(self, reading_node):
        '''
        Decoe a single <reading> element and return it as a string.
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

def _children(parent_node, localName):
    '''
    Return all children of `parent_node` having `localName`.
    '''

    result_nodes = []
    for child_node in parent_node.childNodes:
        if child_node.localName == localName:
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
            d = d + datetime.timedelta(
                days=6 - d.weekday())
            count -= 1
        else:
            d = d - datetime.timedelta(
                days=d.weekday() + 1)
            count += 1

    # Now that we are on a Sunday, the rest of the way is simple.
    return d + datetime.timedelta(weeks=count)

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

    # Isolate the year (if any) and the normal name substring.
    year = None
    if len(slash_tokens) == 2:
        year, normalNameSubstring = slash_tokens
        if year.lower() not in ('a', 'b', 'c'):
            raise MalformedQueryError(
                query,
                'Year is "%s", but must be one of A, B, or C (in either case)!' % (
                    year))
    elif len(slash_tokens) == 1:
        normalNameSubstring = slash_tokens[0]

    # Collect all matches and return them.
    def isMatch(mass):
        '''
        Return ``True`` if `mass` has a matching `year` and contains
        `normalNameSubstring` within its `normalName`.
        '''

        return (mass.year == year) and \
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
        for subreading in reading.split(' or '):
            readings[subreading] = bible.getVerses(subreading)
    return mass.name, readings

def main():
    '''
    The command-line interface.
    '''

    # If the user provided no arguments, print help and quit.
    if len(sys.argv) == 1:
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

_lectionary = OFSundayLectionary()

if __name__ == '__main__':
    main()
