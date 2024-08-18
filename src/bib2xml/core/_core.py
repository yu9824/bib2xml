import xml.etree.cElementTree as ET
from pathlib import Path
from typing import Optional

from pybtex.database import BibliographyData, Entry, Person

from bib2xml.helper import SRCTYPES, XLATE, add_element, escape
from bib2xml.logging import get_child_logger

_logger = get_child_logger(__name__)


URL_SCHEMA = "http://schemas.microsoft.com/office/word/2004/10/bibliography"


def bib2xml(bibdata: BibliographyData, inxml: Optional[Path] = None) -> str:
    if inxml is None:
        root = ET.Element(
            "b:Sources",
            {"xmlns:b": URL_SCHEMA},
        )
    else:
        ET.register_namespace("", URL_SCHEMA)
        ET.register_namespace("b", URL_SCHEMA)
        root = ET.parse(inxml).getroot()

    for key, entry in bibdata.entries.items():
        # typing
        key: str
        entry: Entry

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
        for author in entry.persons["author"]:
            # HACK: typing
            author: Person

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
