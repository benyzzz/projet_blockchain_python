"""
Utility functions for the blockchain project.

This module contains helper functions such as transaction validation and
timestamp formatting. Centralizing these functions makes them easier to
reuse across different parts of the project.
"""

from __future__ import annotations

from typing import Dict, Any
import datetime as _datetime


def validate_transaction(transaction: Dict[str, Any]) -> None:
    """Validate the structure of a transaction.

    Each transaction is expected to be a dictionary containing at least the
    keys ``sender``, ``recipient`` and ``amount``. Additional fields are
    permitted but must not shadow these reserved keys. The ``amount`` should
    be a positive number (integer or float). If the transaction fails any
    of these checks, a :class:`ValueError` is raised.

    Parameters
    ----------
    transaction : Dict[str, Any]
        The transaction to validate.

    Raises
    ------
    ValueError
        If the transaction is missing required keys or has invalid values.
    """
    required_fields = {"sender", "recipient", "amount"}
    missing = required_fields - transaction.keys()
    if missing:
        raise ValueError(f"Transaction missing required fields: {', '.join(missing)}")
    amount = transaction["amount"]
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Transaction amount must be a positive number")


def format_timestamp(timestamp: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convert a UNIX timestamp to a formatted string.

    Parameters
    ----------
    timestamp : float
        The UNIX timestamp to format.
    fmt : str, optional
        The format string compatible with :func:`datetime.datetime.strftime`.

    Returns
    -------
    str
        A human‑readable representation of the timestamp.
    """
    return _datetime.datetime.fromtimestamp(timestamp).strftime(fmt)