#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`text`
'''

# Standard imports:
import re
import unittest

# Local imports:
import addrs
import texts

class TextTestCase(unittest.TestCase):

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

    def test_validateChapterKey(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        with self.assertRaises(KeyError):
            text._validateChapterKey(None)
        with self.assertRaises(KeyError):
            text._validateChapterKey(0)
        with self.assertRaises(KeyError):
            text._validateChapterKey('1')
        text._validateChapterKey(1)
        text._validateChapterKey(2)
        text._validateChapterKey(3)
        with self.assertRaises(KeyError):
            text._validateChapterKey(4)

        text = texts.Text('testing', False)
        text.loadFromString(self.bookWithoutChaptersText)

        with self.assertRaises(KeyError):
            text._validateChapterKey(None)
        with self.assertRaises(KeyError):
            text._validateChapterKey(0)
        with self.assertRaises(KeyError):
            text._validateChapterKey('1')

        # It seems helpful to treat the number 1 as a valid
        # chapterKey.
        text._validateChapterKey(1)

        with self.assertRaises(KeyError):
            text._validateChapterKey(2)

    def test_validateChapterAndVerseKeys(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(None, 1)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(0, 1)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys('1', 1)

        text._validateChapterAndVerseKeys(1, 1)
        text._validateChapterAndVerseKeys(1, 2)
        text._validateChapterAndVerseKeys(1, 3)
        text._validateChapterAndVerseKeys(2, 1)
        text._validateChapterAndVerseKeys(2, 2)
        text._validateChapterAndVerseKeys(2, 3)
        text._validateChapterAndVerseKeys(3, 1)
        text._validateChapterAndVerseKeys(3, 2)
        text._validateChapterAndVerseKeys(3, 3)

        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(1, 4)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(2, 4)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(3, 4)

        text = texts.Text('testing', False)
        text.loadFromString(self.bookWithoutChaptersText)

        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(None, 1)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(0, 1)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys('1', 1)

        # Here again, we treat the number 1 as a valid chapterKey when
        # the book has no chapters.
        text._validateChapterAndVerseKeys(1, 1)
        text._validateChapterAndVerseKeys(1, 3)
        text._validateChapterAndVerseKeys(1, 3)

        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(2, 1)
        with self.assertRaises(KeyError):
            text._validateChapterAndVerseKeys(1, 4)

    def test_validateVerseKey(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # If the book has chapters, any verseKey by itself is cause
        # for an exception.
        with self.assertRaises(KeyError):
            text._validateVerseKey(None)
        with self.assertRaises(KeyError):
            text._validateVerseKey(0)
        with self.assertRaises(KeyError):
            text._validateVerseKey('1')
        with self.assertRaises(KeyError):
            text._validateVerseKey(1)

        text = texts.Text('testing', False)
        text.loadFromString(self.bookWithoutChaptersText)
        with self.assertRaises(KeyError):
            text._validateVerseKey(None)
        with self.assertRaises(KeyError):
            text._validateVerseKey(0)
        with self.assertRaises(KeyError):
            text._validateVerseKey('1')
        text._validateVerseKey(1)
        text._validateVerseKey(2)
        text._validateVerseKey(3)
        with self.assertRaises(KeyError):
            text._validateVerseKey(4)

    def test_getVerse(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # This should return all of chapter 1.
        result = text.getVerse(addrs.Addr(1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should return all of chapter 2.
        result = text.getVerse(addrs.Addr(2))
        self.assertEqual(
            result, [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        # This should return verse 1:1.
        result = text.getVerse(addrs.Addr(1, 1))
        self.assertEqual(
            result, [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should return verse 1:2.
        result = text.getVerse(addrs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should return verse 2:3:
        result = text.getVerse(addrs.Addr(2, 3))
        self.assertEqual(
            result, [
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        text = texts.Text('testing', False)
        text.loadFromString(self.bookWithoutChaptersText)

        # This should return only verse 1.
        result = text.getVerse(addrs.Addr(1))
        self.assertEqual(
            result, [
                (1, u'Judas Jesu Christi servus...'),
                ])

        # This should return only verse 2.
        result = text.getVerse(addrs.Addr(2))
        self.assertEqual(
            result, [
                (2, u'Misericordia vobis...'),
                ])

        # A request for 1:2 should also return verse 2, but the
        # 'address' should have the shape of the reference.
        result = text.getVerse(addrs.Addr(1, 2))
        self.assertEqual(
            result, [
                ((1, 2), u'Misericordia vobis...'),
                ])

    def test_getRangeOfVerses(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # Here are a few ranges entirely within the same chapter,
        # starting with 1:1-1:3.
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(1, 3)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...')],
            verses)

        # 2:1-2:2
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(2, 1), addrs.Addr(2, 2)))
        self.assertEqual(
            [((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...')],
            verses)

        # 3:2-3:3
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(3, 2), addrs.Addr(3, 3)))
        self.assertEqual(
            [((3, 2), u'Cui respondit mulier...'),
             ((3, 3), u'de fructu vero ligni quod est in medio paradisi...')],
            verses)

        # Here are some ranges in adjacent chapters, starting with
        # 1:1-2:1:
        verses = text.getRangeOfVerses(addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(2, 1)))
        self.assertEqual(
            [((1, 1), u'In principio creavit Deus cælum et terram.'),
             ((1, 2), u'Terra autem erat inanis et vacua...'),
             ((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...')],
            verses)

        # 2:2-3:2
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(2, 2), addrs.Addr(3, 2)))
        self.assertEqual(
            [((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...'),
             ((3, 2), u'Cui respondit mulier...')],
            verses)

        # Finally, here is the case of a book in the middle: 1:3-3:1:
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(1, 3), addrs.Addr(3, 1)))
        self.assertEqual(
            [((1, 3), u'Dixitque Deus...'),
             ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
             ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
             ((2, 3), u'Et benedixit diei septimo...'),
             ((3, 1), u'Sed et serpens erat callidior cunctis animantibus terræ quæ fecerat Dominus Deus...')],
            verses)

        # Now let's see if we can handle whole-chapter ranges like
        # 1-2:
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(1), addrs.Addr(2)))
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
            text.getRangeOfVerses(
                addrs.AddrRange(addrs.Addr(1), addrs.Addr(1))))

        # What about a range that begins on a chapter, but ends on a
        # verse, like 1-2:2:
        verses = text.getRangeOfVerses(
            addrs.AddrRange(addrs.Addr(1), addrs.Addr(2, 2)))
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
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            text._allVersesInChapter(1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should arrive at all verses in chapter 2.
        self.assertEqual(
            text._allVersesInChapter(2), [
                ((2, 1), u'Igitur perfecti sunt cæli et terra...'),
                ((2, 2), u'Complevitque Deus die septimo opus suum quod fecerat...'),
                ((2, 3), u'Et benedixit diei septimo...'),
                ])

        text = texts.Text('testing', False)
        text.loadFromString(self.bookWithoutChaptersText)

        # This should arrive at all verses in chapter 1.
        self.assertEqual(
            text._allVersesInChapter(1), [
                ((1, 1), u'Judas Jesu Christi servus...'),
                ((1, 2), u'Misericordia vobis...'),
                ((1, 3), u'Carissimi...'),
                ])

    def test_lastVersesInChapter(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            text._lastVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            text._lastVersesInChapter(1, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            text._lastVersesInChapter(1, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_firstVersesInChapter(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # This should produce verses 1:1-3.
        self.assertEqual(
            text._firstVersesInChapter(1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce verses 1:2-3.
        self.assertEqual(
            text._firstVersesInChapter(1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produces verses 1:3.
        self.assertEqual(
            text._firstVersesInChapter(1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

    def test_middleVersesInChapter(self):
        text = texts.Text('testing')
        text.loadFromString(self.bookWithChaptersText)

        # This should produce all three verses of chapter one.
        self.assertEqual(
            text._middleVersesInChapter(1, 1, 3), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce only verse 1.
        self.assertEqual(
            text._middleVersesInChapter(1, 1, 1), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ])

        # This should produce only verse 2.
        self.assertEqual(
            text._middleVersesInChapter(1, 2, 2), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce only verse 3.
        self.assertEqual(
            text._middleVersesInChapter(1, 3, 3), [
                ((1, 3), u'Dixitque Deus...'),
                ])

        # This should produce verses 1-2.
        self.assertEqual(
            text._middleVersesInChapter(1, 1, 2), [
                ((1, 1), u'In principio creavit Deus cælum et terram.'),
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ])

        # This should produce verses 2-3.
        self.assertEqual(
            text._middleVersesInChapter(1, 2, 3), [
                ((1, 2), u'Terra autem erat inanis et vacua...'),
                ((1, 3), u'Dixitque Deus...'),
                ])

class TextTestCase_chapterKeys(unittest.TestCase):

    def test_1(self):
        text = texts.Text('genesis', True)
        text.loadFromFile()
        self.assertEquals(range(1, 51), text.chapterKeys)

    def test_2(self):
        text = texts.Text('philemon', False)
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
        text = texts.Text('test', True)
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

    def test_bigSample(self):
        words = [
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
            ((3, 3), 'fruct'),
            ((3, 3), 'vero'),
            ((3, 3), 'ligni'),
            ((3, 3), 'quod'),
            ((3, 3), 'est'),
            ((3, 3), 'in'),
            ((3, 3), 'medio'),
            ((3, 3), 'paradisi'),
            ]
        concordance = texts.Concordance()
        concordance.addWords(words)

        expectedEntries = {
            'a' : [
                texts.ConcordanceEntry('animantibus', [(3, 1)]),
                texts.ConcordanceEntry('autem', [(1, 2)]),
                ],

            'b' : [
                texts.ConcordanceEntry('benedixit', [(2, 3)]),
                ],

            'c' : [
                texts.ConcordanceEntry('cæli', [(2, 1)]),
                texts.ConcordanceEntry('cælum', [(1, 1)]),
                texts.ConcordanceEntry('callidior', [(3, 1)]),
                texts.ConcordanceEntry('complevitque', [(2, 2)]),
                texts.ConcordanceEntry('creavit', [(1, 1)]),
                texts.ConcordanceEntry('cui', [(3, 2)]),
                texts.ConcordanceEntry('cunctis', [(3, 1)]),
                ],

            'd' : [
                texts.ConcordanceEntry('de', [(3, 3)]),
                texts.ConcordanceEntry('deus', [(1, 1), (1, 3), (2, 2), (3, 1)]),
                texts.ConcordanceEntry('die', [(2, 2)]),
                texts.ConcordanceEntry('diei', [(2, 3)]),
                texts.ConcordanceEntry('dixitque', [(1, 3)]),
                texts.ConcordanceEntry('dominus', [(3, 1)]),
                ],

            'e' : [
                texts.ConcordanceEntry('erat', [(1, 2), (3, 1)]),
                texts.ConcordanceEntry('est', [(3, 3)]),
                texts.ConcordanceEntry('et', [(1, 1), (1, 2), (2, 1), (2, 3), (3, 1)]),
                ],

            'f' : [
                texts.ConcordanceEntry('fecerat', [(2, 2), (3, 1)]),
                texts.ConcordanceEntry('fruct', [(3, 3)]),
                ],

            'i' : [
                texts.ConcordanceEntry('igitur', [(2, 1)]),
                texts.ConcordanceEntry('in', [(1, 1), (3, 3)]),
                texts.ConcordanceEntry('inanis', [(1, 2)]),
                ],

            'l' : [
                texts.ConcordanceEntry('ligni', [(3, 3)]),
                ],

            'm' : [
                texts.ConcordanceEntry('medio', [(3, 3)]),
                texts.ConcordanceEntry('mulier', [(3, 2)]),
                ],

            'o' : [
                texts.ConcordanceEntry('opus', [(2, 2)]),
                ],

            'p' : [
                texts.ConcordanceEntry('paradisi', [(3, 3)]),
                texts.ConcordanceEntry('perfecti', [(2, 1)]),
                texts.ConcordanceEntry('principio', [(1, 1)]),
                ],

            'q' : [
                texts.ConcordanceEntry('quæ', [(3, 1)]),
                texts.ConcordanceEntry('quod', [(2, 2), (3, 3)]),
                ],

            'r' : [
                texts.ConcordanceEntry('respondit', [(3, 2)]),
                ],

            's' : [
                texts.ConcordanceEntry('sed', [(3, 1)]),
                texts.ConcordanceEntry('septimo', [(2, 2), (2, 3)]),
                texts.ConcordanceEntry('serpens', [(3, 1)]),
                texts.ConcordanceEntry('sunt', [(2, 1)]),
                texts.ConcordanceEntry('suum', [(2, 2)]),
                ],

            't' : [
                texts.ConcordanceEntry('terra', [(1, 2), (2, 1)]),
                texts.ConcordanceEntry('terræ', [(3, 1)]),
                texts.ConcordanceEntry('terram', [(1, 1)]),
                ],

            'v' : [
                texts.ConcordanceEntry('vacua', [(1, 2)]),
                texts.ConcordanceEntry('vero', [(3, 3)]),
                ],
            }

        self.assertEqual(expectedEntries, concordance._entries)

    def test_entriesAreSorted(self):
        words = [
            ((1, 1), 'creavit'),
            ((1, 1), 'cælum'),
            ((2, 1), 'cæli'),
            ((2, 2), 'complevitque'),
            ((3, 1), 'callidior'),
            ((3, 1), 'cunctis'),
            ((3, 2), 'cui'),
            ]
        concordance = texts.Concordance()
        concordance.addWords(words)

        expectedEntries = {
            'c' : [
                texts.ConcordanceEntry('cæli', [(2, 1)]),
                texts.ConcordanceEntry('cælum', [(1, 1)]),
                texts.ConcordanceEntry('callidior', [(3, 1)]),
                texts.ConcordanceEntry('complevitque', [(2, 2)]),
                texts.ConcordanceEntry('creavit', [(1, 1)]),
                texts.ConcordanceEntry('cui', [(3, 2)]),
                texts.ConcordanceEntry('cunctis', [(3, 1)]),
                ]
            }

        self.assertEqual(expectedEntries, concordance._entries)

class ConcordanceEntryTestCase(unittest.TestCase):

    def test_sortableWord(self):
        self.assertEqual(
            'creavit',
            texts.ConcordanceEntry('creavit').sortableWord)
        self.assertEqual(
            'caelum',
            texts.ConcordanceEntry('cælum').sortableWord)

if __name__ == '__main__':
    unittest.main()
