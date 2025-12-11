"""Helper utilities for BibTeX to XML conversion.

This module provides utility functions and classes used throughout the
bib2xml package. It includes:

- XML manipulation utilities (`add_element`, `escape`)
- General-purpose helper functions (`is_installed`, `is_argument`, `dummy_func`)
- Utility classes (`dummy_tqdm`)
- Decorators (`deprecated`)

These utilities support the core conversion functionality and provide
common operations needed for processing bibliography data.
"""

from ._common import (
    deprecated,
    dummy_func,
    dummy_tqdm,
    is_argument,
    is_installed,
)
from ._xml import add_element, escape

__all__ = (
    "add_element",
    "deprecated",
    "dummy_func",
    "dummy_tqdm",
    "escape",
    "is_argument",
    "is_installed",
)
