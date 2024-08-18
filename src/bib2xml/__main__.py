import argparse
import sys
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

from pybtex.database.input import bibtex  # https://github.com/chbrown/pybtex

from bib2xml import __version__
from bib2xml.core import bib2xml
from bib2xml.logging import get_root_logger

root_logger = get_root_logger()

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

    if args.debug:
        root_logger.setLevel(DEBUG)

    bibtexfile: Path = args.bibtexfile
    xmlfile: Optional[Union[Path, Literal[True]]] = args.xmlfile

    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(bibtexfile)

    # bib to xml
    xml_str = bib2xml(bibdata, inxml=args.inxml)

    if xmlfile:
        if isinstance(xmlfile, Path):
            if xmlfile.is_dir():
                xmlfile /= bibtexfile.with_suffix(".xml").name
        else:
            xmlfile = bibtexfile.with_suffix(".xml")

        with open(xmlfile, mode="wb") as f:
            f.write(xml_str.encode("utf-8"))
    else:
        sys.stdout.write(xml_str + "\n")


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="bib2xml")
