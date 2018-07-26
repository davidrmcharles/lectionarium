#!/usr/bin/env python
'''
Tests for :mod:`lectionaryviews`
'''

# Standard imports:
import StringIO
import sys
import unittest

# Local imports:
import lectionaryviews

class mainTestCase(unittest.TestCase):

    def test_noArguments(self):
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        with self.assertRaises(SystemExit):
            lectionaryviews.main([])
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

class LengthOfPathTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(1, lectionaryviews._lengthOfPath('foo'))
        self.assertEqual(2, lectionaryviews._lengthOfPath('foo/bar'))
        self.assertEqual(3, lectionaryviews._lengthOfPath('foo/bar/zod'))

if __name__ == '__main__':
    unittest.main()
