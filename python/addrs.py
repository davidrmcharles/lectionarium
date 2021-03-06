#!/usr/bin/env python
'''
For parsing the *numerical* portion of a scripture citation

For example, things like:

#. ``3:16``,
#. ``20:1-10``, and
#. ``1:2-3:4,6``.

We model the first example as a single address (:class:`Addr`) and the
second example as an address range (:class:`AddrRange`).

The presence of a comma makes the third example a *sequence*.  The
first part of the sequence, ``1:2-3``, being an address range
(:class:`AddrRange`).  And, the second part of the sequence, ``6``
being a single address (:class:`Addr`).

Parsing a full citation including the name of a book is the
responsibility of the :mod:`citations` module.

Summary of Library Interface
======================================================================

* :func:`parse` - Parse the *numerical* portion of a citation
* :class:`Addr` - A single address (chapter, verse, or chapter and verse)
* :class:`AddrRange` - An inclusive range of addresses
* :class:`ParsingError` - An exception occurred in :func:`parse`

Reference
======================================================================
'''

# Standard imports:
import string
import sys

class Addr(object):
    '''
    A single location (chapter or verse)

    This can be a single value that represents either a chapter or a
    verse (depending upon context).  Or, it can be a pair of values
    that definitely represents a chapter and verse.
    '''

    def __init__(self, first, second=None):
        self.first = first
        try:
            self.first = int(first)
        except ValueError:
            if len(self.first) > 1:
                raise

        self.second = second
        if second is not None:
            try:
                self.second = int(second)
            except ValueError:
                if len(self.second) > 1:
                    raise

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
            return '%s' % str(self.first)
        else:
            return '%s:%s' % (str(self.first), str(self.second))

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

    Any :class:`Exception` raises :class:`ParsingError` with the
    original cause within.
    '''

    try:
        return _Parser().parse(token)
    except Exception as e:
        raise ParsingError(token, e), None, sys.exc_info()[2]

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
                'Non-string (%s, %s) passed to addrs.parse()!' % (
                    type(token), token))

    def _rejectEmptyString(self, token):
        if len(token) == 0:
            raise ValueError(
                'Empty/whitespace-only string passed to addrs.parse()!')

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
            return Addr(self._chapterIndex, token)
        else:
            return Addr(token)

    def _createAddrFromTokenPair(self, firstToken, secondToken):
        self._chapterIndex = firstToken
        return Addr(firstToken, secondToken)

class ParsingError(Exception):
    '''
    An :class:`Exception` occurred in a call to :func:`parse`.
    '''

    def __init__(self, token, cause):
        self.token = token
        self.cause = cause

    def __str__(self):
        return 'addrs.ParsingError: %s\nCause: %s' % (
            self.token, self.cause)
