#!/usr/bin/env python
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible

class PointTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.Point(1) == bible.Point(1))
        self.assertTrue(bible.Point(2) == bible.Point(2))

class RangeTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(bible.Range(1, 2) == bible.Range(1, 2))
        self.assertTrue(
            bible.Range(bible.Point(1), bible.Point(2)) == \
                bible.Range(bible.Point(1), bible.Point(2)))

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
