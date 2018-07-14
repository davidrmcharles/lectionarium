#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`books`
'''

# Standard imports:
import unittest

# Local imports:
import books
import addrs

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

if __name__ == '__main__':
    unittest.main()
