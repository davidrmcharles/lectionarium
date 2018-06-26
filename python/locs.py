#!/usr/bin/env python
'''
For parsing the numerical portion of a scripture citation (locations)

This is where we deal with the numerical portion of a scripture
citation.  For example, things like:

#. ``3:16``,
#. ``20:1-10``, and
#. ``1:2-3:4,6``.

The first and second examples are locations.  We model the first as an
:class:`Addr` and the second as an :class:`AddrRange`.

The presence of a comma makes the third example a sequence of
locations, the first being an :class:`AddrRange` and the second being
an :class:`Addr`.

Summary of Library Interface
======================================================================

* :func:`parse` - Parse a single locations token
* :class:`Addr` - A single address (chapter or verse)
* :class:`AddrRange` - An inclusive range of addresses

Reference
======================================================================
'''

# Standard imports:
import string

class Addr(object):
    '''
    A single location (chapter or verse)

    This can be a single value that represents either a chapter or a
    verse (depending upon context).  Or, it can be a pair of values
    that definitely represents a chapter and verse.
    '''

    def __init__(self, first, second=None):
        self.first = first
        self.second = second

    @property
    def dimensionality(self):
        '''
        ``1`` for a one-dimensional address, and ``2`` for
        two-dimensional addresses.
        '''

        return 1 if self.second is None else 2

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.first != other.first:
            return False
        if self.second != other.second:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        if self.first != other.first:
            return True
        if self.second != other.second:
            return True
        return False

    def __hash__(self):
        return hash((self.first, self.second))

    def __str__(self):
        if self.second is None:
            return '%d' % self.first
        else:
            return '%d:%d' % (self.first, self.second)

    def __repr__(self):
        if self.second is None:
            return '<bible.Addr object "%s" at 0x%x>' % (
                self.first, id(self))
        else:
            return '<bible.Addr object "%s:%s" at 0x%x>' % (
                self.first, self.second, id(self))

class AddrRange(object):
    '''
    An inclusive range of addresses

    The range is inclusive and bounded by two :class:`Addr` objects.
    '''

    def __init__(self, first, last):
        self.first = first
        self.last = last

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.first != other.first:
            return False
        if self.last != other.last:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        if self.first != other.first:
            return True
        if self.last != other.last:
            return True
        return False

    def __hash__(self):
        return hash((self.first, self.last))

    def __str__(self):
        return '%s-%s' % (self.first, self.last)

    def __repr__(self):
        return '<bible.AddrRange object "%s-%s" at 0x%x>' % (
            self.first, self.last, id(self))

def parse(token):
    '''
    Parse a single locations token and return it as a list of
    :class:`Addr` and :class:`AddrRange` objects.
    '''

    return _Parser().parse(token)

class _Parser(object):

    def parse(self, token):
        self._rejectNonString(token)
        token = token.strip()
        self._rejectEmptyString(token)
        return self._parseCommaSeparatedSubtokens(token)

    def _parseCommaSeparatedSubtokens(self, token):
        self._chapterIndex = None
        return [
            self._parseHyphenSeparatedSubtokens(subtoken)
            for subtoken in token.split(',')
            ]

    def _parseHyphenSeparatedSubtokens(self, token):
        addrs = [
            self._parseColonSeparatedTokens(subtoken)
            for subtoken in self._splitTokenAtHyphens(token)
            ]
        if len(addrs) == 1:
            return addrs[0]
        elif len(addrs) == 2:
            first, second = addrs
            return AddrRange(first, second)

    def _parseColonSeparatedTokens(self, token):
        subtokens = self._splitTokenAtColons(token)
        if len(subtokens) == 1:
            return self._createAddrFromSingleToken(subtokens[0])
        elif len(subtokens) == 2:
            first, second = subtokens
            return self._createAddrFromTokenPair(first, second)

    def _rejectNonString(self, token):
        if not isinstance(token, basestring):
            raise TypeError(
                'Non-string (%s, %s) passed to locs.parse()!' % (
                    type(token), token))

    def _rejectEmptyString(self, token):
        if len(token) == 0:
            raise ValueError(
                'Empty/whitespace-only string passed to locs.parse()!')

    def _splitTokenAtHyphens(self, token):
        subtokens = token.split('-')
        if len(subtokens) > 2:
            raise ValueError(
                'Too many hyphens in token "%s"!' % token)
        return subtokens

    def _splitTokenAtColons(self, token):
        subtokens = token.split(':')
        if len(subtokens) > 2:
            raise ValueError(
                'Too many colons in token "%s"!' % token)
        subtokens = self._stripTrailingLettersFromTokens(subtokens)
        return subtokens

    def _stripTrailingLettersFromTokens(self, tokens):
        # TODO: This is a temporary expedient!
        return [
            token.rstrip(string.lowercase)
            for token in tokens
            ]

    def _createAddrFromSingleToken(self, token):
        if self._chapterIndex is not None:
            return Addr(int(self._chapterIndex), int(token))
        else:
            return Addr(int(token))

    def _createAddrFromTokenPair(self, firstToken, secondToken):
        self._chapterIndex = firstToken
        return Addr(int(firstToken), int(secondToken))
