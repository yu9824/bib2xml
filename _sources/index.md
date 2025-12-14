# `bib2xml`

A Python package for converting BibTeX files to Microsoft Word Bibliography XML format.

## Overview

`bib2xml` is a tool that converts BibTeX bibliography data into Microsoft Word Bibliography XML format. It provides a command-line interface for easy conversion of BibTeX files to XML format.

## Installation

```bash
pip install git+https://github.com/yu9824/bib2xml.git
```

## Basic Usage

### Command-Line Usage

The most basic usage is to specify a BibTeX file and convert it to XML:

```bash
bib2xml -i references.bib
```

This command will output the converted XML to standard output.

### Specifying Output File

Use the `-o` option to specify the output XML file:

```bash
bib2xml -i references.bib -o references.xml
```

If you specify a directory as the output destination, a file with the same name as the input file but with a `.xml` extension will be created:

```bash
bib2xml -i references.bib -o ./output/
```

### Appending to Existing XML File

Use the `-a` option to append new entries to an existing XML file:

```bash
bib2xml -i new_references.bib -a Sources.xml
```

### Debug Mode

Use the `-d` option to enable debug logging, which is useful for troubleshooting broken BibTeX entries:

```bash
bib2xml -i references.bib -d
```

## Command-Line Options

| Option          | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| `-i, --input`   | Input BibTeX filename (required)                                      |
| `-o, --output`  | Output XML filename. If not specified, output is written to stdout    |
| `-a, --append`  | Existing XML file (e.g., Sources.xml) to append elements to           |
| `-d, --debug`   | Enable debug logging (useful for troubleshooting broken .bib entries) |
| `-v, --version` | Display version number and exit                                       |

## Using from Python API

`bib2xml` can also be used as a Python API:

```python
from pybtex.database.input import bibtex
from bib2xml import bib2xml

# Parse BibTeX file
parser = bibtex.Parser()
bibdata = parser.parse_file("references.bib")

# Convert to XML format
xml_str = bib2xml(bibdata)
print(xml_str)
```

To append to an existing XML file:

```python
from pathlib import Path
from bib2xml import bib2xml

xml_str = bib2xml(bibdata, inxml=Path("Sources.xml"))
```

## Features

- Conversion from BibTeX format to Microsoft Word Bibliography XML format
- Appending entries to existing XML files
- Automatic extraction and structuring of author information
- Proper escaping of LaTeX commands and special characters
- Support for multiple BibTeX entry types

## License

MIT License

## Links

- [GitHub Repository](https://github.com/yu9824/bib2xml)
- [Issue Tracker](https://github.com/yu9824/bib2xml/issues)

```{toctree}
:maxdepth: 2
:caption: API Reference

modules
```
