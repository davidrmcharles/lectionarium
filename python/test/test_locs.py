#!/usr/bin/env python
'''
Tests for :mod:`locs`
'''

# Standard imports:
import unittest

# Local imports:
import locs

class AddrTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(locs.Addr(1) == locs.Addr(1))
        self.assertTrue(locs.Addr(2) == locs.Addr(2))

    def test_str(self):
        self.assertEqual('1', str(locs.Addr(1)))
        self.assertEqual('2', str(locs.Addr(2)))
        self.assertEqual('1:2', str(locs.Addr(1, 2)))

class RangeTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(locs.AddrRange(1, 2) == locs.AddrRange(1, 2))
        self.assertTrue(
            locs.AddrRange(locs.Addr(1), locs.Addr(2)) == \
                locs.AddrRange(locs.Addr(1), locs.Addr(2)))

    def test_str(self):
        self.assertEqual(
            '1:2-3:4', str(locs.AddrRange(locs.Addr(1, 2), locs.Addr(3, 4))))

class parseLocsTokenTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            locs.parseLocsToken(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            locs.parseLocsToken('')

    def test_syntheticAndMinimal(self):
        self.assertEqual(
            [locs.Addr(1)],
            locs.parseLocsToken('1'))
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1), locs.Addr(2))],
            locs.parseLocsToken('1-2'))
        self.assertEqual(
            [locs.Addr(1), locs.Addr(3)],
            locs.parseLocsToken('1,3'))
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1), locs.Addr(2)), locs.Addr(4)],
            locs.parseLocsToken('1-2,4'))
        self.assertEqual(
            [locs.Addr(1, 1)],
            locs.parseLocsToken('1:1'))
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 2))],
            locs.parseLocsToken('1:1-2'))
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(1, 3)],
            locs.parseLocsToken('1:1,3'))
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(1, 2)), locs.Addr(1, 4)],
            locs.parseLocsToken('1:1-2,4'))
        self.assertEqual(
            [locs.AddrRange(locs.Addr(1, 1), locs.Addr(2, 1))],
            locs.parseLocsToken('1:1-2:1'))
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(2, 1)],
            locs.parseLocsToken('1:1,2:1'))
        self.assertEqual(
            [locs.Addr(1, 1), locs.Addr(1, 3), locs.Addr(2, 1)],
            locs.parseLocsToken('1:1,3,2:1'))
        self.assertEqual(
            [locs.Addr(1, 1), locs.AddrRange(locs.Addr(1, 3), locs.Addr(2, 1))],
            locs.parseLocsToken('1:1,3-2:1'))

if __name__ == '__main__':
    unittest.main()
