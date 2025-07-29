"""
Blockchain package initialization.

This package contains the core classes and functions needed to build a simple
blockchain. It exposes the :class:`Block` and :class:`Blockchain` classes for
public use. The helper functions for persistence and utilities are also
available through the :mod:`persistence` and :mod:`utils` submodules.

The aim of this project is to provide a clean, educational implementation of
a blockchain in Python that satisfies the requirements laid out in the
provided project specification. The code follows PEP 8 naming conventions,
includes docstrings for all public objects and functions, and is suitable
both for interactive use and for running via a command‑line interface.
"""

from .block import Block  # noqa: F401
from .blockchain import Blockchain  # noqa: F401
from . import persistence  # noqa: F401
from . import utils  # noqa: F401