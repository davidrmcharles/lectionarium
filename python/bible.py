#!/usr/bin/env python
'''
Represents the Canon of Scripture

* :class:`Ref`
* :func:`parseRef`
* :func:`_parseBookTokensGreedily`
* :class:`Book`
* :class:`Bible`
* :func:`_parseBookToken`
* :class:`Point`
* :class:`Range`
* :func:`_parseVersesToken`
'''

class Ref(object):
    '''
    Represents a range of text in a particular scriptural book.
    '''

    def __init__(self, book, verses):
        self.book = book
        self.verses = verses

def parseRef(text):
    '''
    Parse a human-readable, single-book bible reference and return the
    result as a :class:`Ref`.
    '''

    # Fail if `text` is not a string.
    if not isinstance(text, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to parseRef()!' % (
                type(text), text))

    # Fail if there are no non-white characters in `text`.
    tokens = text.strip().split()
    if len(tokens) == 0:
        raise ValueError(
            'No non-white characters passed to parseRef()!')

    # Try to parse a book out of the leading tokens in a 'greedy'
    # fashion.
    book, tokensConsumed = _parseBookTokensGreedily(tokens)

    # If there is more than one token remaining, we have too many
    # tokens.
    remainingTokens = tokens[tokensConsumed:]
    if len(remainingTokens) > 1:
        raise ValueError(
            'Extra tokens %s!' % remainingTokens[1:])

    # If there is exactly remaining token, try to parse verses out of
    # it.
    verses = None
    if len(remainingTokens) == 1:
        remainingToken = remainingTokens[0]
        verses = _parseVersesToken(remainingToken)

    return Ref(book, verses)

def _parseBookTokensGreedily(tokens):
    '''
    Return the book represented by the leading tokens and the number
    of tokens consumed.  If no book can be parsed out of the tokens,
    return ``(None, 0)``.

    This function parses in a 'greedy' fashion, trying to consume as
    many tokens as possible.  This is key to parsing 'Song of Songs',
    whose abbreviations include 'Song'.
    '''

    for index in reversed(range(len(tokens))):
        superToken = ''.join(tokens[:index + 1])
        book = _parseBookToken(superToken)
        if book is not None:
            return book, index + 1
    return None, 0

class Book(object):
    '''
    Represents a single scriptural 'book'.
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
    Represents the whole Canon of Scripture.
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

_bible = Bible()

def _parseBookToken(token):
    '''
    Parse a book token in any form to a normalized form:

    * Full-book name (no abbreviation)
    * All lowercase
    * Interior whitespace removed
    '''

    book = _bible.findBook(token)
    if book is None:
        return None
    return book.normalName

class Point(object):
    '''
    Represents a single place in some scriptural book.

    This can be a single value that represents either a chapter or a
    verse (depending upon context).  Or, it can be a pair of values
    that definitely represents a chapter and verse.
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

def _parseVersesToken(token):
    '''
    Parse a chapter and verse token to a list of :class:`Point` and
    :class:`Range` objects.
    '''

    # Fail if `token` is not a string.
    if not isinstance(token, basestring):
        raise TypeError(
            'Non-string (%s, %s) passed to _parseVersesToken()!' % (
                type(token), token))

    token.strip()
    if len(token) == 0:
        raise ValueError(
            'Empty/whitespace-only string passed to'
            ' _parseVersesToken()!')

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
