#!/usr/bin/env python
'''
Tests for :mod:`addrs`
'''

# Standard imports:
import unittest

# Local imports:
import addrs

class AddrTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(addrs.Addr(1) == addrs.Addr(1))
        self.assertTrue(addrs.Addr(2) == addrs.Addr(2))

    def test_str(self):
        self.assertEqual('1', str(addrs.Addr(1)))
        self.assertEqual('2', str(addrs.Addr(2)))
        self.assertEqual('1:2', str(addrs.Addr(1, 2)))

class RangeTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertTrue(addrs.AddrRange(1, 2) == addrs.AddrRange(1, 2))
        self.assertTrue(
            addrs.AddrRange(addrs.Addr(1), addrs.Addr(2)) == \
                addrs.AddrRange(addrs.Addr(1), addrs.Addr(2)))

    def test_str(self):
        self.assertEqual(
            '1:2-3:4', str(addrs.AddrRange(addrs.Addr(1, 2), addrs.Addr(3, 4))))

class parseTestCase(unittest.TestCase):

    def test_None(self):
        with self.assertRaises(TypeError):
            addrs.parse(None)

    def test_emptyString(self):
        with self.assertRaises(ValueError):
            addrs.parse('')

    def test_syntheticAndMinimal(self):
        self.assertEqual(
            [addrs.Addr(1)],
            addrs.parse('1'))
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1), addrs.Addr(2))],
            addrs.parse('1-2'))
        self.assertEqual(
            [addrs.Addr(1), addrs.Addr(3)],
            addrs.parse('1,3'))
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1), addrs.Addr(2)), addrs.Addr(4)],
            addrs.parse('1-2,4'))
        self.assertEqual(
            [addrs.Addr(1, 1)],
            addrs.parse('1:1'))
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(1, 2))],
            addrs.parse('1:1-2'))
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(1, 3)],
            addrs.parse('1:1,3'))
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(1, 2)), addrs.Addr(1, 4)],
            addrs.parse('1:1-2,4'))
        self.assertEqual(
            [addrs.AddrRange(addrs.Addr(1, 1), addrs.Addr(2, 1))],
            addrs.parse('1:1-2:1'))
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(2, 1)],
            addrs.parse('1:1,2:1'))
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.Addr(1, 3), addrs.Addr(2, 1)],
            addrs.parse('1:1,3,2:1'))
        self.assertEqual(
            [addrs.Addr(1, 1), addrs.AddrRange(addrs.Addr(1, 3), addrs.Addr(2, 1))],
            addrs.parse('1:1,3-2:1'))

if __name__ == '__main__':
    unittest.main()
