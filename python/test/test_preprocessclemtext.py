#!/usr/bin/env python
'''
Tests for :mod:`prepreocessclemtext`
'''

# Standard imports:
import unittest

# Local imports:
import preprocessclemtext

class removeSpaceBeforePunctuationTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(
            'Then he said to me: why?',
            preprocessclemtext._removeSpaceBeforePunctuation(
                'Then he said to me : why ?'))

if __name__ == '__main__':
    unittest.main()
