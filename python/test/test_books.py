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

class parseTestCase(unittest.TestCase):

    def test_foo_bar_zod(self):
        self.assertEquals(
            (None, 0),
            books.parse(['foo', 'bar', 'zod']))

    def test_Song_of_Songs(self):
        self.assertEquals(
            ('songofsongs', 3),
            books.parse(['Song', 'of', 'Songs']))

    def test_John_3_16(self):
        self.assertEquals(
            ('john', 1),
            books.parse(['John', '3:16']))

    def test_1_John(self):
        self.assertEquals(
            ('1john', 2),
            books.parse(['1', 'John']))

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

    def test_normalAbbreviations(self):
        self.assertEqual(
            ['gn'], books.Book('Genesis', ['Gn']).normalAbbreviations)

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

    def test_validateChapterKey(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterKey(None)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterKey(0)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterKey('1')
        bookWithChapters.text._validateChapterKey(1)
        bookWithChapters.text._validateChapterKey(2)
        bookWithChapters.text._validateChapterKey(3)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterKey(4)

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.text.loadFromString(self.bookWithoutChaptersText)

        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterKey(None)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterKey(0)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterKey('1')

        # It seems helpful to treat the number 1 as a valid
        # chapterKey.
        bookWithoutChapters.text._validateChapterKey(1)

        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterKey(2)

    def test_validateChapterAndVerseKeys(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys(None, 1)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys(0, 1)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys('1', 1)

        bookWithChapters.text._validateChapterAndVerseKeys(1, 1)
        bookWithChapters.text._validateChapterAndVerseKeys(1, 2)
        bookWithChapters.text._validateChapterAndVerseKeys(1, 3)
        bookWithChapters.text._validateChapterAndVerseKeys(2, 1)
        bookWithChapters.text._validateChapterAndVerseKeys(2, 2)
        bookWithChapters.text._validateChapterAndVerseKeys(2, 3)
        bookWithChapters.text._validateChapterAndVerseKeys(3, 1)
        bookWithChapters.text._validateChapterAndVerseKeys(3, 2)
        bookWithChapters.text._validateChapterAndVerseKeys(3, 3)

        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys(1, 4)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys(2, 4)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateChapterAndVerseKeys(3, 4)

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.text.loadFromString(self.bookWithoutChaptersText)

        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterAndVerseKeys(None, 1)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterAndVerseKeys(0, 1)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterAndVerseKeys('1', 1)

        # Here again, we treat the number 1 as a valid chapterKey when
        # the book has no chapters.
        bookWithoutChapters.text._validateChapterAndVerseKeys(1, 1)
        bookWithoutChapters.text._validateChapterAndVerseKeys(1, 3)
        bookWithoutChapters.text._validateChapterAndVerseKeys(1, 3)

        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterAndVerseKeys(2, 1)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateChapterAndVerseKeys(1, 4)

    def test_validateVerseKey(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # If the book has chapters, any verseKey by itself is cause
        # for an exception.
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateVerseKey(None)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateVerseKey(0)
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateVerseKey('1')
        with self.assertRaises(KeyError):
            bookWithChapters.text._validateVerseKey(1)

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.text.loadFromString(self.bookWithoutChaptersText)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateVerseKey(None)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateVerseKey(0)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateVerseKey('1')
        bookWithoutChapters.text._validateVerseKey(1)
        bookWithoutChapters.text._validateVerseKey(2)
        bookWithoutChapters.text._validateVerseKey(3)
        with self.assertRaises(KeyError):
            bookWithoutChapters.text._validateVerseKey(4)

    def test_getVerse(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # This should return all of chapter 1.
        result = bookWithChapters.text.getVerse(locs.Addr(1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should return all of chapter 2.
        result = bookWithChapters.text.getVerse(locs.Addr(2))
        self.assertEqual(
            result, [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        # This should return verse 1:1.
        result = bookWithChapters.text.getVerse(locs.Addr(1, 1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should return verse 1:2.
        result = bookWithChapters.text.getVerse(locs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should return verse 2:3:
        result = bookWithChapters.text.getVerse(locs.Addr(2, 3))
        self.assertEqual(
            result, [
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.text.loadFromString(self.bookWithoutChaptersText)

        # This should return only verse 1.
        result = bookWithoutChapters.text.getVerse(locs.Addr(1))
        self.assertEqual(
            result, [
                (1, u'Judas Jesu Christi servus...'),
                ])

        # This should return only verse 2.
        result = bookWithoutChapters.text.getVerse(locs.Addr(2))
        self.assertEqual(
            result, [
                (2, u'Misericordia vobis...'),
                ])

        # A request for 1:2 should also return verse 2, but the
        # 'address' should have the shape of the reference.
        result = bookWithoutChapters.text.getVerse(locs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Misericordia vobis...'),
                ])

    def test_getRangeOfVerses(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # Here are a few ranges entirely within the same chapter,
        # starting with 1:1-1:3.
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 3)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...')],
            verses)

        # 2:1-2:2
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(2, 1), locs.Addr(2, 2)))
        self.assertEqual(
            [((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...')],
            verses)

        # 3:2-3:3
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(3, 2), locs.Addr(3, 3)))
        self.assertEqual(
            [((3, 2), u'Cui respondit mulier...'),
             ((3, 3), u'de fructu vero ligni quod est in medio paradisi...')],
            verses)

        # Here are some ranges in adjacent chapters, starting with
        # 1:1-2:1:
        verses = bookWithChapters.text.getRangeOfVerses(locs.AddrRange(locs.Addr(1, 1), locs.Addr(2, 1)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...')],
            verses)

        # 2:2-3:2
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(2, 2), locs.Addr(3, 2)))
        self.assertEqual(
            [((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...'),
             ((3, 2), u'Cui respondit mulier...')],
            verses)

        # Finally, here is the case of a book in the middle: 1:3-3:1:
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(1, 3), locs.Addr(3, 1)))
        self.assertEqual(
            [((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...')],
            verses)

        # Now let's see if we can handle whole-chapter ranges like
        # 1-2:
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(1), locs.Addr(2)))
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
            bookWithChapters.text.getRangeOfVerses(
                locs.AddrRange(locs.Addr(1), locs.Addr(1))))

        # What about a range that begins on a chapter, but ends on a
        # verse, like 1-2:2:
        verses = bookWithChapters.text.getRangeOfVerses(
            locs.AddrRange(locs.Addr(1), locs.Addr(2, 2)))
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
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            bookWithChapters.text._allVersesInChapter(1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should arrive at all verses in chapter 2.
        self.assertEqual(
            bookWithChapters.text._allVersesInChapter(2), [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        bookWithoutChapters = books.Book('withoutchapters', hasChapters=False)
        bookWithoutChapters.text.loadFromString(self.bookWithoutChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            bookWithoutChapters.text._allVersesInChapter(1), [
                ((1, 1), u'Judas Jesu Christi servus...'),
                ((1, 2), u'Misericordia vobis...'),
                ((1, 3), u'Carissimi...'),
                ])

    def test_lastVersesInChapter(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            bookWithChapters.text._lastVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            bookWithChapters.text._lastVersesInChapter(1, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            bookWithChapters.text._lastVersesInChapter(1, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_firstVersesInChapter(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            bookWithChapters.text._firstVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            bookWithChapters.text._firstVersesInChapter(1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            bookWithChapters.text._firstVersesInChapter(1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_middleVersesInChapter(self):
        bookWithChapters = books.Book('withchapters', hasChapters=True)
        bookWithChapters.text.loadFromString(self.bookWithChaptersText)

        # This should produce all three verses of chapter one.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce only verse 1.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce only verse 2.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 2, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce only verse 3.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 3, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1-2.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce verses 2-3.
        self.assertEqual(
            bookWithChapters.text._middleVersesInChapter(1, 2, 3), [
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

class TextTestCase_chapterKeys(unittest.TestCase):

    def test_1(self):
        text = books._Text('genesis', True)
        text.loadFromFile()
        self.assertEquals(range(1, 51), text.chapterKeys)

    def test_2(self):
        text = books._Text('philemon', False)
        text.loadFromFile()
        self.assertEquals([1], text.chapterKeys)

class TextTestCase_getAllWords(unittest.TestCase):

    bookWithChaptersText = '''\
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

    def test_1(self):
        text = books._Text('test', True)
        text.loadFromString(self.bookWithChaptersText)
        expectedResult = [
            ((1, 1), 'in'),
            ((1, 1), 'principio'),
            ((1, 1), 'creavit'),
            ((1, 1), 'deus'),
            ((1, 1), 'cælum'),
            ((1, 1), 'et'),
            ((1, 1), 'terram'),
            ((1, 2), 'terra'),
            ((1, 2), 'autem'),
            ((1, 2), 'erat'),
            ((1, 2), 'inanis'),
            ((1, 2), 'et'),
            ((1, 2), 'vacua'),
            ((1, 3), 'dixitque'),
            ((1, 3), 'deus'),
            ((2, 1), 'igitur'),
            ((2, 1), 'perfecti'),
            ((2, 1), 'sunt'),
            ((2, 1), 'cæli'),
            ((2, 1), 'et'),
            ((2, 1), 'terra'),
            ((2, 2), 'complevitque'),
            ((2, 2), 'deus'),
            ((2, 2), 'die'),
            ((2, 2), 'septimo'),
            ((2, 2), 'opus'),
            ((2, 2), 'suum'),
            ((2, 2), 'quod'),
            ((2, 2), 'fecerat'),
            ((2, 3), 'et'),
            ((2, 3), 'benedixit'),
            ((2, 3), 'diei'),
            ((2, 3), 'septimo'),
            ((3, 1), 'sed'),
            ((3, 1), 'et'),
            ((3, 1), 'serpens'),
            ((3, 1), 'erat'),
            ((3, 1), 'callidior'),
            ((3, 1), 'cunctis'),
            ((3, 1), 'animantibus'),
            ((3, 1), 'terræ'),
            ((3, 1), 'quæ'),
            ((3, 1), 'fecerat'),
            ((3, 1), 'dominus'),
            ((3, 1), 'deus'),
            ((3, 2), 'cui'),
            ((3, 2), 'respondit'),
            ((3, 2), 'mulier'),
            ((3, 3), 'de'),
            ((3, 3), 'fructu'),
            ((3, 3), 'vero'),
            ((3, 3), 'ligni'),
            ((3, 3), 'quod'),
            ((3, 3), 'est'),
            ((3, 3), 'in'),
            ((3, 3), 'medio'),
            ((3, 3), 'paradisi')
            ]
        self.assertEqual(expectedResult, list(text.getAllWords()))

class ConcordanceTestCase(unittest.TestCase):

    def test_1(self):
        words = [
            ((1, 1), u'in'),
            ((1, 1), u'principio'),
            ((1, 1), u'creavit'),
            ((1, 1), u'deus'),
            ((1, 1), u'cælum'),
            ((1, 1), u'et'),
            ((1, 1), u'terram'),
            ((1, 2), u'terra'),
            ((1, 2), u'autem'),
            ((1, 2), u'erat'),
            ((1, 2), u'inanis'),
            ((1, 2), u'et'),
            ((1, 2), u'vacua'),
            ((1, 3), u'dixitque'),
            ((1, 3), u'deus'),
            ((2, 1), u'igitur'),
            ((2, 1), u'perfecti'),
            ((2, 1), u'sunt'),
            ((2, 1), u'cæli'),
            ((2, 1), u'et'),
            ((2, 1), u'terra'),
            ((2, 2), u'complevitque'),
            ((2, 2), u'deus'),
            ((2, 2), u'die'),
            ((2, 2), u'septimo'),
            ((2, 2), u'opus'),
            ((2, 2), u'suum'),
            ((2, 2), u'quod'),
            ((2, 2), u'fecerat'),
            ((2, 3), u'et'),
            ((2, 3), u'benedixit'),
            ((2, 3), u'diei'),
            ((2, 3), u'septimo'),
            ((3, 1), u'sed'),
            ((3, 1), u'et'),
            ((3, 1), u'serpens'),
            ((3, 1), u'erat'),
            ((3, 1), u'callidior'),
            ((3, 1), u'cunctis'),
            ((3, 1), u'animantibus'),
            ((3, 1), u'terræ'),
            ((3, 1), u'quæ'),
            ((3, 1), u'fecerat'),
            ((3, 1), u'dominus'),
            ((3, 1), u'deus'),
            ((3, 2), u'cui'),
            ((3, 2), u'respondit'),
            ((3, 2), u'mulier'),
            ((3, 3), u'de'),
            ((3, 3), u'fructu'),
            ((3, 3), u'vero'),
            ((3, 3), u'ligni'),
            ((3, 3), u'quod'),
            ((3, 3), u'est'),
            ((3, 3), u'in'),
            ((3, 3), u'medio'),
            ((3, 3), u'paradisi')
            ]

        concordance = books.Concordance()
        concordance.addWords(words)

        expectedEntries = {
            u'a' : [
                books.ConcordanceEntry(u'animantibus', [(3, 1)]),
                books.ConcordanceEntry(u'autem', [(1, 2)]),
                ],

            u'b' : [
                books.ConcordanceEntry(u'benedixit', [(2, 3)]),
                ],

            u'c' : [
                books.ConcordanceEntry(u'callidior', [(3, 1)]),
                books.ConcordanceEntry(u'complevitque', [(2, 2)]),
                books.ConcordanceEntry(u'creavit', [(1, 1)]),
                books.ConcordanceEntry(u'cui', [(3, 2)]),
                books.ConcordanceEntry(u'cunctis', [(3, 1)]),
                books.ConcordanceEntry(u'cæli', [(2, 1)]),
                books.ConcordanceEntry(u'cælum', [(1, 1)]),
                ],

            u'd' : [
                books.ConcordanceEntry(u'de', [(3, 3)]),
                books.ConcordanceEntry(u'deus', [(1, 1), (1, 3), (2, 2), (3, 1)]),
                books.ConcordanceEntry(u'die', [(2, 2)]),
                books.ConcordanceEntry(u'diei', [(2, 3)]),
                books.ConcordanceEntry(u'dixitque', [(1, 3)]),
                books.ConcordanceEntry(u'dominus', [(3, 1)]),
                ],

            u'e' : [
                books.ConcordanceEntry(u'erat', [(1, 2), (3, 1)]),
                books.ConcordanceEntry(u'est', [(3, 3)]),
                books.ConcordanceEntry(u'et', [(1, 1), (1, 2), (2, 1), (2, 3), (3, 1)]),
                ],

            u'f' : [
                books.ConcordanceEntry(u'fecerat', [(2, 2), (3, 1)]),
                books.ConcordanceEntry(u'fructu', [(3, 3)]),
                ],

            u'i' : [
                books.ConcordanceEntry(u'igitur', [(2, 1)]),
                books.ConcordanceEntry(u'in', [(1, 1), (3, 3)]),
                books.ConcordanceEntry(u'inanis', [(1, 2)]),
                ],

            u'l' : [
                books.ConcordanceEntry(u'ligni', [(3, 3)]),
                ],

            u'm' : [
                books.ConcordanceEntry(u'medio', [(3, 3)]),
                books.ConcordanceEntry(u'mulier', [(3, 2)]),
                ],

            u'o' : [
                books.ConcordanceEntry(u'opus', [(2, 2)]),
                ],

            u'p' : [
                books.ConcordanceEntry(u'paradisi', [(3, 3)]),
                books.ConcordanceEntry(u'perfecti', [(2, 1)]),
                books.ConcordanceEntry(u'principio', [(1, 1)]),
                ],

            u'q' : [
                books.ConcordanceEntry(u'quod', [(2, 2), (3, 3)]),
                books.ConcordanceEntry(u'quæ', [(3, 1)]),
                ],

            u'r' : [
                books.ConcordanceEntry(u'respondit', [(3, 2)]),
                ],

            u's' : [
                books.ConcordanceEntry(u'sed', [(3, 1)]),
                books.ConcordanceEntry(u'septimo', [(2, 2), (2, 3)]),
                books.ConcordanceEntry(u'serpens', [(3, 1)]),
                books.ConcordanceEntry(u'sunt', [(2, 1)]),
                books.ConcordanceEntry(u'suum', [(2, 2)]),
                ],

            u't' : [
                books.ConcordanceEntry(u'terra', [(1, 2), (2, 1)]),
                books.ConcordanceEntry(u'terram', [(1, 1)]),
                books.ConcordanceEntry(u'terræ', [(3, 1)]),
                ],

            u'v' : [
                books.ConcordanceEntry(u'vacua', [(1, 2)]),
                books.ConcordanceEntry(u'vero', [(3, 3)]),
                ],
            }

        self.assertEqual(expectedEntries, concordance._entries)

if __name__ == '__main__':
    unittest.main()
