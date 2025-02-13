# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 16:37:59 2021
Modified on March 24 2023

@author: matheus.sartor
@author: yu9824
"""

import sys
import xml.etree.cElementTree as ET

from .constants import ESCAPE_LETTER_PAIRS

if sys.version_info >= (3, 9):
    from collections.abc import Mapping
else:
    from typing import Mapping

# mapping of MSFT tag to Bibtex field names


def add_element(
    source: ET.Element, tagname: str, fields: "Mapping[str, str]", keyname: str
) -> ET.Element:
    """
    Add a subelement to the given XML Element `source` with the specified `tagname`,
    setting its text content from `fields[keyname]`.

    Parameters
    ----------
    source : xml.etree.ElementTree.Element
        The XML element to which the subelement will be added.
    tagname : str
        The tag name of the subelement to be created.
    fields : Mapping[str, str]
        A mapping containing the fields from which to extract the content.
    keyname : str
        The key in `fields` whose value will be used as the text content of the subelement.

    Returns
    -------
    xml.etree.ElementTree.Element
        The modified `source` element with the new subelement added.

    Raises
    ------
    KeyError
        If `keyname` is not found in `fields`, the subelement is not added and the
        original `source` is returned without modifications.
    """
    try:
        tag = ET.SubElement(source, tagname)
        tag.text = fields[keyname]
    except KeyError:
        source.remove(tag)
    return source


def escape(text: str) -> str:
    """
    Replace specific characters in the input text based on predefined escape sequences.

    This function converts the input text to a string and replaces occurrences of
    specific characters according to the mappings defined in `ESCAPE_LETTER_PAIRS`.

    Parameters
    ----------
    text : str
        The input text to be escaped.

    Returns
    -------
    str
        The escaped text with specified characters replaced.

    Notes
    -----
    - `ESCAPE_LETTER_PAIRS` must be defined as an iterable of `(old, new)` tuples
      where `old` is the character or substring to be replaced and `new` is its
      replacement.
    - If `text` is not a string, it is first converted using `str(text)`.
    """
    new_text = str(text)
    for old, new in ESCAPE_LETTER_PAIRS:
        new_text = new_text.replace(old, new)
    return new_text


if __name__ == "__main__":
    escape("test")
