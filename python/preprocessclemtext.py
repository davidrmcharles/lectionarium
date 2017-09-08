#!/usr/bin/env python
'''
Preprocess the ``clemtext`` provided by
http://vulsearch.sourceforge.net/index.html

Here are the changes we currently make:

* Rename each file to match our ``normalName`` for each book.
* Change enconding from Windows-1252 to UTF-8.
* Change line endings from DOS to Unix.
'''

# Standard Python imports:
import argparse
import os

# This is a mapping of the name of each *input* file to the name of
# its corresponding *output* file.
_fileNames = {
    '1Cor.lat' : '1corinthians.txt',
    '1Jo.lat' : '1john.txt',
    '1Mcc.lat' : '1maccabees.txt',
    '1Par.lat' : '1chronicles.txt',
    '1Ptr.lat' : '1peter.txt',
    '1Rg.lat' : '1samuel.txt',
    '1Thes.lat' : '1thessalonians.txt',
    '1Tim.lat' : '1timothy.txt',
    '2Cor.lat' : '2corinthians.txt',
    '2Jo.lat' : '2john.txt',
    '2Mcc.lat' : '2maccabees.txt',
    '2Par.lat' : '2chronicles.txt',
    '2Ptr.lat' : '2peter.txt',
    '2Rg.lat' : '2samuel.txt',
    '2Thes.lat' : '2thessalonians.txt',
    '2Tim.lat' : '2timothy.txt',
    '3Jo.lat' : '3john.txt',
    '3Rg.lat' : '1kings.txt',
    '4Rg.lat' : '2kings.txt',
    'Abd.lat' : 'obadiah.txt',
    'Act.lat' : 'acts.txt',
    'Agg.lat' : 'haggai.txt',
    'Am.lat' : 'amos.txt',
    'Apc.lat' : 'revelation.txt',
    'Bar.lat' : 'baruch.txt',
    'Col.lat' : 'colossians.txt',
    'Ct.lat' : 'songofsongs.txt',
    'Dn.lat' : 'daniel.txt',
    'Dt.lat' : 'deuteronomy.txt',
    'Ecl.lat' : 'ecclesiastes.txt',
    'Eph.lat' : 'ephesians.txt',
    'Esr.lat' : 'ezra.txt',
    'Est.lat' : 'esther.txt',
    'Ex.lat' : 'exodus.txt',
    'Ez.lat' : 'ezekiel.txt',
    'Gal.lat' : 'galatians.txt',
    'Gn.lat' : 'genesis.txt',
    'Hab.lat' : 'habakkuk.txt',
    'Hbr.lat' : 'hebrews.txt',
    'Is.lat' : 'isaiah.txt',
    'Jac.lat' : 'james.txt',
    'Jdc.lat' : 'judges.txt',
    'Jdt.lat' : 'judith.txt',
    'Job.lat' : 'job.txt',
    'Joel.lat' : 'joel.txt',
    'Jo.lat' : 'john.txt',
    'Jon.lat' : 'jonah.txt',
    'Jos.lat' : 'joshua.txt',
    'Jr.lat' : 'jeremiah.txt',
    'Jud.lat' : 'jude.txt',
    'Lam.lat' : 'lamentations.txt',
    'Lc.lat' : 'luke.txt',
    'Lv.lat' : 'leviticus.txt',
    'Mal.lat' : 'malachi.txt',
    'Mch.lat' : 'michah.txt',
    'Mc.lat' : 'mark.txt',
    'Mt.lat' : 'matthew.txt',
    'Nah.lat' : 'nahum.txt',
    'Neh.lat' : 'nehemiah.txt',
    'Nm.lat' : 'numbers.txt',
    'Os.lat' : 'hosea.txt',
    'Phlm.lat' : 'philemon.txt',
    'Phlp.lat' : 'philippians.txt',
    'Pr.lat' : 'proverbs.txt',
    'Ps.lat' : 'psalms.txt',
    'Rom.lat' : 'romans.txt',
    'Rt.lat' : 'ruth.txt',
    'Sap.lat' : 'wisdom.txt',
    'Sir.lat' : 'sirach.txt',
    'Soph.lat' : 'zephaniah.txt',
    'Tit.lat' : 'titus.txt',
    'Tob.lat' : 'tobit.txt',
    'Zach.lat' : 'zechariah.txt',
    }

def main():
    # Parse the options.
    argParser = argparse.ArgumentParser(
        description='''\
Preprocess the ``clemtext`` provided by http://vulsearch.sourceforge.net/index.html'
''')
    argParser.add_argument(
        '--input-folder',
        metavar='INPUTFOLDER',
        dest='inputFolderPath',
        type=str,
        default='./clemtext',
        help='The input folder path.')
    argParser.add_argument(
        '--output-folder',
        metavar='OUTPUTFOLDER',
        dest='outputFolderPath',
        type=str,
        default='./myclemtext',
        help='The output folder path.')
    args = argParser.parse_args()

    # Go!
    for inputFileName, outputFileName in _fileNames.iteritems():
        inputFilePath = os.path.join(args.inputFolderPath, inputFileName)
        with open(inputFilePath, 'rU') as inputFile:
            outputFilePath = os.path.join(args.outputFolderPath, outputFileName)
            with open(outputFilePath, 'w') as outputFile:
                outputFile.write(
                    inputFile.read().decode('Windows-1252'). encode('utf-8'))

if __name__ == '__main__':
    main()
