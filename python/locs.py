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

    # Fail if `token` is not a string.
    if not isinstance(token, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to locs.parse()!' % (
                type(token), token))

    token.strip()
    if len(token) == 0:
        raise ValueError(
            'Empty/whitespace-only string passed to locs.parse()!')

    chapterIndex = None

    # Parse each of the comma-separated tokens to a list of locations.
    # There can be an arbitrary number of these.
    locs = []
    comma_tokens = token.split(',')
    for comma_token in comma_tokens:
        # Parse each of the hyphen-separated subtokens within the
        # comma-separated token to a list of locations.  There may be
        # only one or two of these subtokens.
        hyphen_tokens = comma_token.split('-')
        if len(hyphen_tokens) > 2:
            raise ValueError(
                'Too many hyphens in token "%s"!' % comma_token)

        addrs = []
        for hyphen_token in hyphen_tokens:
            # Parse each of the colon-separated subtokens within the
            # hyphen-separated token to a list of addrs.  There may be
            # only one or two of these subtokens.
            colon_tokens = hyphen_token.split(':')
            if len(colon_tokens) > 2:
                raise ValueError(
                    'Too many colons in token "%s"!' % hyphen_token)

            # TODO: Eventually we'll have to locations with trailing
            # letters.  For the moment, we'll strip them off.
            colon_tokens = [
                token.rstrip(string.lowercase)
                for token in colon_tokens
                ]

            if len(colon_tokens) == 1:
                # There are no colons in this subtoken.  Reuse the
                # last chapterIndex we've seen (if there is one).
                # Otherwise, generate an address without a
                # chapterIndex.
                if chapterIndex is not None:
                    addrs.append(Addr(int(chapterIndex), int(colon_tokens[0])))
                else:
                    addrs.append(Addr(int(colon_tokens[0])))

            elif len(colon_tokens) == 2:
                # This token has exactly one colon.  Generate a
                # two-dimensional addresss and remember the
                # chapterIndex for later.
                first, second = colon_tokens
                addrs.append(Addr(int(first), int(second)))
                chapterIndex = first

        # If parsing the hyphenated subtokens generated a single
        # address, add it to the locs as-is.  Otherwise, if parsing
        # the hyphenated subtokens generated two addrs, wrap them in a
        # range.
        if len(addrs) == 1:
            locs.extend(addrs)
        elif len(addrs) == 2:
            first, second = addrs
            locs.append(AddrRange(first, second))

    return locs
