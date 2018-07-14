#!/usr/bin/env python
'''
Tests for :mod:`citations`
'''

# Standard imports:
import unittest

# Local imports:
import citations
import addrs

class parseTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            citations.parse(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            citations.parse('')

    def test_actualMistakes(self):
        with self.assertRaises(ValueError):
            citations.parse('Ez` 37:12-14')
        with self.assertRaises(ValueError):
            citations.parse('3 Lk 24:13-35')
        with self.assertRaises(ValueError):
            citations.parse('Acts 2:14:22-33')
        with self.assertRaises(ValueError):
            citations.parse('1 Pt2:20b-25')
        with self.assertRaises(ValueError):
            citations.parse('Zep 2:3,3:12--13')
        with self.assertRaises(ValueError):
            citations.parse('I s58:7-10')
        with self.assertRaises(ValueError):
            citations.parse('Cor 5:6b-8')
        with self.assertRaises(ValueError):
            citations.parse('Is 49L1-6')

    def test_singleTokenBookOnly(self):
        ref = citations.parse('gn')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(None, ref.addrs)

    def test_twoTokenBookOnly(self):
        ref = citations.parse('1 samuel')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(None, ref.addrs)

    def test_twoTokenBookPlus(self):
        ref = citations.parse('1 samuel 1:2-3:4')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 2), addrs.Addr(3, 4))],
            ref.addrs)

    def test_songOfSongs(self):
        '''
        This case requires that the parsing of the book tokens be
        'greedy'.

        Because 'song' is both an abbreviations for this book and the
        first word in its full name, a non-greedy approach to
        parsing-out the name of the book will leave too many tokens
        behind.
        '''

        ref = citations.parse('song of songs 1:2-3:4')
        self.assertEqual('songofsongs', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 2), addrs.Addr(3, 4))],
            ref.addrs)

    def test_syntheticAndMinimal(self):
        '''
        This is exact same series appears in parseVersesTokenTestCase,
        but here we add the name of a book.
        '''

        ref = citations.parse('gn 1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual([addrs.Addr(1)], ref.addrs)

        ref = citations.parse('gn 1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1), addrs.Addr(2))],
            ref.addrs)

        ref = citations.parse('gn 1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1), addrs.Addr(3)],
            ref.addrs)

        ref = citations.parse('gn 1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1), addrs.Addr(2)), addrs.Addr(4)],
            ref.addrs)

        ref = citations.parse('gn 1:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1, 1)],
            ref.addrs)

        ref = citations.parse('gn 1:1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(1, 2))],
            ref.addrs)

        ref = citations.parse('gn 1:1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(1, 3)],
            ref.addrs)

        ref = citations.parse('gn 1:1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(1, 2)), addrs.Addr(1, 4)],
            ref.addrs)

        ref = citations.parse('gn 1:1-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(2, 1))],
            ref.addrs)

        ref = citations.parse('gn 1:1,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(2, 1)],
            ref.addrs)

        ref = citations.parse('gn 1:1,3,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(1, 3), addrs.Addr(2, 1)],
            ref.addrs)

        ref = citations.parse('gn 1:1,3-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.AddrRange(addrs.Addr(1, 3), addrs.Addr(2, 1))],
            ref.addrs)

if __name__ == '__main__':
    unittest.main()
