"""Utility functions for general purposes."""

import importlib.util
import inspect
import warnings
from functools import wraps
from typing import Any, Optional

# deprecated in python >=3.12
from typing import TypeVar  # isort: skip

import sys

if sys.version_info >= (3, 9):
    from collections.abc import Callable, Iterable, Iterator
else:
    from typing import Callable, Iterable, Iterator
if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


T = TypeVar("T")


def is_installed(package_name: str) -> bool:
    """
    Check whether a given Python package is installed.

    Uses `importlib.util.find_spec` to determine if the specified package
    can be imported.

    Parameters
    ----------
    package_name : str
        The name of the package (e.g., "sklearn").

    Returns
    -------
    bool
        True if the package is installed, False otherwise.
    """
    return bool(importlib.util.find_spec(package_name))


def dummy_func(x: T, *args, **kwargs) -> T:
    """Identity function that returns its first argument unchanged.

    This function ignores all arguments except the first one and returns
    it as-is. It is useful as a placeholder or default function when
    a no-operation function is needed.

    Parameters
    ----------
    x : T
        The value to return. Can be any type.
    *args
        Additional positional arguments (ignored).
    **kwargs
        Additional keyword arguments (ignored).

    Returns
    -------
    T
        The same value as the input `x`, unchanged.

    Examples
    --------
    >>> dummy_func(42)
    42
    >>> dummy_func("hello", "world", key="value")
    'hello'
    >>> dummy_func([1, 2, 3])
    [1, 2, 3]
    """
    return x


def is_argument(__callable: "Callable[..., Any]", arg_name: str) -> bool:
    """Check if a callable accepts a specific argument name.

    This function inspects the signature of a callable object and determines
    whether it accepts an argument with the specified name. This is useful
    for checking function signatures dynamically, especially when dealing
    with optional arguments or different function versions.

    Parameters
    ----------
    __callable : Callable[..., Any]
        A callable object (function, method, class, etc.) whose signature
        should be inspected.
    arg_name : str
        The name of the argument to check for in the callable's signature.

    Returns
    -------
    bool
        `True` if the callable accepts an argument with the name `arg_name`,
        `False` otherwise.

    Examples
    --------
    >>> def example_func(a, b, c=None):
    ...     pass
    ...
    >>> is_argument(example_func, "a")
    True
    >>> is_argument(example_func, "d")
    False
    >>> is_argument(example_func, "c")
    True

    Notes
    -----
    This function checks parameter names, not parameter types or positions.
    It will return `True` for any parameter with the matching name, regardless
    of whether it is a positional argument, keyword-only argument, or has
    a default value.
    """
    return arg_name in set(inspect.signature(__callable).parameters.keys())


class dummy_tqdm(Iterable[T]):
    """
    A dummy class that mimics the behavior of 'tqdm' for testing or placeholder purposes.

    This class allows you to use a tqdm-like interface in cases where the
    progress bar functionality is not needed or when testing code without
    depending on the actual `tqdm` library.

    Parameters
    ----------
    __iterable : Iterable[T]
        An iterable object that will be wrapped and returned by the class.

    Methods
    -------
    __iter__() -> Iterator[T]
        Returns an iterator for the provided iterable.
    __getattr__(name: str) -> Callable[..., None]
        Returns a no-operation function for unsupported attributes.
    """

    def __init__(self, __iterable: "Iterable[T]", *args, **kwargs) -> None:
        self.__iterable = __iterable

    def __iter__(self) -> "Iterator[T]":
        """
        Return an iterator for the given iterable.

        Returns
        -------
        Iterator[T]
            An iterator for the provided iterable object.
        """
        return iter(self.__iterable)

    def __getattr__(self, name: str) -> "Callable[..., None]":
        """
        Handle unsupported attribute access by returning a no-op function.

        This method allows the class to simulate the behavior of tqdm by
        returning a no-op function for any attribute that is not defined.

        Parameters
        ----------
        name : str
            The name of the attribute being accessed.

        Returns
        -------
        Callable[..., None]
            A no-op function that does nothing.
        """
        return self.__no_operation

    @staticmethod
    def __no_operation(*args, **kwargs) -> None:
        """
        A no-operation function used as a placeholder.

        This function does nothing and is used as a fallback for unsupported
        method calls or attributes.

        Returns
        -------
        None
        """
        return


def deprecated(
    reason: Optional[str] = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to mark a function as deprecated.

    Parameters
    ----------
    reason : str, optional
        Explanation of why the function is deprecated or what should be used instead.

    Returns
    -------
    Callable
        A decorator that wraps the target function and emits a ``DeprecationWarning``
        upon each call.

    Notes
    -----
    - Preserves the wrapped function's type signature.
    - Emits a ``DeprecationWarning`` every time the function is called.
    - Appends a ``.. deprecated::`` directive to the function's docstring.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        base_message = f"{func.__name__} is deprecated."
        if reason:
            base_message += f" {reason}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(base_message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        # Add deprecation notice to docstring in NumPy style
        original_doc = func.__doc__ or ""
        deprecation_header = f".. deprecated::\n    {reason or ''}\n\n"
        wrapper.__doc__ = deprecation_header + original_doc

        return wrapper

    return decorator
