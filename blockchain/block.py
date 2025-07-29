"""
Definition of the :class:`Block` class used in the blockchain.

A block encapsulates a set of transactions along with metadata such as the
block index, timestamp, hash of the previous block and a nonce used during
proof‑of‑work mining. Each block can compute its own hash based on its
contents to ensure integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import json
import hashlib
import time


@dataclass
class Block:
    """Represents a single block in the blockchain.

    Attributes
    ----------
    index : int
        The position of the block in the blockchain.
    timestamp : float
        UNIX timestamp representing when the block was created. Using a float
        here preserves sub‑second precision. A human readable string can be
        derived if needed.
    transactions : List[Dict[str, Any]]
        A list of transactions included in this block. Each transaction is
        represented as a dictionary with arbitrary keys and values.
    previous_hash : str
        The hash of the previous block in the chain.
    nonce : int
        A number that miners change in order to find a valid hash satisfying
        the proof‑of‑work difficulty.
    hash : str
        The computed SHA‑256 hash of the current block. This field is
        calculated using the :meth:`compute_hash` method and stored after
        mining. It is not used in the hash computation itself.
    """

    index: int
    timestamp: float = field(default_factory=lambda: time.time())
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    previous_hash: str = "0"
    nonce: int = 0
    hash: str = ""

    def compute_hash(self) -> str:
        """Compute the SHA‑256 hash of the block's contents.

        The hash is computed over the block's index, timestamp, list of
        transactions, previous hash and nonce. The resulting hexadecimal
        digest uniquely identifies the block's contents.

        Returns
        -------
        str
            The hexadecimal SHA‑256 digest of the block.
        """
        # Prepare a deterministic representation of the block's state using
        # json.dumps with sorted keys to ensure consistent ordering.
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the block to a dictionary.

        Returns
        -------
        Dict[str, Any]
            A dictionary representation of the block suitable for JSON
            serialization.
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create a :class:`Block` instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            A dictionary representation of a block, typically loaded from
            persistent storage.

        Returns
        -------
        Block
            A new :class:`Block` populated with the values from *data*.
        """
        block = cls(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=data.get("transactions", []),
            previous_hash=data.get("previous_hash", "0"),
            nonce=data.get("nonce", 0),
        )
        block.hash = data.get("hash", "")
        return block