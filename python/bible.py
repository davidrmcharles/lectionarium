#!/usr/bin/env python
'''
Represents the Canon of Scripture

* :func:`parseBibleRef` - TODO
* :func:`_parseBookToken` - TODO
* :class:`Point`
* :class:`Range`
* :func:`_parseChapterAndVerseToken`
'''

def parseBibleRef(text):
    '''
    Parse a human-readable bible refrence to an object representation.
    '''

    return  # TODO

def _parseBookToken(token):
    '''
    Parse a book token to a normalized book name.
    '''

    return  # TODO

class Point(object):
    '''
    Represents a single place in some scriptural book.

    This can be a single value that represents either a chapter or a
    verse depending upon context.  Or, it can be a pair of values that
    most definitely represents both a chapter and verse.
    '''

    def __init__(self, first, second=None):
        self.first = first
        self.second = second

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
            return '<bible.Point object "%s" at 0x%x>' % (
                self.first, id(self))
        else:
            return '<bible.Point object "%s:%s" at 0x%x>' % (
                self.first, self.second, id(self))

class Range(object):
    '''
    Represents an range of text in some scriptural book.

    The range is inclusive, and bounded by two :class:`Point` objects.
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
        return '<bible.Range object "%s-%s" at 0x%x>' % (
            self.first, self.last, id(self))

def _parseChapterAndVerseToken(token):
    '''
    Parse a chapter and verse token to a list of points and ranges.
    '''

    # Fail if `token` is not a string.
    if not isinstance(token, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to _parseChapterAndVerseToken()!' % (
                type(token), token))

    token.strip()
    if len(token) == 0:
        raise ValueError(
            'Empty/whitespace-only string passed to'
            ' _parseChapterAndVerseToken()!')

    prefix = None

    # Parse each of the comma-separated tokens to a list of points and
    # ranges.  There can be an arbitrary number of these.
    result = []
    comma_tokens = token.split(',')
    for comma_token in comma_tokens:
        # Parse each of the hyphen-separated subtokens within the
        # comma-separated token to a list of points and ranges.  There
        # may be only one or two of these subtokens.
        hyphen_tokens = comma_token.split('-')
        if len(hyphen_tokens) > 2:
            raise ValueError('Too many hyphens!')

        points = []
        for hyphen_token in hyphen_tokens:
            # Parse each of the colon-separated subtokens within the
            # hyphen-separated tken to a list of points.  There may be
            # only one or two of these subtokens.
            colon_tokens = hyphen_token.split(':')
            if len(colon_tokens) > 2:
                raise ValueError('Too many colons!')

            if len(colon_tokens) == 1:
                # There are no colons in this subtoken.  Reuse the
                # last prefix we've seen (if there is one).
                # Otherwise, generate a point without a prefix.
                if prefix is not None:
                    points.append(Point(int(prefix), int(colon_tokens[0])))
                else:
                    points.append(Point(int(colon_tokens[0])))

            elif len(colon_tokens) == 2:
                # This token has exactly point colon.  Generate a
                # two-dimensional point and remember the prefix for
                # later.
                first, second = colon_tokens
                points.append(Point(int(first), int(second)))
                prefix = first

        # If parsing the hyphenated subtokens generated a single
        # point, add it to the result as-is.  Otherwise, if parsing
        # the hyphenated subtokens generated two points, wrap them in
        # a range.
        if len(points) == 1:
            result.extend(points)
        elif len(points) == 2:
            first, second = points
            result.append(Range(first, second))

    return result
