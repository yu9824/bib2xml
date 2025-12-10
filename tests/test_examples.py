"""Tests using example files from the examples directory."""

import xml.etree.ElementTree as ET
from pathlib import Path

from pybtex.database.input import bibtex  # type: ignore[import-untyped]

from bib2xml import bib2xml

# Get the project root directory (parent of tests directory)
TEST_ROOT_DIR = Path(__file__).parent.resolve()
BIB_FILE = TEST_ROOT_DIR / "bib-example.bib"
XML_FILE = TEST_ROOT_DIR / "bib-example.xml"


def normalize_xml(xml_str: str) -> str:
    """Normalize XML string for comparison by parsing and re-serializing."""
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
    return ET.tostring(root, encoding="unicode")


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


def test_xml_source_content_comparison():
    """Test that Source element content matches expected XML."""
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

        # Compare all child elements
        result_children = {child.tag: child.text for child in result_source}
        expected_children = {
            child.tag: child.text for child in expected_source
        }

        # Check that all expected elements exist in result
        for key, expected_value in expected_children.items():
            assert key in result_children, (
                f"Missing element '{key}' in result for tag '{tag}'"
            )
            # Compare text content (normalize whitespace)
            result_value = result_children[key] or ""
            expected_value = expected_value or ""
            assert result_value.strip() == expected_value.strip(), (
                f"Element '{key}' mismatch for tag '{tag}': "
                f"'{result_value}' vs '{expected_value}'"
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
