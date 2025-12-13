"""Processes Bibtex files (.bib), produces Word Bibliography XML (.xml) output

Usage
========

bash
-------

.. code-block:: bash

    bib2xml -i bib-example.bib -o bib-example-xml.xml

Python
-------

.. code-block:: python

    from bib2xml import bib2xml
    from pybtex.database.input import bibtex

    bib_parser = bibtex.Parser()
    xml_str = bib2xml(bib_parser.parse_file("bib-example.bib"))
    with open("bib-example-xml.xml", mode="w") as f:
        f.write(xml_str)

"""

from bib2xml._core._core import bib2xml

__version__ = "0.2.0"
__license__ = "MIT"
__author__ = "yu9824"
__copyright__ = "Copyright © 2025 yu9824"

__all__ = ("bib2xml",)
