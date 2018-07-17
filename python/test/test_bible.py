#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Tests for :mod:`bible`
'''

# Standard imports:
import unittest

# Local imports:
import bible

class parseTestCase(unittest.TestCase):

    def test_foo_bar_zod(self):
        self.assertEquals(
            (None, 0),
            bible.parse(['foo', 'bar', 'zod']))

    def test_Song_of_Songs(self):
        self.assertEquals(
            ('songofsongs', 3),
            bible.parse(['Song', 'of', 'Songs']))

    def test_John_3_16(self):
        self.assertEquals(
            ('john', 1),
            bible.parse(['John', '3:16']))

    def test_1_John(self):
        self.assertEquals(
            ('1john', 2),
            bible.parse(['1', 'John']))

class BibleTestCase(unittest.TestCase):

    def test_findBook(self):
        self.assertIsNotNone(bible.findBook('Genesis'))
        self.assertIsNotNone(bible.findBook('genesis'))
        self.assertIsNotNone(bible.findBook('GENESIS'))
        self.assertIsNotNone(bible.findBook('GeNeSIs'))

        self.assertIsNotNone(bible.findBook('Gn'))
        self.assertIsNotNone(bible.findBook('gn'))
        self.assertIsNotNone(bible.findBook('GN'))
        self.assertIsNotNone(bible.findBook('gN'))

class BookTestCase(unittest.TestCase):

    def test_normalName(self):
        self.assertEqual('genesis', bible.Book('Genesis', ['Gn']).normalName)

    def test_normalAbbreviations(self):
        self.assertEqual(
            ['gn'], bible.Book('Genesis', ['Gn']).normalAbbreviations)

    def test_matchesToken(self):
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('Genesis'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('genesis'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GENESIS'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GeNesIs'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('Gn'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('gn'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('GN'))
        self.assertTrue(bible.Book('Genesis', ['Gn']).matchesToken('gN'))

    def test_str(self):
        self.assertEqual('Genesis (Gn)', str(bible.Book('Genesis', ['Gn'])))

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

class VerseFormatterTestCase(unittest.TestCase):

    def test_1(self):
        '''
        Here is a single verse of prose.
        '''

        verseFormatter = bible.VerseFormatter()
        verseFormatter.useColor = False
        verseFormatter.formatVerses([
                ((3, 16), 'Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret: ut omnis qui credit in eum, non pereat, sed habeat vitam æternam.')
            ])

        self.assertEqual(1, len(verseFormatter.paragraphs))

        expectedText = '''\
[3:16] Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret: ut omnis
qui credit in eum, non pereat, sed habeat vitam æternam.
'''
        self.assertEqual(expectedText, verseFormatter.consoleFormattedText)

    def test_2(self):
        '''
        Here is a single verse that begins in prose but departs into
        two lines of poetry, and terminates with the end of that
        poetry.
        '''

        verseFormatter = bible.VerseFormatter()
        verseFormatter.useColor = False
        verseFormatter.formatVerses([
                ((3, 4), 'Est autem Deus verax: omnis autem homo mendax, sicut scriptum est: [Ut justificeris in sermonibus tuis:/ et vincas cum judicaris.]')
                ])

        self.assertEqual(2, len(verseFormatter.paragraphs))

        expectedText = '''\
[3:4] Est autem Deus verax: omnis autem homo mendax, sicut scriptum est:
            Ut justificeris in sermonibus tuis:
                et vincas cum judicaris.
'''
        self.assertEqual(expectedText, verseFormatter.consoleFormattedText)

    def test_3(self):
        '''
        Here is one piece of poetry immediately followed by another.

        During development, I observed the creation of an empty
        paragraph between the two poetry selections.
        '''

        verseFormatter = bible.VerseFormatter()
        verseFormatter.useColor = False
        verseFormatter.formatVerses([
            ((3, 9), '[Audi, Israël, mandata vitæ:/ auribus percipe, ut scias prudentiam./'),
            ((3, 38), 'Post hæc in terris visus est,/ et cum hominibus conversatus est.]'),
            ((4, 1), '[Hic liber mandatorum Dei,/ et lex quæ est in æternum:/ omnes qui tenent eam pervenient ad vitam:/ qui autem dereliquerunt eam, in mortem./')
            ])

        expectedText = '''\
[3:9]       Audi, Israël, mandata vitæ:
                auribus percipe, ut scias prudentiam.
[3:38]          Post hæc in terris visus est,
                et cum hominibus conversatus est.
[4:1]       Hic liber mandatorum Dei,
                et lex quæ est in æternum:
                omnes qui tenent eam pervenient ad vitam:
                qui autem dereliquerunt eam, in mortem.
'''
        self.assertEqual(expectedText, verseFormatter.consoleFormattedText)

    def test_htmlFormattedText_obadiah_1_2(self):
        '''
        Obadiah verses 1 and 2 contains a transition from prose to
        poetry.
        '''

        formatter = bible.VerseFormatter()
        formatter.useColor = False
        formatter.formatVerses([
                ((1, 1), 'Visio Abdiæ. [Hæc dicit Dominus Deus ad Edom:/ Auditum audivimus a Domino,/ et legatum ad gentes misit:/ surgite, et consurgamus adversus eum in prælium./'),
                ((1, 2), 'Ecce parvulum dedi te in gentibus:/ contemptibilis tu es valde./'),
                ])

        expectedText = '''\
<p><a name="1:1"><sup class="prose-verse-number">1</sup></a> Visio Abdiæ.</p>
<p class="first-verse-of-poetry">
  Hæc dicit Dominus Deus ad Edom:<br/>
  Auditum audivimus a Domino,<br/>
  et legatum ad gentes misit:<br/>
  surgite, et consurgamus adversus eum in prælium.<br/>
</p>
<p class="non-first-verse-of-poetry">
  <a name="1:2"><sup class="poetry-verse-number">2</sup></a>
  Ecce parvulum dedi te in gentibus:<br/>
  contemptibilis tu es valde.<br/>
</p>
'''

        self.assertEqual(expectedText, formatter.htmlFormattedText)

    def test_htmlFormattedText_obadiah_16_17(self):
        '''
        Obadiah verses 16 and 17 is poetry with an intervening
        paragraph break.
        '''

        formatter = bible.VerseFormatter()
        formatter.useColor = False
        formatter.formatVerses([
                ((1, 16), '[Quomodo enim bibistis super montem sanctum meum,/ bibent omnes gentes jugiter:/ et bibent, et absorbebunt,/ et erunt quasi non sint.\\'),
                ((1, 17), 'Et in monte Sion erit salvatio, et erit sanctus;/ et possidebit domus Jacob eos qui se possederant./'),
                ])

        expectedText = '''\
<p class="first-verse-of-poetry">
  <a name="1:16"><sup class="poetry-verse-number">16</sup></a>
  Quomodo enim bibistis super montem sanctum meum,<br/>
  bibent omnes gentes jugiter:<br/>
  et bibent, et absorbebunt,<br/>
  et erunt quasi non sint.<br/>
</p>


<p class="first-verse-of-poetry">
  <a name="1:17"><sup class="poetry-verse-number">17</sup></a>
  Et in monte Sion erit salvatio, et erit sanctus;<br/>
  et possidebit domus Jacob eos qui se possederant.<br/>
</p>
'''

        self.assertEqual(expectedText, formatter.htmlFormattedText)

if __name__ == '__main__':
    unittest.main()
