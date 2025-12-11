"""Core module for BibTeX to XML conversion.

This module provides the main conversion functionality for transforming
BibTeX bibliography data into Microsoft Word Bibliography XML format.

The primary function in this module is `bib2xml`, which takes a parsed
BibTeX database and converts it to an XML string compatible with Word's
bibliography system.
"""

from ._core import bib2xml

__all__ = ("bib2xml",)
