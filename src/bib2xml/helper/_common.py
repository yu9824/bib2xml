"""Utility functions for general purposes."""

import inspect
import pkgutil
from typing import Any

# deprecated in python >=3.12
from typing import TypeVar  # isort: skip

import sys

if sys.version_info >= (3, 9):
    from collections.abc import Callable
else:
    from typing import Callable

T = TypeVar("T")

PACKAGE_NAMES = {_module.name for _module in pkgutil.iter_modules()}


def is_installed(package_name: str) -> bool:
    """Check if the package is installed.

    Parameters
    ----------
    package_name : str
        package name like `sklearn`

    Returns
    -------
    bool
        if installed, True
    """
    return package_name in PACKAGE_NAMES


def dummy_func(x: T, *args, **kwargs) -> T:
    """dummy function

    Parameters
    ----------
    x : T
        Anything

    Returns
    -------
    T
        same as input
    """
    return x


def is_argument(__callable: "Callable[..., Any]", arg_name: str) -> bool:
    """Check to see if it is included in the callable argument.

    Parameters
    ----------
    __callable : Callable
        callable object

    arg_name : str
        argument name

    Returns
    -------
    bool
        if included, True
    """
    return arg_name in set(inspect.signature(__callable).parameters.keys())
