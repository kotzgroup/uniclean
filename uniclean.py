#!/usr/bin/env python3
# Translate input from Unicode (UTF-8) to LaTeX or ASCII equivalents.
# Each file is OVERWRITTEN with the updated text, unless no changes are needed.
# If no files are listed, stdin is processed to stdout.
# Untranslated codes are reported as warnings to stderr.
#
# uniclean.py [--ascii | --xml | --html | --latex]  [filename]...
#
# where
#  default  --ascii will translate to plain-text ASCII equivalents;
#  optional --xml   will translate to XML (HTML) equivalents;
#  optional --html  will translate to HTML (XML) equivalents;
#  optional --latex will translate to LaTeX equivalents.
# The latter two cases may leave some characters unmapped, and warn to stderr;
# if such warnings occur, search the output for "\N{..}" and fix it by hand.
# Then add a new entry to the mapping tables here, to help others in future!
#
# If no files are listed, the stdin is transformed and printed to stdout.
# Otherwise, each file is transformed and written back to the SAME file;
# if no changes were needed, the file is not touched.
#
# Exit 0 if success, non-zero if any Unicode could not be translated.
#
# References:
#  https://docs.python.org/2/library/argparse.html#module-argparse
#  https://docs.python.org/3/howto/unicode.html
#  https://docs.python.org/3/library/stdtypes.html#str.maketrans
#  https://docs.python.org/3/library/stdtypes.html#str.translate
#  https://docs.python.org/3/library/stdtypes.html#str.encode
#  https://docs.python.org/3/library/stdtypes.html#bytes.decode
#  https://stackoverflow.com/questions/16549332/python-3-how-to-specify-stdin-encoding
#
# 2019-20 David Kotz kotz@dartmouth.edu
#

import sys
import argparse

##############################################################################
########### functions to return mapTable and mapErrors ###################

##############################################################################
# Return ASCII mappings; caller can optionally provide an additional map,
# which updates (or replaces) entries in the default map.
def mapASCII(mapp={}): # return (mapTable, mapErrors)
    # plaintext mappings
    map = {
        "«":"<<", "»":">>",
        "‘":"'", "’":"'",
        '“':'"', '”':'"',
        "—":"-", "–":"-",
        "≤":"<=", "≥":">=",
        "©":"(c)",
        "…":"...",
        "á":"a", "à":"a", "ä":"a",
        "é":"e", "è":"e",
        "í":"i",
        "ö":"o", "ó":"o",
        "ü":"u", "ú":"u",
        "č":"c", "ć":"c", "ç":"c", "Ç":"C",
        "ñ":"n",
        "ş":"s",
        "ž":"z",
        "•":"*",
        "\u00A0":" ",  # non-breaking space
        "\u2029":"\n", # paragraph break
        }
    # update the default map with additions (or replacements) from parameter
    map.update(mapp)

    # unmapped codes will output names '\N{...}'
    mapErrors = 'namereplace'

    # build a translation table from that map
    mapTable = str.maketrans(map)
    return (mapTable, mapErrors)

##############################################################################
# Return XML mappings (also useful for HTML); caller can optionally provide an additional map,
# which updates (or replaces) entries in the default map.
def mapXML(map={}): # return (mapTable, mapErrors)
    # the default parameter (empty map) is sufficient.

    # any unmapped non-ASCII chars will be mapped to '&#xxx;'
    mapErrors = 'xmlcharrefreplace'

    # build a translation table from that map
    mapTable = str.maketrans(map)
    return (mapTable, mapErrors)

##############################################################################
# Return LaTeX mappings; caller can optionally provide an additional map,
# which updates (or replaces) entries in the default map.
# Our map also maps non-unicode 'special chars' that cause LaTeX trouble in text mode:
#     # $ % & ~ _ ^ \ { } < = >
def mapLaTeX(mapp={}): # return (mapTable, mapErrors)
    map = {
        "#":r"\#", "$":r"\$", "%":r"\%", "&":r"\&", "{":r"\{", "}":r"\}",
        "~":r"{\textasciitilde}", "^": r"{\textasciicircum}",
        "_":r"{\textunderscore}", "\\":r"{\textbackslash}",
        "<":r"{$<$}", "=": r"{$=$}", ">": r"{$>$}",
        "«":r"{\guillemotleft}",  "»": r"{\guillemotright}",
        "‘":r"`",   "’":r"'",
        '“':r"``",  '”':r"''",
        "—":r"---", "–":r"--",
        "≤":r"$\leq$", "≥":r"$\geq$",
        "©":r"{\textcopyright}",
        "…":r"{\ldots}",
        "á":r"{\'{a}}", "à":r"{\`{a}}", "ä":r'{\"{a}}',
        "é":r"{\'{e}}", "è":r"{\`{e}}",
        "í":r"{\'{\i}}",
        "ö":r'{\"{o}}', "ó":r'{\"{o}}',
        "ü":r'{\"{u}}', "ú":r"{\'{u}}",
        "č":r"{\v{c}}", "ć":r"{\'c}",   "ç":r"{\c{c}}", "Ç":r"{\c{C}}",
        "ñ":r"{\~{n}}",
        "ş":r"{\c{s}}",
        "ž":r"{\v{z}}",   # might not work in all fonts
        "•":r"$\bullet$",
        "\u00A0":r"~",      # non-breaking space
        "\u2029":r"\par ",  # paragraph break
        }
    # update the default map with additions (or replacements) from parameter
    map.update(mapp)

    # unmapped codes will output names '\N{...}'
    mapErrors = 'namereplace'

    # build a translation table from that map
    mapTable = str.maketrans(map)
    return (mapTable, mapErrors)

##############################################################################
########### transform: function to transform Unicode from sInput #############
# arguments:
#   sInput is a str that may contain Unicode
#   maps   is a tuple (table, errors) returned by one of the above functions.
# returns sText, a str with Unicode mapped according to mapTable and mapErrors.
# Any unmapped characters are handled according to second element of 'maps'.
#
# typical usage:
#   sText = uniclean.transform(sInput, uniclean.mapLaTeX())
#
def transform(sInput, maps):
    # map characters to ASCII equivalent, according to above mappings
    (mapTable, mapErrors) = maps
    sText = sInput.translate(mapTable)

    # convert to ASCII byte-string; handle remaining unmapped chars here
    bText = sText.encode('ascii', mapErrors)
    # convert that 'bytes' object back to a 'str' object
    sText = bText.decode('ascii')

    return sText

##############################################################################
########### countUnmapped: count number of unmapped chars left in sText ######
# warn about unreplaced Unicode characters
# arguments:
#   sText is a str that resulted from transform()
#   source is a str that describes the source of sInput (e.g., "stdin" or a filename)
#   warn (optional) is an open File; if present, errors are printed to that file
def countUnmapped(sText, source, warnFile=None):
    nErrors = 0 # number of errors found
    s = 0       # index to start looking within sText
    while r'\N{' in sText[s:]:
        s = sText.find(r'\N{', s)
        e = sText.find('}', s)
        if warnFile:
            print(source+": unknown Unicode", sText[s:e+1], file=warnFile)
        s = e
        nErrors += 1

    return nErrors


##############################################################################
############ main: process arguments, initialize, execute
def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description='''
        Translate Unicode within files, to ASCII, XML, HTML, or LaTeX.
        Each file is processed and overwritten with any changes needed.
        If no files are listed, stdin is processed to stdout.''')
    formatGroup = parser.add_mutually_exclusive_group()
    formatGroup.add_argument('--ascii', action='store_const', \
                                 dest='init', const=mapASCII)
    formatGroup.add_argument('--xml',   action='store_const', \
                                 dest='init', const=mapXML)
    formatGroup.add_argument('--html',  action='store_const', \
                                 dest='init', const=mapXML)
    formatGroup.add_argument('--latex', action='store_const', \
                                 dest='init', const=mapLaTeX)
    parser.add_argument('filename', type=str, nargs='*', \
                            help="file to be updated")
    parser.set_defaults(init=mapASCII)
    args = parser.parse_args()
    maps = args.init() # initialize mapping table needed by transform()

    # number of instances where we could not translate a Unicode
    failureCount = 0

    # Behavior depends on whether arguments include filenames
    if not args.filename:
        # no files listed - process stdin
        # assume UTF-8; don't translate line-endings
        sys.stdin.reconfigure(encoding='UTF-8', newline='')
        sInput = sys.stdin.read()
        sText = transform(sInput, maps)
        failureCount += countUnmapped(sText, "stdin", sys.stderr)
        sys.stdout.write(sText)
    else:
        # one or more files listed - process each in turn
        for filename in args.filename:
            # open the file in 'text' mode
            # assume UTF-8; don't translate line-endings
            with open(filename, mode='rt', encoding='UTF-8', newline='') as f:
                # read all its text as a Unicode string
                sInput = f.read()
                # transform its Unicode characters
                sText = transform(sInput, maps)
                failureCount += countUnmapped(sText, filename, sys.stderr)
                # overwrite the original file with the updated string
                if sText != sInput:  # but only if different
                    with open(filename, 'wt') as fOutput:
                        fOutput.write(sText)

    # exit 0=success, non-zero = number of translation failures
    sys.exit(failureCount)

####################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
