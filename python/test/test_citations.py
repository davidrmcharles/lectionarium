#!/usr/bin/env python
'''
Tests for :mod:`citations`
'''

# Standard imports:
import unittest

# Local imports:
import citations
import locs

class parseCitationTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            citations.parseCitation(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            citations.parseCitation('')

    def test_actualMistakes(self):
        with self.assertRaises(ValueError):
            citations.parseCitation('Ez` 37:12-14')
        with self.assertRaises(ValueError):
            citations.parseCitation('3 Lk 24:13-35')
        with self.assertRaises(ValueError):
            citations.parseCitation('Acts 2:14:22-33')
        with self.assertRaises(ValueError):
            citations.parseCitation('1 Pt2:20b-25')
        with self.assertRaises(ValueError):
            citations.parseCitation('Zep 2:3,3:12--13')
        with self.assertRaises(ValueError):
            citations.parseCitation('I s58:7-10')
        with self.assertRaises(ValueError):
            citations.parseCitation('Cor 5:6b-8')
        with self.assertRaises(ValueError):
            citations.parseCitation('Is 49L1-6')

    def test_singleTokenBookOnly(self):
        ref = citations.parseCitation('gn')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(None, ref.locs)

    def test_twoTokenBookOnly(self):
        ref = citations.parseCitation('1 samuel')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(None, ref.locs)

    def test_twoTokenBookPlus(self):
        ref = citations.parseCitation('1 samuel 1:2-3:4')
        self.assertEqual('1samuel', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 2), locs.Addr(3, 4))],
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

        ref = citations.parseCitation('song of songs 1:2-3:4')
        self.assertEqual('songofsongs', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 2), locs.Addr(3, 4))],
            ref.locs)

    def test_syntheticAndMinimal(self):
        '''
        This is exact same series appears in parseVersesTokenTestCase,
        but here we add the name of a book.
        '''

        ref = citations.parseCitation('gn 1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual([locs.Addr(1)], ref.locs)

        ref = citations.parseCitation('gn 1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1), locs.Addr(2))],
            ref.locs)

        ref = citations.parseCitation('gn 1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1), locs.Addr(3)],
            ref.locs)

        ref = citations.parseCitation('gn 1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1), locs.Addr(2)), locs.Addr(4)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1, 1)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1-2')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 2))],
            ref.locs)

        ref = citations.parseCitation('gn 1:1,3')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(1, 3)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1-2,4')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 2)), locs.Addr(1, 4)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(2, 1))],
            ref.locs)

        ref = citations.parseCitation('gn 1:1,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(2, 1)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1,3,2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(1, 3), locs.Addr(2, 1)],
            ref.locs)

        ref = citations.parseCitation('gn 1:1,3-2:1')
        self.assertEqual('genesis', ref.book)
        self.assertEqual(
            [locs.Addr(1, 1), locs.AddrRange(locs.Addr(1, 3), locs.Addr(2, 1))],
            ref.locs)

if __name__ == '__main__':
    unittest.main()
