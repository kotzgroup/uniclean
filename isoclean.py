#!/usr/bin/env python3
# Translate input from Unicode (UTF-8) to LaTeX or ASCII equivalents.
# Each file is OVERWRITTEN with the updated text, unless no changes are needed.
#
# usage:
#   isoclean.py [--xml|--latex] file...
# where
#  optional --xml   will translate to XML (HTML) equivalents;
#  optional --latex will translate to LaTeX equivalents;
#  default is plain-text ASCII equivalents.
# The latter two may leave some characters unmapped, and warn to stderr;
# if such warnings occur, search the output for "\N{..}" and fix it by hand.
# Then add a new entry to the mapping tables here, to help others in future!
#
# References:
#  https://docs.python.org/3/howto/unicode.html
#  https://docs.python.org/3/library/stdtypes.html#str.maketrans
#  https://docs.python.org/3/library/stdtypes.html#str.translate
#  https://docs.python.org/3/library/stdtypes.html#str.encode
#  https://docs.python.org/3/library/stdtypes.html#bytes.decode
#
# 2019 David Kotz kotz@dartmouth.edu
# 

import sys

usage = "usage: isoclean.py [--xml|--latex] file..."

if not sys.argv[1:]:
    exit(usage)

############# process arguments #####

# set up the mapping table
if sys.argv[1] == "--xml":
    # XML mappings (also useful for HTML)
    fileList = sys.argv[2:]
    map = { } # we need no map: all non-ASCII will be mapped to '&#xxx;'
    mapErrors = 'xmlcharrefreplace'
elif sys.argv[1] == "--latex":
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
           "á":"\\'{a}",
           "á":"\\'{a}", "à":"\\`{a}",
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
           "á":"a", "à":"a",
           "é":"e", "è":"e",
           "ö":"o",
           "ü":"u",
           "ñ":"n",
           "•":"*"
           }

# either way, build a translation table from that map
mapTable = str.maketrans(map)

# and verify that there are some filenames provided
if not fileList:
    print("No input files specified.")
    sys.exit(usage)

############# process files #########

# Now scan and convert each file
for filename in fileList:
    # open the file in 'text' mode; assume UTF-8; don't translate line-endings
    with open(filename, mode='rt', encoding='UTF-8', newline='') as fInput:
        # read all its text as a Unicode string
        sInput = fInput.read()

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
            print(filename+": unknown Unicode", sText[s:e+1], file=sys.stderr)
            s = e

        # overwrite the original file with the updated string, if different
        if sText != sInput:
            with open(filename, 'wt') as fOutput:
                fOutput.write(sText)

# end of for loop over all filenames
