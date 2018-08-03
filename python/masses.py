#!/usr/bin/env python
'''
Masses with their readings

* :func:`getSundayMasses`
* :func:`getWeekdayMasses`
* :func:`getSpecialMasses`
* :class:`Mass` - A single mass (or Good Friday)
* :class:`Reading` - A single reading
'''

# Stnadard imports:
import calendar
import inspect
import os
import re
import xml.dom.minidom

# Local imports:
import citations
import domtools

_thisFilePath = inspect.getfile(inspect.currentframe())
_thisFolderPath = os.path.abspath(os.path.dirname(_thisFilePath))
_rootFolderPath = os.path.dirname(_thisFolderPath)

def getSundayMasses():
    xmlFilePath = os.path.join(
        _rootFolderPath, 'xml', 'sunday-lectionary.xml')
    doc = xml.dom.minidom.parse(xmlFilePath)
    try:
        return _XMLDecoder.decode_sunday_lectionary(doc.documentElement)
    finally:
        doc.unlink()

def getWeekdayMasses():
    xmlFilePath = os.path.join(
        _rootFolderPath, 'xml', 'weekday-lectionary.xml')
    doc = xml.dom.minidom.parse(xmlFilePath)
    try:
        return _XMLDecoder.decode_weekday_lectionary(doc.documentElement)
    finally:
        doc.unlink()

def getSpecialMasses():
    xmlFilePath = os.path.join(
        _rootFolderPath, 'xml', 'special-lectionary.xml')
    doc = xml.dom.minidom.parse(xmlFilePath)
    try:
        return _XMLDecoder.decode_special_lectionary(doc.documentElement)
    finally:
        doc.unlink()

class _XMLDecoder(object):

    @staticmethod
    def decode_sunday_lectionary(lectionary_node):
        '''
        Decode a <lectionary> element for the Sunday lectionary and
        return all of its masses as a list.
        '''

        result = []
        for season_node in domtools.children(lectionary_node, 'season'):
            result.extend(_XMLDecoder._decode_season(season_node))
        return result

    @staticmethod
    def decode_weekday_lectionary(lectionary_node):
        '''
        Decode the <lectionary> element for the weekday lectionary and
        return all its masses as a list.
        '''

        result = []
        for season_node in domtools.children(lectionary_node, 'season'):
            result.extend(_XMLDecoder._decode_season(season_node))
        return result

    @staticmethod
    def decode_special_lectionary(lectionary_node):
        '''
        Decode the <lectionary> element for the special lectionary
        and return all its masses as a list.
        '''

        result = []
        for mass_node in domtools.children(lectionary_node, 'mass'):
            mass = _XMLDecoder._decode_mass(mass_node)
            result.append(mass)
        return result

    @staticmethod
    def _decode_season(season_node):
        '''
        Decode a <season> element and return all its masses as a
        list.
        '''

        result = []
        seasonid = domtools.attr(season_node, 'id', ifMissing=None)
        for child_node in domtools.children(season_node, ['mass', 'week']):
            if child_node.localName == 'mass':
                mass = _XMLDecoder._decode_mass(child_node)
                mass.seasonid = seasonid
                result.append(mass)
            elif child_node.localName == 'week':
                masses = _XMLDecoder._decode_week(child_node)
                for mass in masses:
                    mass.seasonid = seasonid
                result.extend(masses)
        return result

    @staticmethod
    def _decode_week(week_node):
        '''
        Decode a <week> element and return all its masses as a list.
        '''

        result = []
        for mass_node in domtools.children(week_node, 'mass'):
            mass = _XMLDecoder._decode_mass(mass_node)
            mass.weekid = domtools.attr(week_node, 'id', ifMissing=None)
            result.append(mass)
        return result

    @staticmethod
    def _decode_variation(variation_node):
        '''
        Decode a <variation> element and return all of its readings as a
        list of :class:`Reading` objects.
        '''

        result = []
        cycles = domtools.attr(variation_node, 'cycles', ifMissing=None)
        option_index = 0
        for child_node in domtools.children(
            variation_node, ['reading', 'option']):
            if child_node.localName == 'reading':
                reading = _XMLDecoder._decode_reading(child_node)
                reading.cycles = cycles
                result.append(reading)
            elif child_node.localName == 'option':
                readings = _XMLDecoder._decode_option(child_node)
                for reading_index, reading in enumerate(readings):
                    reading.cycles = cycles
                    reading.optionSetIndex = option_index
                    reading.optionSetSize = len(readings)
                    reading.optionIndex = reading_index
                result.extend(readings)
                option_index += 1
        return result

    @staticmethod
    def _decode_option(option_node):
        '''
        Decode an <option> element and return all its readings as a list.
        '''

        result = []
        for reading_node in domtools.children(option_node, 'reading'):
            result.append(_XMLDecoder._decode_reading(reading_node))
        return result

    @staticmethod
    def _decode_mass(mass_node):
        '''
        Decode a single <mass> element and return it as a
        :class:`Mass` objects.
        '''

        fixedMonth, fixedDay = None, None
        fixedDate = domtools.attr(mass_node, 'date', None)
        if fixedDate is not None:
            fixedMonth, fixedDay = fixedDate.split('-')
            fixedMonth, fixedDay = int(fixedMonth), int(fixedDay)

        weekid = domtools.attr(mass_node, 'weekid', ifMissing=None)
        id_ = domtools.attr(mass_node, 'id', ifMissing=None)
        name = domtools.attr(mass_node, 'name', ifMissing=None)

        readings = []
        option_index = 0
        for child_node in domtools.children(
            mass_node, ['reading', 'option', 'variation']):
            if child_node.localName == 'reading':
                readings.append(_XMLDecoder._decode_reading(child_node))
            elif child_node.localName == 'option':
                optional_readings = _XMLDecoder._decode_option(child_node)
                for optional_reading_index, optional_reading in enumerate(
                    optional_readings):
                    optional_reading.optionSetIndex = option_index
                    optional_reading.optionSetSize = len(optional_readings)
                    optional_reading.optionIndex = optional_reading_index
                readings.extend(optional_readings)
                option_index += 1
            elif child_node.localName == 'variation':
                readings.extend(_XMLDecoder._decode_variation(child_node))

        mass = Mass(readings)
        mass.name = name
        mass.fixedMonth = fixedMonth
        mass.fixedDay = fixedDay
        mass.id = id_
        mass.weekid = weekid
        return mass

    @staticmethod
    def _decode_reading(reading_node):
        '''
        Decode a single <reading> element and return it as a
        :clas:`Reading` object.
        '''

        reading = Reading(domtools.text(reading_node))
        reading.cycles = domtools.attr(reading_node, 'cycles', ifMissing=None)
        reading.altCitation = domtools.attr(reading_node, 'alt', ifMissing=None)
        return reading

class Mass(object):
    '''
    A single mass (or Good Friday, even though it technically isn't a
    mass)
    '''

    def __init__(self, readings):
        self._allReadings = readings
        self._id = None
        self._name = None
        self._fixedMonth = None
        self._fixedDay = None
        self._weekid = None
        self._seasonid = None

    def __str__(self):
        return self._name

    def __repr__(self):
        return '<lectionary.Mass object %s at 0x%x>' % (
            self.fqid, id(self))

    @property
    def allReadings(self):
        '''
        All the readings as a list of :class:`Reading` objects.
        '''

        return self._allReadings

    def applicableReadings(self, sundayCycle, weekdayCycle):
        '''
        Return the readings applicable to `sundayCycle` and
        `weekdayCycle` only.
        '''

        return [
            reading
            for reading
            in self._allReadings
            if reading.isApplicable(sundayCycle, weekdayCycle)
            ]

    @property
    def id(self):
        '''
        A computer-friendly identifier for the mass.

        * All lowercase
        * All spaces converted to hyphens
        * All other non-alphanumeric characters removed
        '''

        if self._id is not None:
            return self._id
        elif self._name is not None:
            return '-'.join(
                re.sub(
                    r'[^[A-Za-z0-9 ]',
                    '',
                    self._name).lower().split())
        else:
            return '%02d-%02d' % (self.fixedMonth, self.fixedDay)

    @id.setter
    def id(self, newValue):
        self._id = newValue

    @property
    def name(self):
        '''
        A human-friendly name for the mass.
        '''

        return self._name

    @property
    def displayName(self):
        '''
        A display-name for the mass.
        '''

        if self.name is not None:
            return self.name
        else:
            return '%s %d' % (
                calendar.month_name[self.fixedMonth],
                self.fixedDay)

    @name.setter
    def name(self, newValue):
        self._name = newValue

    @property
    def fqid(self):
        '''
        A fully-qualified identifier for the mass that builds upon
        ``id``.
        '''

        # Qualify the mass as much as possible.
        tokens = [self.id]
        if self._weekid is not None:
            tokens.insert(0, self._weekid)
        if self._seasonid is not None:
            tokens.insert(0, self._seasonid)
        return '/'.join(tokens)

    @property
    def fixedMonth(self):
        '''
        The month as an ``int``, if this is a fixed-date mass.
        Otherwise, ``None``.
        '''

        return self._fixedMonth

    @fixedMonth.setter
    def fixedMonth(self, newValue):
        self._fixedMonth = newValue

    @property
    def fixedDay(self):
        '''
        The day as an ``int``, if this is a fixed-date mass.
        Otherwise, ``None``.
        '''

        return self._fixedDay

    @fixedDay.setter
    def fixedDay(self, newValue):
        self._fixedDay = newValue

    @property
    def isSunday(self):
        '''
        ``True`` if this is a Sunday mass.
        '''

        return self.id.startswith('sunday')

    @property
    def isSundayInOrdinaryTime(self):
        '''
        ``True`` if this mass is a Sunday in Ordinary Time.
        '''

        return self.isSunday and \
            (self._seasonid == 'ordinary')

    @property
    def weekid(self):
        '''
        A computer-friendly identifier for the week.  Otherwise,
        ``None``.
        '''

        return self._weekid

    @weekid.setter
    def weekid(self, newValue):
        self._weekid = newValue

    @property
    def seasonid(self):
        '''
        A computer-friendly identifier for the season.  Othewise,
        ``None``.
        '''

        return self._seasonid

    @seasonid.setter
    def seasonid(self, newValue):
        self._seasonid = newValue

class Reading(object):
    '''
    A single reading from Sacred Scripture as a citation
    and the conditions surrounding its applicability
    '''

    def __init__(self, citation):
        self._citation = citation
        self._altCitation = None
        self._cycles = None
        self._optionSetIndex = None
        self._optionSetSize = None
        self._optionIndex = None

    @property
    def title(self):
        '''
        The title of the reading.
        '''

        tokens = [citations.parse(self._citation).displayString]

        if self._optionSetIndex is not None:
            tokens.append(
                '(Option %d of %d)' % (
                    self._optionIndex + 1, self._optionSetSize))

        return ' '.join(tokens)

    @property
    def citation(self):
        '''
        The citation for the NAB
        '''

        if self._altCitation is not None:
            return self._altCitation
        return self._citation

    @property
    def altCitation(self):
        '''
        The citation especially for the Clementine Vulgate
        '''

        return self._altCitation

    @altCitation.setter
    def altCitation(self, altCitation):
        self._altCitation = altCitation

    @property
    def cycles(self):
        '''
        The cycles to which a reading applies.  ``None`` if the
        reading applies to all cycles.
        '''

        return self._cycles

    @cycles.setter
    def cycles(self, cycles):
        self._cycles = cycles

    @property
    def optionSetIndex(self):
        '''
        The index of the containing option set, or ``None`` if the
        reading is not optional
        '''

        return self._optionSetIndex

    @optionSetIndex.setter
    def optionSetIndex(self, optionSetIndex):
        self._optionSetIndex = optionSetIndex

    @property
    def optionSetSize(self):
        '''
        The total number of optional readings within its set
        '''

        return self._optionSetSize

    @optionSetSize.setter
    def optionSetSize(self, optionSetSize):
        self._optionSetSize = optionSetSize

    @property
    def optionIndex(self):
        '''
        The index of an optional reading within its set
        '''

        return self._optionIndex

    @optionIndex.setter
    def optionIndex(self, optionIndex):
        self._optionIndex = optionIndex

    def isApplicable(self, sundayCycle, weekdayCycle):
        '''
        ``True`` if this reading applies to the given `sundayCycle`
        and `weekdayCycle`.
        '''

        if self._cycles is None:
            return True
        if sundayCycle is None and weekdayCycle is None:
            return True
        if (sundayCycle is not None) and (sundayCycle in self._cycles):
            return True
        if (weekdayCycle is not None) and (weekdayCycle == self._cycles):
            return True
        return False
