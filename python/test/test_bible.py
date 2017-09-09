#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible

class getVersesTestCase(unittest.TestCase):

    def test_singleVerse(self):
        expectedVerses = [
            ((3, 14), 'Dixit...')
            ]

        verses = bible.getVerses('ex 3:14')
        self.assertEqual(1, len(verses))

        verseAddr, verseText = verses[0]
        self.assertEqual((3, 14), verseAddr)

    def test_rangeOfVerses(self):
        expectedVerses = [
            ((11, 25), 'Dixit...'),
            ((11, 26), 'et...')
            ]

        verses = bible.getVerses('john 11:25-26')
        self.assertEqual(2, len(verses))

        verseAddr, verseText = verses[0]
        self.assertEqual((11, 25), verseAddr)

        verseAddr, verseText = verses[1]
        self.assertEqual((11, 26), verseAddr)

class parseRefTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            bible.parseRef(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            bible.parseRef('')

    def test_singleTokenBookOnly(self):
        ref = bible.parseRef('gn')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(None, ref.locs)

    def test_twoTokenBookOnly(self):
        ref = bible.parseRef('1 samuel')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(None, ref.locs)

    def test_twoTokenBookPlus(self):
        ref = bible.parseRef('1 samuel 1:2-3:4')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 2), bible.Addr(3, 4))],
            ref.locs)

    def test_songOfSongs(self):
        '''
        This case requires that the parsing of the book tokens be
        'greedy'.

        Because 'song' is both an abbreviations for this book and the
        first word in its full name, a non-greedy approach to
        parsing-out the name of the book will leave too many tokens
        behind.
        '''

        ref = bible.parseRef('song of songs 1:2-3:4')
        self.assertEqual('songofsongs', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 2), bible.Addr(3, 4))],
            ref.locs)

    def test_syntheticAndMinimal(self):
        '''
        This is exact same series appears in parseVersesTokenTestCase,
        but here we add the name of a book.
        '''

        ref = bible.parseRef('gn 1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual([bible.Addr(1)], ref.locs)

        ref = bible.parseRef('gn 1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1), bible.Addr(2))],
            ref.locs)

        ref = bible.parseRef('gn 1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1), bible.Addr(3)],
            ref.locs)

        ref = bible.parseRef('gn 1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1), bible.Addr(2)), bible.Addr(4)],
            ref.locs)

        ref = bible.parseRef('gn 1:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1, 1)],
            ref.locs)

        ref = bible.parseRef('gn 1:1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(1, 2))],
            ref.locs)

        ref = bible.parseRef('gn 1:1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(1, 3)],
            ref.locs)

        ref = bible.parseRef('gn 1:1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(1, 2)), bible.Addr(1, 4)],
            ref.locs)

        ref = bible.parseRef('gn 1:1-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(2, 1))],
            ref.locs)

        ref = bible.parseRef('gn 1:1,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(2, 1)],
            ref.locs)

        ref = bible.parseRef('gn 1:1,3,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(1, 3), bible.Addr(2, 1)],
            ref.locs)

        ref = bible.parseRef('gn 1:1,3-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [bible.Addr(1, 1), bible.AddrRange(bible.Addr(1, 3), bible.Addr(2, 1))],
            ref.locs)

class parseBookTokensGreedilyTestCase(unittest.TestCase):

    def test_1(self):
        bible._parseBookTokensGreedily(['foo', 'bar', 'zod'])

class BookTestCase(unittest.TestCase):

    # Here is a phony book with chapters, fabricated from excerpts of
    # genesis.txt.
    bookWithChaptersText = u'''\
1:1 In principio creavit Deus cælum et terram.
1:2 Terra autem erat inanis et vacua...
1:3 Dixitque Deus...
2:1 Igitur perfecti sunt cæli et terra...
2:2 Complevitque Deus die septimo opus suum quod fecerat...
2:3 Et benedixit diei septimo...
3:1 Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...
3:2 Cui respondit mulier...
3:3 de fructu vero ligni quod est in medio paradisi...
'''

    # Here is a phony book *without* chapters, fabricated from
    # excerpts of jude.txt.
    bookWithoutChaptersText = u'''\
1:1 Judas Jesu Christi servus...
1:2 Misericordia vobis...
1:3 Carissimi...
'''

    def test_normalName(self):
        self.assertEqual('genesis', bible.Book('Genesis', ['Gn']).normalName)

    def test_noramlAbbreviations(self):
        self.assertEqual(['gn'], bible.Book('Genesis', ['Gn']).normalAbbreviations)

    def test_matchesToken(self):
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('Genesis'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('genesis'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GENESIS'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GeNesIs'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('Gn'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('gn'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GN'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('gN'))

    def test_str(self):
        self.assertEqual('Genesis (Gn)', str(bible.Book('Genesis', ['Gn'])))

    def test_getVerse(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should return all of chapter 1.
        result = bookWithChapters.getVerse(bible.Addr(1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should return all of chapter 2.
        result = bookWithChapters.getVerse(bible.Addr(2))
        self.assertEqual(
            result, [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        # This should return verse 1:1.
        result = bookWithChapters.getVerse(bible.Addr(1, 1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should return verse 1:2.
        result = bookWithChapters.getVerse(bible.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should return verse 2:3:
        result = bookWithChapters.getVerse(bible.Addr(2, 3))
        self.assertEqual(
            result, [
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        bookWithoutChapters = bible.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.loadTextFromString(self.bookWithoutChaptersText)

        # This should return only verse 1.
        result = bookWithoutChapters.getVerse(bible.Addr(1))
        self.assertEqual(
            result, [
                (1, u'Judas Jesu Christi servus...'),
                ])

        # This should return only verse 2.
        result = bookWithoutChapters.getVerse(bible.Addr(2))
        self.assertEqual(
            result, [
                (2, u'Misericordia vobis...'),
                ])

        # A request for 1:2 should also return verse 2, but the
        # 'address' should have the shape of the reference.
        result = bookWithoutChapters.getVerse(bible.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Misericordia vobis...'),
                ])

    def test_getRangeOfVerses(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # Here are a few ranges entirely within the same chapter,
        # starting with 1:1-1:3.
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(1, 1), bible.Addr(1, 3)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...')],
            verses)

        # 2:1-2:2
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(2, 1), bible.Addr(2, 2)))
        self.assertEqual(
            [((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...')],
            verses)

        # 3:2-3:3
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(3, 2), bible.Addr(3, 3)))
        self.assertEqual(
            [((3, 2), u'Cui respondit mulier...'),
             ((3, 3), u'de fructu vero ligni quod est in medio paradisi...')],
            verses)

        # Here are some ranges in adjacent chapters, starting with
        # 1:1-2:1:
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(1, 1), bible.Addr(2, 1)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...')],
            verses)

        # 2:2-3:2
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(2, 2), bible.Addr(3, 2)))
        self.assertEqual(
            [((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...'),
             ((3, 2), u'Cui respondit mulier...')],
            verses)

        # Finally, here is the case of a book in the middle: 1:3-3:1:
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(1, 3), bible.Addr(3, 1)))
        self.assertEqual(
            [((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...')],
            verses)

        # Now let's see if we can handle whole-chapter ranges like
        # 1-2:
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(1), bible.Addr(2)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...')],
            verses)

        # What about a range that begins on a chapter, but ends on a
        # verse, like 1-2:2:
        verses = bookWithChapters.getRangeOfVerses(bible.AddrRange(bible.Addr(1), bible.Addr(2, 2)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...')],
            verses)

        # Now, how to express a range that begins on a verse and ends
        # at the end of a chapter?  1:2-3 won't do!  perhaps something
        # like 1:2--3?  But, we can't parse that yet.

        # TODO: Finally, before this method can be fully tested, we
        # must handle the case of a book with chapters.

    def test_allVersesInChapter(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            bookWithChapters._allVersesInChapter(1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should arrive at all verses in chapter 2.
        self.assertEqual(
            bookWithChapters._allVersesInChapter(2), [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        bookWithoutChapters = bible.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.loadTextFromString(self.bookWithoutChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            bookWithoutChapters._allVersesInChapter(1), [
                ((1, 1), u'Judas Jesu Christi servus...'),
                ((1, 2), u'Misericordia vobis...'),
                ((1, 3), u'Carissimi...'),
                ])

    def test_lastVersesInChapter(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            bookWithChapters._lastVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            bookWithChapters._lastVersesInChapter(1, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            bookWithChapters._lastVersesInChapter(1, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_firstVersesInChapter(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            bookWithChapters._firstVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            bookWithChapters._firstVersesInChapter(1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            bookWithChapters._firstVersesInChapter(1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_middleVersesInChapter(self):
        bookWithChapters = bible.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should produce all three verses of chapter one.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce only verse 1.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce only verse 2.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 2, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce only verse 3.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 3, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1-2.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce verses 2-3.
        self.assertEqual(
            bookWithChapters._middleVersesInChapter(1, 2, 3), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

class BibleTestCase(unittest.TestCase):

    def test_findBook(self):
        self.assertIsNotNone(bible._bible.findBook('Genesis'))
        self.assertIsNotNone(bible._bible.findBook('genesis'))
        self.assertIsNotNone(bible._bible.findBook('GENESIS'))
        self.assertIsNotNone(bible._bible.findBook('GeNeSIs'))

        self.assertIsNotNone(bible._bible.findBook('Gn'))
        self.assertIsNotNone(bible._bible.findBook('gn'))
        self.assertIsNotNone(bible._bible.findBook('GN'))
        self.assertIsNotNone(bible._bible.findBook('gN'))

class AddrTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.Addr(1) == bible.Addr(1))
        self.assertTrue(bible.Addr(2) == bible.Addr(2))

    def test_str(self):
        self.assertEqual('1', str(bible.Addr(1)))
        self.assertEqual('2', str(bible.Addr(2)))
        self.assertEqual('1:2', str(bible.Addr(1, 2)))

class RangeTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.AddrRange(1, 2) == bible.AddrRange(1, 2))
        self.assertTrue(
            bible.AddrRange(bible.Addr(1), bible.Addr(2)) == \
                bible.AddrRange(bible.Addr(1), bible.Addr(2)))

    def test_str(self):
        self.assertEqual(
            '1:2-3:4', str(bible.AddrRange(bible.Addr(1, 2), bible.Addr(3, 4))))

class parseVersesTokenTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            bible._parseLocsToken(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            bible._parseLocsToken('')

    def test_syntheticAndMinimal(self):
        self.assertEqual(
            [bible.Addr(1)],
            bible._parseLocsToken('1'))
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1), bible.Addr(2))],
            bible._parseLocsToken('1-2'))
        self.assertEqual(
            [bible.Addr(1), bible.Addr(3)],
            bible._parseLocsToken('1,3'))
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1), bible.Addr(2)), bible.Addr(4)],
            bible._parseLocsToken('1-2,4'))
        self.assertEqual(
            [bible.Addr(1, 1)],
            bible._parseLocsToken('1:1'))
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(1, 2))],
            bible._parseLocsToken('1:1-2'))
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(1, 3)],
            bible._parseLocsToken('1:1,3'))
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(1, 2)), bible.Addr(1, 4)],
            bible._parseLocsToken('1:1-2,4'))
        self.assertEqual(
            [bible.AddrRange(bible.Addr(1, 1), bible.Addr(2, 1))],
            bible._parseLocsToken('1:1-2:1'))
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(2, 1)],
            bible._parseLocsToken('1:1,2:1'))
        self.assertEqual(
            [bible.Addr(1, 1), bible.Addr(1, 3), bible.Addr(2, 1)],
            bible._parseLocsToken('1:1,3,2:1'))
        self.assertEqual(
            [bible.Addr(1, 1), bible.AddrRange(bible.Addr(1, 3), bible.Addr(2, 1))],
            bible._parseLocsToken('1:1,3-2:1'))

if __name__ == '__main__':
    unittest.main()
