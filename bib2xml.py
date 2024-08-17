#!/usr/bin/python

import argparse
import sys
import xml.etree.cElementTree as ET
from logging import DEBUG
from pathlib import Path
from typing import Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from pybtex.database.input import bibtex  # https://github.com/chbrown/pybtex

from bib2xml.helper import convert
from bib2xml.logging import get_child_logger

_logger = get_child_logger(__name__)

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument(
    "-a",
    "--append",
    dest="inxml",
    type=Path,
    help="existing filename (e.g. Sources.xml) to append elements to",
)
cli_parser.add_argument(
    "-d",
    "--debug",
    dest="debug",
    action="store_true",
    default=False,
    help="debug (useful for broken .bib entries)",
)
cli_parser.add_argument(
    "-i",
    "--input",
    dest="bibtexfile",
    required=True,
    type=Path,
    help="input bibtex filename",
)
cli_parser.add_argument(
    "-o",
    "--output",
    dest="xmlfile",
    type=Path,
    default=None,
    const=True,
    help="output filename",
)
args = cli_parser.parse_args()

inxml: Optional[Path] = args.inxml
bibtexfile: Path = args.bibtexfile
xmlfile: Optional[Union[Path, Literal[True]]] = args.xmlfile

bib_parser = bibtex.Parser()


bibdata = bib_parser.parse_file(bibtexfile)

url_schema = "http://schemas.microsoft.com/office/word/2004/10/bibliography"
try:
    ET.register_namespace("", url_schema)
    ET.register_namespace("b", url_schema)
    root = ET.parse(inxml).getroot()
except TypeError:
    root = ET.Element(
        "b:Sources",
        {"xmlns:b": url_schema},
    )

for key, entry in bibdata.entries.items():
    if args.debug:
        _logger.setLevel(DEBUG)
        _logger.debug(key)
    source = ET.SubElement(root, "b:Source")
    tag = ET.SubElement(source, "b:Tag")
    tag.text = key
    b = bibdata.entries[key].fields

    srctypes = {
        "book": "Book",
        "article": "JournalArticle",
        "incollection": "ArticleInAPeriodical",
        "inproceedings": "ConferenceProceedings",
        "misc": "Misc",
        "phdthesis": "Report",
        "techreport": "Report",
    }

    try:
        srctype = ET.SubElement(source, "b:SourceType")
        srctype.text = srctypes.get(entry.type)
    except KeyError:
        source.remove(srctype)

    def add_element(source, tagname, keyname):
        try:
            tag = ET.SubElement(source, tagname)
            tag.text = b[keyname]
        except KeyError:
            source.remove(tag)
        return source

    # mapping of MSFT tag to Bibtex field names
    xlate = (
        ("b:Title", "title"),
        ("b:Year", "year"),
        ("b:City", "city"),
        ("b:Publisher", "publisher"),
        ("b:ConferenceName", "organization"),
        ("b:URL", "url"),
        ("b:BookTitle", "booktitle"),
        ("b:ChapterNumber", "chapter"),
        ("b:Edition", "edition"),
        ("b:Institution", "institution"),
        ("b:JournalName", "journal"),
        ("b:Month", "month"),
        ("b:Volume", "volume"),
        ("b:Issue", "number"),
        ("b:Pages", "pages"),
        ("b:Type", "type"),
        ("b:URL", "howpublished"),
    )
    for msft, bibft in xlate:
        source = add_element(source, msft, bibft)

    authors0 = ET.SubElement(source, "b:Author")
    authors1 = ET.SubElement(authors0, "b:Author")
    namelist = ET.SubElement(authors1, "b:NameList")
    for author in bibdata.entries[key].persons["author"]:
        person = ET.SubElement(namelist, "b:Person")
        first = ET.SubElement(person, "b:First")
        try:
            first.text = author.first_names[0]
        except IndexError:
            first.text = ""
        last = ET.SubElement(person, "b:Last")
        last.text = author.last_names[0]

# hack, unable to get register_namespace to work right when parsing the doc
output = ET.tostring(root)
output2 = convert(output)
# xml_file = ET.fromstring(output2)
# tree = ET.ElementTree(xml_file)
# tree.write("xml_output.xml")
try:
    with open(xmlfile, mode="wb") as f:
        f.write(output2.encode("utf-8")[2:-1])
except TypeError:
    print(output2)
