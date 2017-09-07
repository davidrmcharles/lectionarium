#!/usr/bin/env python
'''
Represents the Canon of Scripture

* :func:`parseBibleRef` - TODO
* :class:`Book`
* :class:`Bible`
* :func:`_parseBookToken`
* :class:`Point`
* :class:`Range`
* :func:`_parseChapterAndVerseToken`
'''

def parseBibleRef(text):
    '''
    Parse a human-readable bible refrence to an object representation.
    '''

    return  # TODO

class Book(object):
    '''
    Represents a single 'book' of the scriptures.
    '''

    def __init__(self, name, *abbreviations):
        self.name = name
        self.abbreviations = list(abbreviations)

    @property
    def normalName(self):
        '''
        The normalized name for the book:

        * Full-book name (no abbreviations)
        * All lowercase
        * No interior whitespace
        '''

        return ''.join(self.name.lower().split())

    @property
    def normalAbbreviations(self):
        '''
        The abbreviations for the book, normalized.

        (Same rules as for ``normalName``.
        '''

        return [
            ''.join(abbreviation.lower().split())
            for abbreviation in self.abbreviations
            ]

    def matchesToken(self, token):
        '''
        Return ``True`` if `token` can refer to this book.
        '''

        token = ''.join(token.lower().split())
        return token in [self.normalName] + self.normalAbbreviations

    def __str__(self):
        return '%s (%s)' % (
            self.name,
            ', '.join(self.abbreviations))

    def __repr__(self):
        return '<bible.Book object "%s" at 0x%x>' % (
            self, id(self))

class Bible(object):
    '''
    Represents the Canon of Scripture
    '''

    def __init__(self):
        self._otBooks = [
            Book('Genesis', 'Gn'),
            Book('Exodus', 'Ex'),
            Book('Leviticus', 'Lv'),
            Book('Numbers', 'Nm'),
            Book('Deuteronomy', 'Dt'),
            Book('Joshua', 'Jos'),
            Book('Judges', 'Jgs'),
            Book('Ruth', 'Ru'),
            Book('1 Samuel', '1 Sm'),
            Book('2 Samuel', '2 Sm'),
            Book('1 Kings', '1 Kgs'),
            Book('2 Kings', '2 Kgs'),
            Book('1 Chronicles', '1 Chr'),
            Book('2 Chronicles', '2 Chr'),
            Book('Ezra', 'Ezr'),
            Book('Nehemiah', 'Neh'),
            Book('Tobit', 'Tb'),
            Book('Judith', 'Jdt'),
            Book('Esther', 'Est'),
            Book('1 Maccabees', '1 Mc'),
            Book('2 Maccabees', '2 Mc'),
            Book('Job', 'Jb'),
            Book('Psalms', 'Ps', 'Pss'),
            Book('Proverbs', 'Prv'),
            Book('Ecclesiastes', 'Eccl'),
            Book('Song of Songs', 'Song', 'Sg'),
            Book('Wisdom', 'Wis'),
            Book('Sirach', 'Sir'),
            Book('Isaiah', 'Is'),
            Book('Jeremiah', 'Jr'),
            Book('Lamentations', 'Lam'),
            Book('Baruch', 'Bar'),
            Book('Ezekiel', 'Ez'),
            Book('Daniel', 'Dn'),
            Book('Hosea', 'Hos'),
            Book('Joel', 'Jl'),
            Book('Amos', 'Am'),
            Book('Obadiah', 'Ob'),
            Book('Jonah', 'Jon'),
            Book('Michah', 'Mi'),
            Book('Nahum', 'Na'),
            Book('Habakkuk', 'Hb'),
            Book('Zephaniah', 'Zep'),
            Book('Haggai', 'Hg'),
            Book('Zechariah', 'Zec'),
            Book('Malachi', 'Mal'),
            ]

        self._ntBooks = [
            Book('Matthew', 'Mt'),
            Book('Mark', 'Mk'),
            Book('Luke', 'Lk'),
            Book('John', 'Jn'),
            Book('Acts', 'Acts'),
            Book('Romans', 'Rom'),
            Book('1 Corinthians', '1 Cor'),
            Book('2 Corinthians', '2 Cor'),
            Book('Galatians', 'Gal'),
            Book('Ephesians', 'Eph'),
            Book('Philippians', 'Phil'),
            Book('Colossians', 'Col'),
            Book('1 Thessalonians', '1 Thes'),
            Book('2 Thessalonians', '2 Thes'),
            Book('1 Timothy', '1 Tm'),
            Book('2 Timothy', '2 Tm'),
            Book('Titus', 'Ti'),
            Book('Philemon', 'Phlm'),
            Book('Hebrews', 'Heb'),
            Book('James', 'Jas'),
            Book('1 Peter', '1 Pt'),
            Book('2 Peter', '2 Pt'),
            Book('1 John', '1 Jn'),
            Book('2 John', '2 Jn'),
            Book('3 John', '3 Jn'),
            Book('Jude', 'Jude'),
            Book('Revelation', 'Rv'),
            ]

        self._allBooks = self._otBooks + self._ntBooks

    @property
    def allBooks(self):
        '''
        All books.
        '''

        return self._allBooks

    def findBook(self, token):
        '''
        Find and return the book that goes with `token`.
        '''

        for book in self._allBooks:
            if book.matchesToken(token):
                return book
        return None

    @property
    def allBookAbbreviations(self):
        '''
        All book abbreviations in a single, flattened list.
        '''

        return itertools.chain.from_iterable(
            book.abbreviations for book in self._allBooks)

_bible = Bible()

def _parseBookToken(token):
    '''
    Parse a book token in any form to a normalized form:

    * Full-book name (no abbreviation)
    * All lowercase
    * Interior whitespace removed
    '''

    return _bible.findBook(token).normalName

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
