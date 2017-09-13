#!/usr/bin/env python
'''
The Lectionary of the Roman Rite

* :class:`Celebration`
* :class:`OFSundayLectionary`
'''

import xml.dom.minidom

class Celebration(object):
    '''
    A single liturgical event
    '''

    def __init__(self, name, readings, date=None):
        self._name = name
        self._readings = readings
        self._date = date

class OFSundayLectionary(object):
    '''
    The Ordinary Form Lectionary for Sundays
    '''

    def __init__(self):
        self._celebrations = []
        doc = xml.dom.minidom.parse('lectionary.xml')
        for year_node in _children(doc.documentElement, 'year'):
            self._celebrations.extend(self._decode_year(year_node))
        majorFeasts_node = _firstChild(doc.documentElement, 'majorFeasts')
        self._celebrations.extend(self._decode_majorFeasts(majorFeasts_node))

    def _decode_year(self, year_node):
        '''
        Decode a <year> element and return all its celebrations as a
        list.
        '''

        result = []
        for season_node in _children(year_node, 'season'):
            result.extend(self._decode_season(season_node))
        return result

    def _decode_season(self, season_node):
        '''
        Decode a <season> element and return all its celebrations as a
        list.
        '''

        result = []
        for celebration_node in _children(season_node, 'celebration'):
            celebration = self._decode_celebration(celebration_node)
            result.append(celebration)
        return result

    def _decode_majorFeasts(self, majorFeasts_node):
        '''
        Decode a <majorFeasts> element and return all its celebrations
        as a list.
        '''

        result = []
        for celebration_node in _children(majorFeasts_node, 'celebration'):
            celebration = self._decode_celebration(celebration_node)
            result.append(celebration)
        return result

    def _decode_celebration(self, celebration_node):
        '''
        Decode a single <celebration> element and return it as a
        :class:`Celebration` object.
        '''

        date = _attr(celebration_node, 'date', None)
        name = _attr(celebration_node, 'name')

        readings = []
        for reading_node in _children(celebration_node, 'reading'):
            readings.append(self._decode_reading(reading_node))

        return Celebration(name, readings, date)

    def _decode_reading(self, reading_node):
        '''
        Decoe a single <reading> element and return it as a string.
        '''

        return _text(reading_node)

# Now, let's fix DOM:

def _text(node):
    '''
    The text content of a `node`
    '''

    return node.nodeValue

def _firstChild(parent_node, localName):
    '''
    The first child of `parent_node` having `localName`.
    '''

    for child_node in parent_node.childNodes:
        if child_node.localName == localName:
            return child_node
    return None

def _children(parent_node, localName):
    '''
    All children of `parent_node` having `localName`.
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
    The value of the attribute of `node` having `localName`.
    '''

    if not node.hasAttribute(localName):
        if ifMissing is RaiseIfAttrIsMissing:
            raise MissingAttrException()
        else:
            return ifMissing
    return node.getAttribute(localName)

