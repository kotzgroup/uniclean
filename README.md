# isoclean

Translate input from Unicode (UTF-8) to LaTeX or ASCII equivalents.
Each file is ***OVERWRITTEN*** with the updated text, unless no changes are needed.

usage:

```
   isoclean.py [--xml|--latex] file...
```

where

 * optional `--xml`   will translate to XML (HTML) equivalents;
 * optional `--latex` will translate to LaTeX equivalents;
 * default is plain-text ASCII equivalents.

The latter two may leave some characters unmapped, and warn to stderr;
if such warnings occur, search the output for `\N{..}` and fix it by hand.
Then add a new entry to the mapping tables here, to help others in future!

## References:
 * [https://docs.python.org/3/howto/unicode.html]()
 * [https://docs.python.org/3/library/stdtypes.html#str.maketrans]()
 * [https://docs.python.org/3/library/stdtypes.html#str.translate]()
 * [https://docs.python.org/3/library/stdtypes.html#str.encode]()
 * [https://docs.python.org/3/library/stdtypes.html#bytes.decode]()

## Author
2019 David Kotz kotz@dartmouth.edu

