"""
Core blockchain implementation.

This module defines the :class:`Blockchain` class, which manages a chain of
blocks, handles transactions, performs proof‑of‑work mining, validates
integrity and supports conflict resolution. The implementation is kept
simple and self‑contained, making it ideal for educational purposes or
small‑scale applications.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import time
import json
import os

from .block import Block
from . import utils
from . import persistence


class Blockchain:
    """A simple, secure blockchain implementation.

    Parameters
    ----------
    difficulty : int, optional
        The proof‑of‑work difficulty expressed as the number of leading zeros
        required in the block's hash. A higher difficulty increases the
        computational work needed to mine a block. Defaults to 2.
    autosave : bool, optional
        If set to ``True``, the blockchain will automatically persist itself
        to disk after each mined block. Defaults to ``True``.
    storage_path : str, optional
        Path to the JSON file used for persisting the blockchain. If not
        provided, a default filename ``blockchain.json`` will be created in
        the current working directory.

    Notes
    -----
    When instantiated, the blockchain attempts to load an existing chain
    from the given *storage_path*. If no file exists or the contents are
    invalid, a new chain is initialized with a genesis block.
    """

    def __init__(self, difficulty: int = 2, autosave: bool = True, storage_path: Optional[str] = None) -> None:
        self.difficulty = difficulty
        self.autosave = autosave
        self.storage_path = storage_path or os.path.join(os.getcwd(), "blockchain.json")
        # In‑memory list of blocks comprising the chain
        self.chain: List[Block] = []
        # List of pending transactions awaiting inclusion in the next block
        self.pending_transactions: List[Dict[str, Any]] = []
        # Attempt to load an existing chain; if none exists, create genesis
        if not self.load_chain():
            self.create_genesis_block()

    # ----------------------------------------------------------------------
    # Block and transaction management
    # ----------------------------------------------------------------------
    def create_genesis_block(self) -> Block:
        """Create the first block of the blockchain (genesis block).

        The genesis block has index zero, no previous hash and an empty list
        of transactions. Its nonce is determined via proof of work to meet
        the configured difficulty. The resulting block is appended to the
        chain and persisted if autosave is enabled.

        Returns
        -------
        Block
            The genesis block.
        """
        genesis = Block(index=0, transactions=[], previous_hash="0")
        genesis = self.proof_of_work(genesis)
        self.chain.append(genesis)
        if self.autosave:
            self.save_chain()
        return genesis

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Add a new transaction to the list of pending transactions.

        Transactions are validated using :func:`utils.validate_transaction` to
        ensure they conform to an expected schema. Invalid transactions will
        raise a :class:`ValueError`.

        Parameters
        ----------
        transaction : Dict[str, Any]
            A dictionary representing a transaction. At minimum it should
            contain the keys ``sender``, ``recipient`` and ``amount``, but
            additional metadata can also be included.

        Raises
        ------
        ValueError
            If the transaction fails validation.
        """
        utils.validate_transaction(transaction)
        self.pending_transactions.append(transaction)
        # Persist immediately when autosave is enabled to avoid losing
        # pending transactions between CLI invocations. Minage et
        # résolution de conflits réaliseront également une persistance mais
        # l’ajout de transaction est le seul endroit où la liste d’attente
        # est modifiée sans créer un bloc.
        if self.autosave:
            self.save_chain()

    def mine_pending_transactions(self) -> Block:
        """Mine a new block containing all pending transactions.

        This function creates a new block using the current pending
        transactions, performs proof‑of‑work to find a valid nonce and hash,
        resets the pending transaction list and appends the block to the
        chain. If autosave is enabled, the chain is persisted to disk.

        Returns
        -------
        Block
            The newly mined block.

        Raises
        ------
        ValueError
            If there are no transactions to mine.
        """
        if not self.pending_transactions:
            raise ValueError("No transactions to mine")
        index = len(self.chain)
        previous_hash = self.chain[-1].hash
        # Copy pending transactions to avoid mutation during mining
        transactions_copy = list(self.pending_transactions)
        block = Block(index=index, transactions=transactions_copy, previous_hash=previous_hash)
        # Perform proof of work
        block = self.proof_of_work(block)
        # Append to chain and reset pending transactions
        self.chain.append(block)
        self.pending_transactions = []
        if self.autosave:
            self.save_chain()
        return block

    # ----------------------------------------------------------------------
    # Proof of work and validation
    # ----------------------------------------------------------------------
    def proof_of_work(self, block: Block) -> Block:
        """Perform the proof‑of‑work algorithm to mine a block.

        The algorithm repeatedly increments the block's nonce until its
        computed hash has a certain number of leading zeros equal to
        :attr:`difficulty`. Once a valid hash is found, it is assigned to
        ``block.hash`` and the block is returned.

        Parameters
        ----------
        block : Block
            The block to be mined. Its nonce and hash fields will be
            modified by this function.

        Returns
        -------
        Block
            The mined block with a valid nonce and hash.
        """
        prefix = "0" * self.difficulty
        nonce = 0
        while True:
            block.nonce = nonce
            block_hash = block.compute_hash()
            if block_hash.startswith(prefix):
                block.hash = block_hash
                return block
            nonce += 1

    def is_valid_chain(self, chain: Optional[List[Block]] = None) -> bool:
        """Check whether the blockchain (or a supplied chain) is valid.

        Validation involves verifying that each block's stored hash is
        correct, that its hash satisfies the difficulty requirement, and
        that the ``previous_hash`` of each block matches the actual hash of
        the preceding block.

        Parameters
        ----------
        chain : List[Block], optional
            A chain to validate. If not provided, the in‑memory chain of
            this instance is checked.

        Returns
        -------
        bool
            ``True`` if the chain is valid, ``False`` otherwise.
        """
        chain = chain or self.chain
        if not chain:
            return False
        prefix = "0" * self.difficulty
        # Validate genesis block separately
        genesis = chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0":
            return False
        expected_genesis_hash = genesis.compute_hash()
        if not genesis.hash or not genesis.hash.startswith(prefix) or genesis.hash != expected_genesis_hash:
            return False
        # Validate subsequent blocks
        for i in range(1, len(chain)):
            current = chain[i]
            prev = chain[i - 1]
            # Check index continuity
            if current.index != i:
                return False
            # Validate hash chain linkage
            if current.previous_hash != prev.hash:
                return False
            # Compute and compare the hash
            computed_hash = current.compute_hash()
            if not computed_hash.startswith(prefix) or current.hash != computed_hash:
                return False
        return True

    # ----------------------------------------------------------------------
    # Conflict resolution
    # ----------------------------------------------------------------------
    def resolve_conflicts(self, neighbour_chains: List[List[Dict[str, Any]]]) -> bool:
        """Resolve conflicts by adopting the longest valid chain from neighbours.

        In a distributed setting, different nodes may have divergent versions
        of the blockchain. To achieve consensus, the node will replace its
        chain with the longest valid chain it can find among its neighbours.

        Parameters
        ----------
        neighbour_chains : List[List[Dict[str, Any]]]
            A list of chains received from neighbouring nodes, each chain
            represented as a list of block dictionaries (as produced by
            :meth:`Block.to_dict`).

        Returns
        -------
        bool
            ``True`` if the chain was replaced with a longer valid chain,
            ``False`` otherwise.
        """
        new_chain: Optional[List[Block]] = None
        max_length = len(self.chain)
        for raw_chain in neighbour_chains:
            try:
                chain_blocks = [Block.from_dict(b) for b in raw_chain]
            except Exception:
                # Skip invalid data
                continue
            if len(chain_blocks) > max_length and self.is_valid_chain(chain_blocks):
                max_length = len(chain_blocks)
                new_chain = chain_blocks
        if new_chain:
            self.chain = new_chain
            if self.autosave:
                self.save_chain()
            return True
        return False

    # ----------------------------------------------------------------------
    # Persistence
    # ----------------------------------------------------------------------
    def save_chain(self) -> None:
        """Persist the current chain and pending transactions to disk.

        The blockchain state is stored as a dictionary with two keys:

        - ``chain`` : liste des blocs sérialisés (via :meth:`Block.to_dict`)
        - ``pending_transactions`` : liste des transactions en attente

        Cette structure permet de restaurer correctement les transactions en
        attente lors du prochain chargement, évitant ainsi de les perdre entre
        deux exécutions de la CLI. Si le répertoire du fichier n’existe pas,
        il est créé automatiquement. Les erreurs d’écriture lèvent un
        ``OSError``.
        """
        directory = os.path.dirname(self.storage_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        data = {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": list(self.pending_transactions),
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_chain(self) -> bool:
        """Load a blockchain and pending transactions from disk.

        Le fichier JSON peut être soit :

        1. **Ancien format** : une liste de blocs sérialisés. Dans ce cas les
           transactions en attente sont initialisées à une liste vide.
        2. **Nouveau format** : un dictionnaire avec les clés ``chain`` et
           ``pending_transactions``. La chaîne est validée avant d’être
           acceptée; les transactions en attente sont restaurées sans
           validation supplémentaire (leur format sera vérifié lors du minage).

        Returns
        -------
        bool
            ``True`` if a valid chain was loaded, ``False`` otherwise.
        """
        if not os.path.exists(self.storage_path):
            return False
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Déterminer le format du fichier
            if isinstance(data, list):
                # Ancien format : liste de blocs
                loaded_chain = [Block.from_dict(block) for block in data]
                pending = []
            elif isinstance(data, dict):
                loaded_chain = [Block.from_dict(block) for block in data.get("chain", [])]
                pending = data.get("pending_transactions", [])
                if not isinstance(pending, list):
                    pending = []
            else:
                return False
        except Exception:
            return False
        # Validate loaded chain before accepting it
        if self.is_valid_chain(loaded_chain):
            self.chain = loaded_chain
            self.pending_transactions = pending
            return True
        return False