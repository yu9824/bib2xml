from types import MappingProxyType

# mapping of MSFT tag to Bibtex field names
XLATE: "tuple[tuple[str, str], ...]" = (
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
"""
Mapping of XML bibliographic field names to BibTeX-style field names.

This tuple of tuples provides a predefined mapping between bibliographic XML element
names (prefixed with `"b:"`) and their corresponding BibTeX-style field names.

Each inner tuple contains:
    - The XML element name as a string.
    - The corresponding BibTeX-style field name as a string.

Notes
-----
- This mapping is useful for converting XML-based bibliographic data to BibTeX format.
- The `"b:URL"` field appears twice, mapping to both `"url"` and `"howpublished"`,
  which may require special handling to avoid conflicts.
"""

SRCTYPES = MappingProxyType(
    {
        "book": "Book",
        "article": "JournalArticle",
        "incollection": "ArticleInAPeriodical",
        "inproceedings": "ConferenceProceedings",
        "misc": "Misc",
        "phdthesis": "Report",
        "techreport": "Report",
    }
)
"""
Mapping of source types to standardized reference types.

This dictionary-like immutable mapping provides a conversion from common
bibliographic source type keys to their corresponding standardized reference
type names.

Examples
--------
>>> SRCTYPES["book"]
'Book'

>>> SRCTYPES["article"]
'JournalArticle'

Notes
-----
This mapping is implemented using `MappingProxyType` to ensure that it is
immutable and cannot be modified at runtime.

Keys represent common BibTeX-like source types, and values represent their
standardized reference type names.
"""
