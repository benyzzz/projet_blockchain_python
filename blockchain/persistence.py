"""
Persistence helpers for the blockchain project.

This module provides simple functions to serialize and deserialize a
blockchain to and from JSON on disk. These helpers complement the
methods available on the :class:`~blockchain.blockchain.Blockchain`
class and can be used independently if desired.
"""

from __future__ import annotations

from typing import List, Optional
import json
import os

from .block import Block


def save_chain(chain: List[Block], path: str) -> None:
    """Serialize and save a chain of blocks to disk.

    Parameters
    ----------
    chain : List[Block]
        The blockchain represented as a list of :class:`Block` instances.
    path : str
        Path to the file where the chain should be saved. If the directory
        does not exist, it will be created.
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    data = [block.to_dict() for block in chain]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_chain(path: str) -> Optional[List[Block]]:
    """Load a blockchain from a JSON file.

    Parameters
    ----------
    path : str
        Path to the JSON file containing the serialized blockchain.

    Returns
    -------
    Optional[List[Block]]
        A list of :class:`Block` objects if the file exists and is valid,
        otherwise ``None``. Invalid data will be ignored.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chain = [Block.from_dict(item) for item in data]
        return chain
    except Exception:
        return None