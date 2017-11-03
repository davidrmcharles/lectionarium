#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible
import locs

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

class formatVerseTestCase(unittest.TestCase):

    def test_1(self):
        '''
        Here is a single verse of prose.
        '''

        paragraphs = []
        bible._formatVerse(
            paragraphs,
            (3, 16),
            'Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret: ut omnis qui credit in eum, non pereat, sed habeat vitam æternam.')

        self.assertEqual(1, len(paragraphs))

        expectedText = '''\
[3:16] Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret: ut omnis
qui credit in eum, non pereat, sed habeat vitam æternam.'''
        self.assertEqual(
            expectedText,
            paragraphs[-1].formatForConsole())

    def test_2(self):
        '''
        Here is a single verse that begins in prose but departs into
        two lines of poetry, and terminates with the end of that
        poetry.
        '''

        paragraphs = []
        bible._formatVerse(
            paragraphs,
            (3, 4),
            'Est autem Deus verax: omnis autem homo mendax, sicut scriptum est: [Ut justificeris in sermonibus tuis:/ et vincas cum judicaris.]')

        # Because this verse terminates with the end of poetry, it
        # terminates at the end of a paragraph, so _formatVerse() must
        # append an additional, empty Paragraph.  This is because it
        # may be called again, and if so, the next verse must go into
        # a new Paragraph of the appropriate type, and not be added to
        # the paragraph of poetry.
        self.assertTrue(paragraphs[-1].isEmpty)
        paragraphs.pop()

        self.assertEqual(2, len(paragraphs))

        expectedText = '''\
[3:4] Est autem Deus verax: omnis autem homo mendax, sicut scriptum est:
            Ut justificeris in sermonibus tuis:
                et vincas cum judicaris.'''
        self.assertEqual(
            expectedText,
            '\n'.join([
                    paragraph.formatForConsole()
                    for paragraph
                    in paragraphs
                    ]))

    def test_3(self):
        '''
        Here is one piece of poetry immediately followed by another.

        During development, I observed the creation of an empty
        paragraph between the two poetry selections.
        '''

        paragraphs = []
        bible._formatVerse(
            paragraphs, (3, 9), '[Audi, Israël, mandata vitæ:/ auribus percipe, ut scias prudentiam./')
        bible._formatVerse(
            paragraphs, (3, 38), 'Post hæc in terris visus est,/ et cum hominibus conversatus est.]')
        bible._formatVerse(
            paragraphs, (4, 1), '[Hic liber mandatorum Dei,/ et lex quæ est in æternum:/ omnes qui tenent eam pervenient ad vitam:/ qui autem dereliquerunt eam, in mortem./')

        expectedText = '''\
[3:9]       Audi, Israël, mandata vitæ:
                auribus percipe, ut scias prudentiam.
[3:38]          Post hæc in terris visus est,
                et cum hominibus conversatus est.
[4:1]       Hic liber mandatorum Dei,
                et lex quæ est in æternum:
                omnes qui tenent eam pervenient ad vitam:
                qui autem dereliquerunt eam, in mortem.'''
        self.assertEqual(
            expectedText,
            '\n'.join([
                    paragraph.formatForConsole()
                    for paragraph
                    in paragraphs
                    ]))

if __name__ == '__main__':
    unittest.main()
