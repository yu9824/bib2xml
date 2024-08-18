import argparse
import sys
import xml.etree.cElementTree as ET
from logging import DEBUG
from pathlib import Path
from typing import Optional, Union

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from pybtex.database import Entry, Person
from pybtex.database.input import bibtex  # https://github.com/chbrown/pybtex

from bib2xml import __version__
from bib2xml.helper import SRCTYPES, XLATE, add_element, convert
from bib2xml.logging import get_child_logger

_logger = get_child_logger(__name__)

__all__ = ("main",)


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    cli_parser = argparse.ArgumentParser(
        prog=prog, description="convert .bib to .xml"
    )
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
        nargs="?",
        help="output filename",
    )
    cli_parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="show current version",
        version=f"%(prog)s: {__version__}",
    )
    args = cli_parser.parse_args(cli_args)

    inxml: Optional[Path] = args.inxml
    bibtexfile: Path = args.bibtexfile
    xmlfile: Optional[Union[Path, Literal[True]]] = args.xmlfile

    bib_parser = bibtex.Parser()

    bibdata = bib_parser.parse_file(bibtexfile)

    url_schema = (
        "http://schemas.microsoft.com/office/word/2004/10/bibliography"
    )
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
        # typing
        key: str
        entry: Entry

        if args.debug:
            _logger.setLevel(DEBUG)
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
    xml_str = convert(xml_bytes)
    # xml_file = ET.fromstring(output2)
    # tree = ET.ElementTree(xml_file)
    # tree.write("xml_output.xml")

    if xmlfile:
        if isinstance(xmlfile, Path):
            if xmlfile.is_dir():
                xmlfile /= bibtexfile.with_suffix(".xml").name
        else:
            xmlfile = bibtexfile.with_suffix(".xml")

        with open(xmlfile, mode="wb") as f:
            f.write(xml_str.encode("utf-8")[2:-1])
    else:
        sys.stdout.write(xml_str + "\n")


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="bib2xml")
