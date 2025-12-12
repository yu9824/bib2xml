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

# https://github.com/chbrown/pybtex
from pybtex.database.input import bibtex

from bib2xml import __version__, bib2xml
from bib2xml.logging import get_library_root_logger

root_logger = get_library_root_logger()

__all__ = ("main",)


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    """Main entry point for the command-line interface.

    Parses command-line arguments, converts a BibTeX file to XML format,
    and either writes the output to a file or prints it to stdout.

    Parameters
    ----------
    cli_args : Sequence[str]
        Command-line arguments to parse. Typically `sys.argv[1:]`.
    prog : Optional[str], optional
        Program name to display in help messages. If `None`, defaults to
        the script name. Default is `None`.

    Returns
    -------
    None

    Raises
    ------
    SystemExit
        If argument parsing fails or if the `--version` flag is used.
    FileNotFoundError
        If the input BibTeX file does not exist.
    ValueError
        If the BibTeX file cannot be parsed.

    Notes
    -----
    Command-line options:
        - ``-a, --append``: Path to an existing XML file to append elements to.
        - ``-d, --debug``: Enable debug logging for troubleshooting broken entries.
        - ``-i, --input``: Input BibTeX filename (required).
        - ``-o, --output``: Output XML filename. If not specified, output is
          written to stdout. If a directory is specified, the output file
          will be created in that directory with the same name as the input
          file but with a `.xml` extension.
        - ``--pretty``: Format output XML with indentation for better readability.
        - ``-v, --version``: Display the version number and exit.

    Examples
    --------
    >>> main(["-i", "references.bib", "-o", "references.xml"])
    >>> main(["-i", "references.bib", "-a", "Sources.xml"])
    >>> main(["-i", "references.bib"])  # Output to stdout
    """
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
        "--pretty",
        dest="pretty",
        action="store_true",
        default=False,
        help="format output XML with indentation for better readability",
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
    xml_str = bib2xml(bibdata, inxml=args.inxml, pretty=args.pretty)

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
    """Entry point function called when the package is executed as a script.

    This function is typically called when the package is invoked via the
    command line using ``python -m bib2xml`` or through the installed
    ``bib2xml`` command. It parses ``sys.argv[1:]`` and passes the arguments
    to the ``main`` function.

    Returns
    -------
    None

    See Also
    --------
    main : Main function that performs the actual conversion.

    Notes
    -----
    This function is registered as the entry point in ``pyproject.toml``
    under ``[project.scripts]``, allowing it to be called directly from
    the command line.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="bib2xml")
