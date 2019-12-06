#!/usr/bin/env python3
# Translate input from Unicode (UTF-8) to LaTeX or ASCII equivalents.
# Each file is OVERWRITTEN with the updated text, unless no changes are needed.
# If no files are listed, stdin is processed to stdout.
# Untranslated codes are reported as warnings to stderr.
#
usage = "usage: isoclean.py [--xml|--latex] [file]..."
# where
#  optional --xml   will translate to XML (HTML) equivalents;
#  optional --latex will translate to LaTeX equivalents;
#  default is plain-text ASCII equivalents.
# The latter two cases may leave some characters unmapped, and warn to stderr;
# if such warnings occur, search the output for "\N{..}" and fix it by hand.
# Then add a new entry to the mapping tables here, to help others in future!
#
# If no files are listed, the stdin is transformed and printed to stdout.
# Otherwise, each file is transformed and written back to the same file; 
# if no changes were needed, the file is not touched.
#
# Exit 0 if success, non-zero if any Unicode could not be translated.
#
# References:
#  https://docs.python.org/3/howto/unicode.html
#  https://docs.python.org/3/library/stdtypes.html#str.maketrans
#  https://docs.python.org/3/library/stdtypes.html#str.translate
#  https://docs.python.org/3/library/stdtypes.html#str.encode
#  https://docs.python.org/3/library/stdtypes.html#bytes.decode
#  https://stackoverflow.com/questions/16549332/python-3-how-to-specify-stdin-encoding
#
# 2019 David Kotz kotz@dartmouth.edu
# 

import sys

# number of instances where we could not translate a Unicode
failureCount = 0

############# main: process arguments #####

# set up the mapping table
if sys.argv[1:] and sys.argv[1] == "--xml":
    # XML mappings (also useful for HTML)
    fileList = sys.argv[2:]
    map = { } # we need no map: all non-ASCII will be mapped to '&#xxx;'
    mapErrors = 'xmlcharrefreplace'
elif sys.argv[1:] and sys.argv[1] == "--latex":
    # latex mappings
    fileList = sys.argv[2:]
    mapErrors = 'namereplace'  # unmapped codes will output names '\N{...}'
    map = {"«":"{\\guillemotleft}", "»":"{\\guillemotright}",
           "‘":"`", "’":"'", 
           '“':"``", '”':"''", 
           "—":"---", "–":"--",
           "≤":"$\\leq$", "≥":"$\\geq$",
           "©":"{\\textcopyright}",
           "…":"{\\ldots}",
           "á":"\\'{a}", "à":"\\`{a}", "ä":'\\"{a}',
           "é":"\\'{e}", "è":"\\`{e}",
           "ö":'\\"{o}',
           "ü":'\\"{u}',
           "ñ":"\\~{n}",
           "•":"$\\bullet$"
           }
else:
    # plaintext mappings
    fileList = sys.argv[1:]
    mapErrors = 'namereplace'  # unmapped codes will output names '\N{...}'
    map = {"«":"<<", "»":">>", 
           "‘":"'", "’":"'", 
           '“':'"', '”':'"', 
           "—":"-", "–":"-",
           "≤":"<=", "≥":">=",
           "©":"(c)",
           "…":"...",
           "á":"a", "à":"a", "ä":"a",
           "é":"e", "è":"e",
           "ö":"o",
           "ü":"u",
           "ñ":"n",
           "•":"*"
           }

# either way, build a translation table from that map
mapTable = str.maketrans(map)


################### transform: function to transform Unicode from sInput #############
# arguments:
#   sInput is a str that may contain Unicode
#   source is a str that describes the source of sInput ("stdin" or a filename)
# return value: a str with Unicode mapped according to mapTable and mapErrors.
# global variable 'failureCount' is incremented for each translation failure.

def transform(sInput, source):
    # track the number of translation failures, over time
    global failureCount

    # map characters to ASCII equivalent, according to above mappings
    sText = sInput.translate(mapTable)

    # convert to ASCII byte-string; handle remaining unmapped chars here
    bText = sText.encode('ascii', mapErrors)
    # convert that 'bytes' object back to a 'str' object
    sText = bText.decode('ascii')

    # warn about unreplaced Unicode characters
    s = 0 # index to start looking within sText
    while '\\N{' in sText[s:]:
        s = sText.find('\\N{', s)
        e = sText.find('}', s)
        print(source+": unknown Unicode", sText[s:e+1], file=sys.stderr)
        s = e
        failureCount += 1

    return sText


############# main: process files or stdin #########

# Behavior depends on whether arguments include filenames
if not fileList:
    # no files listed - process stdin; assume UTF-8; don't translate line-endings
    sys.stdin.reconfigure(encoding='utf-8', newline='')
    sInput = sys.stdin.read()
    sText = transform(sInput, "stdin")
    sys.stdout.write(sText)

else:
    # one or more files listed - process each in turn
    for filename in fileList:
        # open the file in 'text' mode; assume UTF-8; don't translate line-endings
        with open(filename, mode='rt', encoding='UTF-8', newline='') as fInput:
            # read all its text as a Unicode string
            sInput = fInput.read()
            # transform its Unicode characters
            sText = transform(sInput, filename)
            # overwrite the original file with the updated string, if different
            if sText != sInput:
                with open(filename, 'wt') as fOutput:
                    fOutput.write(sText)

# exit 0=success, non-zero = number of translation failures
exit(failureCount)
