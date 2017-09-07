#!/usr/bin/env python
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible

class BookTestCase(unittest.TestCase):

    def test_normalName(self):
        self.assertEqual('genesis', bible.Book('Genesis', 'Gn').normalName)

    def test_noramlAbbreviations(self):
        self.assertEqual(['gn'], bible.Book('Genesis', 'Gn').normalAbbreviations)

    def test_matchesToken(self):
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('Genesis'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('genesis'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('GENESIS'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('GeNesIs'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('Gn'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('gn'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('GN'))
        self.assertTrue(bible.Book('Genesis', 'Gn').matchesToken('gN'))

    def test_str(self):
        self.assertEqual('Genesis (Gn)', str(bible.Book('Genesis', 'Gn')))

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

class PointTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.Point(1) == bible.Point(1))
        self.assertTrue(bible.Point(2) == bible.Point(2))

    def test_str(self):
        self.assertEqual('1', str(bible.Point(1)))
        self.assertEqual('2', str(bible.Point(2)))
        self.assertEqual('1:2', str(bible.Point(1, 2)))

class RangeTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.Range(1, 2) == bible.Range(1, 2))
        self.assertTrue(
            bible.Range(bible.Point(1), bible.Point(2)) == \
                bible.Range(bible.Point(1), bible.Point(2)))

    def test_str(self):
        self.assertEqual(
            '1:2-3:4', str(bible.Range(bible.Point(1, 2), bible.Point(3, 4))))

class parseChapterAndVerseTokenTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            bible._parseChapterAndVerseToken(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            bible._parseChapterAndVerseToken('')

    def test_syntheticAndMinimal(self):
        self.assertEquals(
            [bible.Point(1)],
            bible._parseChapterAndVerseToken('1'))
        self.assertEquals(
            [bible.Range(bible.Point(1), bible.Point(2))],
            bible._parseChapterAndVerseToken('1-2'))
        self.assertEquals(
            [bible.Point(1), bible.Point(3)],
            bible._parseChapterAndVerseToken('1,3'))
        self.assertEquals(
            [bible.Range(bible.Point(1), bible.Point(2)), bible.Point(4)],
            bible._parseChapterAndVerseToken('1-2,4'))
        self.assertEquals(
            [bible.Point(1, 1)],
            bible._parseChapterAndVerseToken('1:1'))
        self.assertEquals(
            [bible.Range(bible.Point(1, 1), bible.Point(1, 2))],
            bible._parseChapterAndVerseToken('1:1-2'))
        self.assertEquals(
            [bible.Point(1, 1), bible.Point(1, 3)],
            bible._parseChapterAndVerseToken('1:1,3'))
        self.assertEquals(
            [bible.Range(bible.Point(1, 1), bible.Point(1, 2)), bible.Point(1, 4)],
            bible._parseChapterAndVerseToken('1:1-2,4'))
        self.assertEquals(
            [bible.Range(bible.Point(1, 1), bible.Point(2, 1))],
            bible._parseChapterAndVerseToken('1:1-2:1'))
        self.assertEquals(
            [bible.Point(1, 1), bible.Point(2, 1)],
            bible._parseChapterAndVerseToken('1:1,2:1'))
        self.assertEquals(
            [bible.Point(1, 1), bible.Point(1, 3), bible.Point(2, 1)],
            bible._parseChapterAndVerseToken('1:1,3,2:1'))
        self.assertEquals(
            [bible.Point(1, 1), bible.Range(bible.Point(1, 3), bible.Point(2, 1))],
            bible._parseChapterAndVerseToken('1:1,3-2:1'))

if __name__ == '__main__':
    unittest.main()
