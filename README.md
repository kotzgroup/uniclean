# uniclean

Translate input from Unicode (UTF-8) to LaTeX or ASCII equivalents.
Each file is ***OVERWRITTEN*** with the updated text, unless no changes are needed.
If no files are listed, stdin is processed to stdout.
Untranslated codes are reported as warnings to stderr.


	usage: uniclean.py [-h] [--ascii | --xml | --html | --latex]
                   [filename [filename ...]]
where

 * default  `--ascii` will translate to plain text (ASCII) equivalents;
 * optional `--xml`   will translate to XML (HTML) equivalents;
 * optional `--html`  will translate to HTML (XML) equivalents;
 * optional `--latex` will translate to LaTeX equivalents;

The ASCII and LaTeX cases may leave some characters unmapped, and warn to stderr;
if such warnings occur, search the output for `\N{..}` and fix it by hand.
Then add a new entry to the mapping tables here, to help others in future!

If no files are listed, the stdin is transformed and printed to stdout.
Otherwise, each file is transformed and written back to the same file; if no changes were needed, the file is not touched.

## TODO

* needs an ‘encoding’ switch, to allow user to pick an encoding other than utf-8; see the [list](https://docs.python.org/3/library/codecs.html#standard-encodings) of encodings supported by Python.

## References:
 * [https://docs.python.org/3/howto/unicode.html]()

## Author
David Kotz, 2019: <kotz@dartmouth.edu>

