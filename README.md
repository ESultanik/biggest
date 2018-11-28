# Biggest

A utility for finding the largest directories and/or files in a given
directory hierarchy. Biggest supports pretty printed and colorized
output to the terminal:
![Example of Biggest being run](docs/images/example.gif)

All pretty printing and ANSI color codes are printed to STDERR, while the actual file paths are printed to STDOUT. Therefore, suppressing STDERR output will only print the file paths with no ANSI escape sequences, pretty printing, or file sizes, which can be used for scripting:
![Use Biggest in scripts by suppressing STDERR](docs/images/raw.gif)

## Installation

Simply run
```
$ pip3 install biggest
```

## Output

Unlike similar utilities, Biggest will only return a directory if the
sum of the sizes of its immediate files _minus the sizes of any files
included in the Biggest output_ make it large enough to be
included. That’s a complicated, self-referential definition, so here’s
an example:
- Say the directory `/tmp/` looks like this:
```
/tmp/
├── [25 MB] a.zip
├── [15 MB] b.zip
└── /tmp/foo
    ├── [20 MB] c.zip
    └── [10 MB] d.zip
```
- Running `biggest /tmp/ -n 3` will yield `a.zip`, `c.zip`, and `b.zip`. The directory `/tmp/foo` did not make the cut because its file `b.zip` was large enough to be included, and therefore its 20 megabytes were not included in the size of `/tmp/foo`
- Now lets say a new file `e.zip` that is 50 megabytes is added to `/tmp`. Now `biggest /tmp/ -n 3` will return `e.zip`, `/tmp/foo`, and `a.zip`. `/tmp/foo` was included this time because none of its files were large enough to make the cut, and therefore its size was interpreted as 30 megabytes.

Why does Biggest use this algorithm? Since a directory is always at least as large as its largest file, then, if Biggest didn’t use this algorithm, it would always return the directories containing the largest files!

Biggest uses a very efficient (and perhaps optimal) implementation of this algorithm. The worst case runtime is roughly _O_(𝑛 log 𝑚), where 𝑛 is the `-n` argument passed to Biggest and 𝑚 is the number of files and directories being analyzed, but validating that is left as an exercise for the reader.

## Options

- **`-f`** ignore directories and only find the largest files
- **`-h`** prints file sizes with human-readable unit suffixes like "MB" and "GB"

## Requirements

* Python 3.6 or newer
* [Colorama](https://github.com/tartley/colorama)

## License

Biggest is licensed and distributed under the [AGPLv3](LICENSE) license. [Contact us](https://www.sultanik.com/) if you’re looking for an exception to the terms.
