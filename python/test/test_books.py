#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`books`
'''

# Standard imports:
import unittest

# Local imports:
import books
import locs

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
        self.assertEqual('genesis', books.Book('Genesis', ['Gn']).normalName)

    def test_noramlAbbreviations(self):
        self.assertEqual(['gn'], books.Book('Genesis', ['Gn']).normalAbbreviations)

    def test_matchesToken(self):
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('Genesis'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('genesis'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('GENESIS'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('GeNesIs'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('Gn'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('gn'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('GN'))
        self.assertTrue(books.Book('Genesis', ['Gn']).matchesToken('gN'))

    def test_str(self):
        self.assertEqual('Genesis (Gn)', str(books.Book('Genesis', ['Gn'])))

    def test_getVerse(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # This should return all of chapter 1.
        result = bookWithChapters.getVerse(locs.Addr(1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should return all of chapter 2.
        result = bookWithChapters.getVerse(locs.Addr(2))
        self.assertEqual(
            result, [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        # This should return verse 1:1.
        result = bookWithChapters.getVerse(locs.Addr(1, 1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should return verse 1:2.
        result = bookWithChapters.getVerse(locs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should return verse 2:3:
        result = bookWithChapters.getVerse(locs.Addr(2, 3))
        self.assertEqual(
            result, [
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.loadTextFromString(self.bookWithoutChaptersText)

        # This should return only verse 1.
        result = bookWithoutChapters.getVerse(locs.Addr(1))
        self.assertEqual(
            result, [
                (1, u'Judas Jesu Christi servus...'),
                ])

        # This should return only verse 2.
        result = bookWithoutChapters.getVerse(locs.Addr(2))
        self.assertEqual(
            result, [
                (2, u'Misericordia vobis...'),
                ])

        # A request for 1:2 should also return verse 2, but the
        # 'address' should have the shape of the reference.
        result = bookWithoutChapters.getVerse(locs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Misericordia vobis...'),
                ])

    def test_getRangeOfVerses(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.loadTextFromString(self.bookWithChaptersText)

        # Here are a few ranges entirely within the same chapter,
        # starting with 1:1-1:3.
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 3)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...')],
            verses)

        # 2:1-2:2
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(2, 1), locs.Addr(2, 2)))
        self.assertEqual(
            [((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...')],
            verses)

        # 3:2-3:3
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(3, 2), locs.Addr(3, 3)))
        self.assertEqual(
            [((3, 2), u'Cui respondit mulier...'),
             ((3, 3), u'de fructu vero ligni quod est in medio paradisi...')],
            verses)

        # Here are some ranges in adjacent chapters, starting with
        # 1:1-2:1:
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(1, 1), locs.Addr(2, 1)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...')],
            verses)

        # 2:2-3:2
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(2, 2), locs.Addr(3, 2)))
        self.assertEqual(
            [((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...'),
             ((3, 2), u'Cui respondit mulier...')],
            verses)

        # Finally, here is the case of a book in the middle: 1:3-3:1:
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(1, 3), locs.Addr(3, 1)))
        self.assertEqual(
            [((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...')],
            verses)

        # Now let's see if we can handle whole-chapter ranges like
        # 1-2:
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(1), locs.Addr(2)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...')],
            verses)

        # What about a range like 1-1?  We don't expect this from a
        # human, but it can happen when we normalize a mix of
        # addresses and address ranges to address ranges.
        expectedVerses = [
            ((1, 1), u'In principio creavit Deus cælum et terram.'),
            ((1, 2), u'Terra autem erat inanis et vacua...'),
            ((1, 3), u'Dixitque Deus...')
            ]
        self.assertEqual(
            expectedVerses,
            bookWithChapters.getRangeOfVerses(
                locs.AddrRange(locs.Addr(1), locs.Addr(1))))

        # What about a range that begins on a chapter, but ends on a
        # verse, like 1-2:2:
        verses = bookWithChapters.getRangeOfVerses(locs.AddrRange(locs.Addr(1), locs.Addr(2, 2)))
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
        bookWithChapters = books.Book('withchapters', hasChapters=True)
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

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.loadTextFromString(self.bookWithoutChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            bookWithoutChapters._allVersesInChapter(1), [
                ((1, 1), u'Judas Jesu Christi servus...'),
                ((1, 2), u'Misericordia vobis...'),
                ((1, 3), u'Carissimi...'),
                ])

    def test_lastVersesInChapter(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
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
        bookWithChapters = books.Book('withchapters', hasChapters=True)
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
        bookWithChapters = books.Book('withchapters', hasChapters=True)
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
        self.assertIsNotNone(books.findBook('Genesis'))
        self.assertIsNotNone(books.findBook('genesis'))
        self.assertIsNotNone(books.findBook('GENESIS'))
        self.assertIsNotNone(books.findBook('GeNeSIs'))

        self.assertIsNotNone(books.findBook('Gn'))
        self.assertIsNotNone(books.findBook('gn'))
        self.assertIsNotNone(books.findBook('GN'))
        self.assertIsNotNone(books.findBook('gN'))

class parseTestCase(unittest.TestCase):

    def test_1(self):
        books.parse(['foo', 'bar', 'zod'])

if __name__ == '__main__':
    unittest.main()
