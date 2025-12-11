import xml.etree.cElementTree as ET
from pathlib import Path
from typing import Optional

from pybtex.database import (  # type: ignore[import-untyped]
    BibliographyData,
    Entry,
    Person,
)

from bib2xml.helper import add_element, escape
from bib2xml.helper.constants import SRCTYPES, XLATE
from bib2xml.logging import get_child_logger

_logger = get_child_logger(__name__)


URL_SCHEMA = "http://schemas.microsoft.com/office/word/2004/10/bibliography"


def bib2xml(bibdata: BibliographyData, inxml: Optional[Path] = None) -> str:
    """Convert bibliography data into an XML formatted string.

    This function converts a parsed BibTeX bibliography database into Microsoft
    Word Bibliography XML format. Each entry in the bibliography is transformed
    into a `<b:Source>` element with appropriate subelements for fields and authors.

    Parameters
    ----------
    bibdata : BibliographyData
        The bibliography data containing entries to be converted. This should
        be a `pybtex.database.BibliographyData` object obtained from parsing
        a BibTeX file.
    inxml : Path, optional
        Path to an existing XML file to update. If provided, the function will
        parse the existing XML and append new entries to it. If `None` (default),
        a new XML structure is created from scratch.

    Returns
    -------
    str
        A string representation of the bibliography data in XML format, compatible
        with Microsoft Word's bibliography system. The XML uses the namespace
        defined by `URL_SCHEMA`.

    Notes
    -----
    - The function converts `bibdata` into an XML format compatible with
      `URL_SCHEMA` (Microsoft Word Bibliography schema).
    - If `inxml` is provided, it attempts to parse and update the existing XML file.
      The existing entries are preserved, and new entries are appended.
    - If an entry type does not have a corresponding source type in `SRCTYPES`,
      the `<b:SourceType>` element is omitted for that entry, but the entry
      is still included in the output.
    - Author names are extracted from the `author` field and structured under
      the `<b:Author>` tag hierarchy. If an author's first name is missing,
      an empty string is used.
    - The output XML is escaped to handle special characters and LaTeX commands
      commonly found in BibTeX entries.

    Examples
    --------
    >>> from pybtex.database.input import bibtex
    >>> from bib2xml import bib2xml
    >>>
    >>> parser = bibtex.Parser()
    >>> bibdata = parser.parse_file("references.bib")
    >>> xml_str = bib2xml(bibdata)
    >>> print(xml_str[:100])  # Print first 100 characters
    >>>
    >>> # Append to existing XML file
    >>> xml_str = bib2xml(bibdata, inxml=Path("Sources.xml"))
    """
    if inxml is None:
        root = ET.Element(
            "b:Sources",
            {"xmlns:b": URL_SCHEMA},
        )
    else:
        ET.register_namespace("", URL_SCHEMA)
        ET.register_namespace("b", URL_SCHEMA)
        root = ET.parse(inxml).getroot()

    # typing
    key: str
    entry: Entry
    for key, entry in bibdata.entries.items():
        _logger.debug(key)

        source = ET.SubElement(root, "b:Source")
        tag = ET.SubElement(source, "b:Tag")
        tag.text = key
        fields = entry.fields

        try:
            srctype = ET.SubElement(source, "b:SourceType")
            srctype.text = SRCTYPES.get(entry.type)
        except KeyError:
            source.remove(srctype)

        for msft, bibft in XLATE:
            source = add_element(source, msft, fields, bibft)

        authors0 = ET.SubElement(source, "b:Author")
        authors1 = ET.SubElement(authors0, "b:Author")
        namelist = ET.SubElement(authors1, "b:NameList")

        # typing
        author: Person
        for author in entry.persons["author"]:
            person = ET.SubElement(namelist, "b:Person")
            first = ET.SubElement(person, "b:First")
            try:
                first.text = author.first_names[0]
            except IndexError:
                first.text = ""
            last = ET.SubElement(person, "b:Last")
            last.text = author.last_names[0]

    # hack, unable to get register_namespace to work right when parsing the doc
    xml_bytes = ET.tostring(root)
    return escape(xml_bytes.decode(encoding="utf-8"))
