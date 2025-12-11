"""Tests using example files from the examples directory."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from pybtex.database.input import bibtex  # type: ignore[import-untyped]

from bib2xml import bib2xml

# Get the project root directory (parent of tests directory)
TEST_ROOT_DIR = Path(__file__).parent.resolve()
BIB_FILE = TEST_ROOT_DIR / "bib-example.bib"
XML_FILE = TEST_ROOT_DIR / "bib-example.xml"


def normalize_xml(xml_str: str) -> str:
    """Normalize XML string for comparison by parsing and re-serializing.

    This function normalizes XML by:
    - Parsing and re-serializing to ensure consistent structure
    - Removing namespace prefixes for comparison
    - Sorting child elements for consistent ordering
    - Removing whitespace (newlines, indentation) between tags
    - Normalizing whitespace in text content
    """
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        # If parsing fails, return original string
        return xml_str

    # Remove namespace prefixes for comparison
    for elem in root.iter():
        if elem.tag.startswith("{http://"):
            elem.tag = elem.tag.split("}")[1]

    # Sort elements for consistent comparison
    def sort_children(elem: ET.Element) -> None:
        elem[:] = sorted(elem, key=lambda x: (x.tag, x.text or ""))

    sort_children(root)
    xml_output = ET.tostring(root, encoding="unicode")

    # Normalize whitespace: remove newlines, tabs, and normalize spaces
    # Remove whitespace between tags (but preserve text content)
    # First, normalize all whitespace characters to single spaces
    xml_output = re.sub(r"\s+", " ", xml_output)
    # Remove spaces between tags (e.g., "> <" becomes "><")
    xml_output = re.sub(r">\s+<", "><", xml_output)
    # Remove leading/trailing whitespace
    xml_output = xml_output.strip()

    return xml_output


def test_bib_to_xml_conversion():
    """Test that bib-example.bib converts correctly to XML."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Read expected XML
    expected_xml = XML_FILE.read_text(encoding="utf-8")

    # Normalize both XML strings for comparison
    normalized_result = normalize_xml(xml_str)
    normalized_expected = normalize_xml(expected_xml)

    # Compare normalized XML
    assert normalized_result == normalized_expected, (
        "Converted XML does not match expected XML"
    )


def test_bib_to_xml_structure():
    """Test that the converted XML has the correct structure."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Parse the XML
    root = ET.fromstring(xml_str)

    # Check root element
    assert (
        root.tag
        == "{http://schemas.microsoft.com/office/word/2004/10/bibliography}Sources"
    )

    # Check that we have Source elements
    sources = root.findall(
        ".//{http://schemas.microsoft.com/office/word/2004/10/bibliography}Source"
    )
    assert len(sources) > 0, "No Source elements found in XML"

    # Check that each Source has a Tag element
    for source in sources:
        tag = source.find(
            "{http://schemas.microsoft.com/office/word/2004/10/bibliography}Tag"
        )
        assert tag is not None, "Source element missing Tag"
        assert tag.text is not None, "Tag element has no text"


def test_bib_entry_count():
    """Test that all BibTeX entries are converted."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Count entries in BibTeX
    bib_entry_count = len(bibdata.entries)

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Parse the XML and count Source elements
    root = ET.fromstring(xml_str)
    xml_source_count = len(
        root.findall(
            ".//{http://schemas.microsoft.com/office/word/2004/10/bibliography}Source"
        )
    )

    # Check that counts match
    assert bib_entry_count == xml_source_count, (
        f"Entry count mismatch: {bib_entry_count} BibTeX entries vs {xml_source_count} XML sources"
    )


def test_xml_source_tags_match():
    """Test that all Source tags in converted XML match expected XML."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Read expected XML
    expected_xml = XML_FILE.read_text(encoding="utf-8")

    # Parse both XML strings
    result_root = ET.fromstring(xml_str)
    expected_root = ET.fromstring(expected_xml)

    # Get all Source elements
    ns = "{http://schemas.microsoft.com/office/word/2004/10/bibliography}"
    result_sources = result_root.findall(f".//{ns}Source")
    expected_sources = expected_root.findall(f".//{ns}Source")

    # Check that we have the same number of sources
    assert len(result_sources) == len(expected_sources), (
        f"Source count mismatch: {len(result_sources)} vs {len(expected_sources)}"
    )

    # Create dictionaries mapping Tag to Source element
    def get_tag_to_source(sources: list[ET.Element]) -> dict[str, ET.Element]:
        tag_to_source = {}
        for source in sources:
            tag_elem = source.find(f"{ns}Tag")
            if tag_elem is not None and tag_elem.text is not None:
                tag_to_source[tag_elem.text] = source
        return tag_to_source

    result_tag_map = get_tag_to_source(result_sources)
    expected_tag_map = get_tag_to_source(expected_sources)

    # Check that all tags match
    assert set(result_tag_map.keys()) == set(expected_tag_map.keys()), (
        f"Tag mismatch: {set(result_tag_map.keys())} vs {set(expected_tag_map.keys())}"
    )


def compare_xml_elements(
    result_elem: ET.Element,
    expected_elem: ET.Element,
    path: str = "",
) -> "list[str]":
    """Recursively compare XML elements and their hierarchical structure.

    Parameters
    ----------
    result_elem : ET.Element
        The result XML element to compare.
    expected_elem : ET.Element
        The expected XML element to compare against.
    path : str
        The current path in the XML hierarchy (for error messages).

    Returns
    -------
    list[str]
        List of error messages. Empty list if elements match.
    """
    errors = []
    current_path = f"{path}/{result_elem.tag}" if path else result_elem.tag

    # Compare tag names
    if result_elem.tag != expected_elem.tag:
        errors.append(
            f"Tag mismatch at '{path}': '{result_elem.tag}' vs '{expected_elem.tag}'"
        )
        return errors

    # Compare text content (normalize whitespace)
    result_text = (result_elem.text or "").strip()
    expected_text = (expected_elem.text or "").strip()
    if result_text != expected_text:
        errors.append(
            f"Text content mismatch at '{current_path}': "
            f"'{result_text}' vs '{expected_text}'"
        )

    # Compare tail content
    result_tail = (result_elem.tail or "").strip()
    expected_tail = (expected_elem.tail or "").strip()
    if result_tail != expected_tail:
        errors.append(
            f"Tail content mismatch at '{current_path}': "
            f"'{result_tail}' vs '{expected_tail}'"
        )

    # Compare attributes
    if result_elem.attrib != expected_elem.attrib:
        errors.append(
            f"Attributes mismatch at '{current_path}': "
            f"{result_elem.attrib} vs {expected_elem.attrib}"
        )

    # Compare child elements
    result_children = list(result_elem)
    expected_children = list(expected_elem)

    # Group children by tag name
    def group_by_tag(
        elements: list[ET.Element],
    ) -> dict[str, list[ET.Element]]:
        grouped: dict[str, list[ET.Element]] = {}
        for elem in elements:
            tag = elem.tag
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(elem)
        return grouped

    result_grouped = group_by_tag(result_children)
    expected_grouped = group_by_tag(expected_children)

    # Check for missing or extra tags
    result_tags = set(result_grouped.keys())
    expected_tags = set(expected_grouped.keys())

    missing_tags = expected_tags - result_tags
    extra_tags = result_tags - expected_tags

    for tag in missing_tags:
        errors.append(f"Missing tag '{tag}' at '{current_path}'")

    for tag in extra_tags:
        errors.append(f"Extra tag '{tag}' at '{current_path}'")

    # Compare children with same tag
    common_tags = result_tags & expected_tags
    for tag in common_tags:
        result_tag_children = result_grouped[tag]
        expected_tag_children = expected_grouped[tag]

        # Compare count
        if len(result_tag_children) != len(expected_tag_children):
            errors.append(
                f"Child count mismatch for tag '{tag}' at '{current_path}': "
                f"{len(result_tag_children)} vs {len(expected_tag_children)}"
            )
            # Continue with minimum count to avoid index errors
            min_count = min(
                len(result_tag_children), len(expected_tag_children)
            )
        else:
            min_count = len(result_tag_children)

        # Compare each child element
        for i in range(min_count):
            child_errors = compare_xml_elements(
                result_tag_children[i],
                expected_tag_children[i],
                current_path,
            )
            errors.extend(child_errors)

    return errors


def test_xml_source_content_comparison():
    """Test that Source element hierarchical structure and content matches expected XML."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Read expected XML
    expected_xml = XML_FILE.read_text(encoding="utf-8")

    # Parse both XML strings
    result_root = ET.fromstring(xml_str)
    expected_root = ET.fromstring(expected_xml)

    ns = "{http://schemas.microsoft.com/office/word/2004/10/bibliography}"

    # Get all Source elements
    result_sources = result_root.findall(f".//{ns}Source")
    expected_sources = expected_root.findall(f".//{ns}Source")

    # Compare each source by tag
    for result_source in result_sources:
        tag_elem = result_source.find(f"{ns}Tag")
        if tag_elem is None or tag_elem.text is None:
            continue

        tag = tag_elem.text

        # Find corresponding source in expected XML
        expected_source = None
        for src in expected_sources:
            expected_tag = src.find(f"{ns}Tag")
            if expected_tag is not None and expected_tag.text == tag:
                expected_source = src
                break

        assert expected_source is not None, (
            f"Source with tag '{tag}' not found in expected XML"
        )

        # Compare hierarchical structure and content
        errors = compare_xml_elements(
            result_source, expected_source, f"Source[{tag}]"
        )

        assert len(errors) == 0, (
            f"Structure/content mismatch for Source with tag '{tag}':\n"
            + "\n".join(f"  - {error}" for error in errors)
        )


def test_xml_first_entry_detailed():
    """Test detailed comparison of the first entry."""
    # Parse the BibTeX file
    bib_parser = bibtex.Parser()
    bibdata = bib_parser.parse_file(BIB_FILE)

    # Get first entry key
    first_entry_key = list(bibdata.entries.keys())[0]

    # Convert to XML
    xml_str = bib2xml(bibdata)

    # Read expected XML
    expected_xml = XML_FILE.read_text(encoding="utf-8")

    # Parse both XML strings
    result_root = ET.fromstring(xml_str)
    expected_root = ET.fromstring(expected_xml)

    ns = "{http://schemas.microsoft.com/office/word/2004/10/bibliography}"

    # Find the first source in both
    result_sources = result_root.findall(f".//{ns}Source")
    expected_sources = expected_root.findall(f".//{ns}Source")

    assert len(result_sources) > 0, "No sources found in result XML"
    assert len(expected_sources) > 0, "No sources found in expected XML"

    # Find source with matching tag
    result_source = None
    expected_source = None

    for src in result_sources:
        tag_elem = src.find(f"{ns}Tag")
        if tag_elem is not None and tag_elem.text == first_entry_key:
            result_source = src
            break

    for src in expected_sources:
        tag_elem = src.find(f"{ns}Tag")
        if tag_elem is not None and tag_elem.text == first_entry_key:
            expected_source = src
            break

    assert result_source is not None, (
        f"Source with tag '{first_entry_key}' not found in result"
    )
    assert expected_source is not None, (
        f"Source with tag '{first_entry_key}' not found in expected"
    )

    # Compare all elements
    result_elements = {child.tag: child.text for child in result_source}
    expected_elements = {child.tag: child.text for child in expected_source}

    # Check key elements
    key_elements = [f"{ns}Tag", f"{ns}SourceType", f"{ns}Title", f"{ns}Year"]
    for key in key_elements:
        if key in expected_elements:
            assert key in result_elements, f"Missing element '{key}' in result"
            result_text = (result_elements[key] or "").strip()
            expected_text = (expected_elements[key] or "").strip()
            assert result_text == expected_text, (
                f"Element '{key}' mismatch: '{result_text}' vs '{expected_text}'"
            )
