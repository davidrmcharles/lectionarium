#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible

class parseTestCase(unittest.TestCase):

    def test_foo_bar_zod(self):
        self.assertEquals(
            (None, 0),
            bible.parse(['foo', 'bar', 'zod']))

    def test_Song_of_Songs(self):
        self.assertEquals(
            ('songofsongs', 3),
            bible.parse(['Song', 'of', 'Songs']))

    def test_John_3_16(self):
        self.assertEquals(
            ('john', 1),
            bible.parse(['John', '3:16']))

    def test_1_John(self):
        self.assertEquals(
            ('1john', 2),
            bible.parse(['1', 'John']))

class BibleTestCase(unittest.TestCase):

    def test_findBook(self):
        self.assertIsNotNone(bible.getBible().findBook('Genesis'))
        self.assertIsNotNone(bible.getBible().findBook('genesis'))
        self.assertIsNotNone(bible.getBible().findBook('GENESIS'))
        self.assertIsNotNone(bible.getBible().findBook('GeNeSIs'))

        self.assertIsNotNone(bible.getBible().findBook('Gn'))
        self.assertIsNotNone(bible.getBible().findBook('gn'))
        self.assertIsNotNone(bible.getBible().findBook('GN'))
        self.assertIsNotNone(bible.getBible().findBook('gN'))

class BookTestCase(unittest.TestCase):

    def test_normalName(self):
        self.assertEqual('genesis', bible.Book('Genesis', ['Gn']).normalName)

    def test_normalAbbreviations(self):
        self.assertEqual(
            ['gn'], bible.Book('Genesis', ['Gn']).normalAbbreviations)

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

    def test_invalidRangeOfVerses(self):
        with self.assertRaises(bible.InvalidCitation):
            bible.getVerses('john 18:42')

class CommandLineParserTestCase(unittest.TestCase):

    pass

if __name__ == '__main__':
    unittest.main()
