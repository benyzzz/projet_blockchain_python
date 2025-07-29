"""
Unit tests for the blockchain project.

These tests exercise the core functionality of the blockchain implementation:
creation of the genesis block, transaction addition, block mining, chain
validation and conflict resolution. Running the tests ensures that code
changes do not break existing behaviour.
"""

from __future__ import annotations

import os
import json
import unittest
from typing import List

# Add project root to sys.path to allow relative imports when running tests
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blockchain.blockchain import Blockchain  # type: ignore
from blockchain.block import Block  # type: ignore


class BlockchainTestCase(unittest.TestCase):
    """Test suite for the :class:`Blockchain` class."""

    def setUp(self) -> None:
        # Use a temporary storage path to avoid interfering with real data
        self.temp_file = "test_chain.json"
        # Ensure no residue from previous runs
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.bc = Blockchain(difficulty=2, autosave=False, storage_path=self.temp_file)

    def tearDown(self) -> None:
        # Clean up the temporary storage file
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_genesis_block_created(self) -> None:
        """Ensure the genesis block is created on initialization."""
        self.assertEqual(len(self.bc.chain), 1)
        genesis = self.bc.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        # Hash should satisfy difficulty
        self.assertTrue(genesis.hash.startswith("0" * self.bc.difficulty))
        self.assertEqual(genesis.hash, genesis.compute_hash())

    def test_add_transaction_and_mine(self) -> None:
        """Test adding a transaction and mining a new block."""
        tx = {"sender": "Alice", "recipient": "Bob", "amount": 10}
        self.bc.add_transaction(tx)
        self.assertEqual(len(self.bc.pending_transactions), 1)
        block = self.bc.mine_pending_transactions()
        # After mining, pending transactions should be cleared
        self.assertEqual(len(self.bc.pending_transactions), 0)
        # The new block should contain the transaction
        self.assertIn(tx, block.transactions)
        # Chain length should be 2 (genesis + new block)
        self.assertEqual(len(self.bc.chain), 2)
        # Validate chain
        self.assertTrue(self.bc.is_valid_chain())

    def test_validation_detects_tampering(self) -> None:
        """Tampering with a block should invalidate the chain."""
        # Add and mine a transaction
        tx = {"sender": "A", "recipient": "B", "amount": 1}
        self.bc.add_transaction(tx)
        self.bc.mine_pending_transactions()
        # Tamper with the block's transaction amount
        self.bc.chain[1].transactions[0]["amount"] = 999
        # Recompute hash incorrectly (simulate malicious change without mining)
        self.bc.chain[1].hash = self.bc.chain[1].compute_hash()
        self.assertFalse(self.bc.is_valid_chain())

    def test_conflict_resolution(self) -> None:
        """Test the resolve_conflicts method selects the longest valid chain."""
        # Create a neighbour chain longer than current chain
        neighbour_bc = Blockchain(difficulty=2, autosave=False, storage_path="neighbour.json")
        # Add and mine two blocks to make it longer
        for i in range(2):
            neighbour_bc.add_transaction({"sender": "X", "recipient": "Y", "amount": i + 1})
            neighbour_bc.mine_pending_transactions()
        # Provide neighbour chain data as list of dicts
        neighbour_chain_data: List[List[dict]] = [[b.to_dict() for b in neighbour_bc.chain]]
        replaced = self.bc.resolve_conflicts(neighbour_chain_data)
        self.assertTrue(replaced)
        # Our chain should now equal the neighbour's chain
        self.assertEqual(len(self.bc.chain), len(neighbour_bc.chain))
        self.assertTrue(self.bc.is_valid_chain())
        # Clean up neighbour storage file
        if os.path.exists("neighbour.json"):
            os.remove("neighbour.json")


if __name__ == "__main__":
    unittest.main()