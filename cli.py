"""
Command‑line interface for the blockchain project.

Running this script allows you to interact with the blockchain via simple
commands. You can add transactions, mine new blocks, view the chain,
validate integrity, view pending transactions, and perform conflict
resolution. The CLI uses Python's built‑in :mod:`argparse` module for
command parsing and prints informative messages to the console.

Example usage::

    python cli.py add-transaction --sender Alice --recipient Bob --amount 5
    python cli.py mine
    python cli.py view
    python cli.py validate
    python cli.py pending
    python cli.py resolve --file neighbours.json

The blockchain data is stored in ``blockchain.json`` in the current working
directory by default. You can override this using the ``--storage`` option
on any command.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from blockchain.blockchain import Blockchain


def create_parser() -> argparse.ArgumentParser:
    """Create the top‑level argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Interact with a simple Python blockchain."
    )
    parser.add_argument(
        "--storage",
        default="blockchain.json",
        help="Path to the blockchain storage file (default: blockchain.json)",
    )
    parser.add_argument(
        "--difficulty",
        type=int,
        default=2,
        help="Proof‑of‑work difficulty (number of leading zeros)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-transaction command
    tx_parser = subparsers.add_parser(
        "add-transaction", help="Add a new transaction to the pending list"
    )
    tx_parser.add_argument("--sender", required=True, help="Sender identifier")
    tx_parser.add_argument(
        "--recipient", required=True, help="Recipient identifier"
    )
    tx_parser.add_argument(
        "--amount", required=True, type=float, help="Amount to transfer"
    )
    tx_parser.add_argument(
        "--metadata",
        help="Optional JSON string with additional transaction data",
    )

    # mine command
    mine_parser = subparsers.add_parser(
        "mine", help="Mine a new block containing all pending transactions"
    )

    # view command
    view_parser = subparsers.add_parser(
        "view", help="Display the full blockchain"
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate the integrity of the blockchain"
    )

    # pending command
    pending_parser = subparsers.add_parser(
        "pending", help="Show pending transactions awaiting mining"
    )

    # resolve command
    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve conflicts using neighbour chains from a JSON file",
    )
    resolve_parser.add_argument(
        "--file",
        required=True,
        help="Path to a JSON file containing a list of neighbour chains",
    )

    return parser


def main(args: List[str]) -> None:
    """Entry point for the blockchain CLI.

    Parameters
    ----------
    args : List[str]
        The command‑line arguments (typically ``sys.argv[1:]``).
    """
    parser = create_parser()
    ns = parser.parse_args(args)
    # Initialize the blockchain. We disable autosave during CLI operations
    # except when mining or resolving conflicts to avoid redundant writes.
    blockchain = Blockchain(
        difficulty=ns.difficulty,
        autosave=True,
        storage_path=ns.storage,
    )

    if ns.command == "add-transaction":
        metadata: Dict[str, Any] = {}
        if ns.metadata:
            try:
                metadata = json.loads(ns.metadata)
            except json.JSONDecodeError:
                print("Error: metadata must be valid JSON", file=sys.stderr)
                sys.exit(1)
        tx = {
            "sender": ns.sender,
            "recipient": ns.recipient,
            "amount": ns.amount,
            **metadata,
        }
        try:
            blockchain.add_transaction(tx)
            print("Transaction added successfully.")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif ns.command == "mine":
        try:
            block = blockchain.mine_pending_transactions()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(
            f"Block mined! Index: {block.index}, Hash: {block.hash}, Transactions: {len(block.transactions)}"
        )

    elif ns.command == "view":
        for block in blockchain.chain:
            print(f"Block {block.index}:")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Previous Hash: {block.previous_hash}")
            print(f"  Hash: {block.hash}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Transactions ({len(block.transactions)}):")
            for tx in block.transactions:
                print(f"    {tx}")
            print("")

    elif ns.command == "validate":
        is_valid = blockchain.is_valid_chain()
        if is_valid:
            print("Blockchain is valid.")
        else:
            print("Blockchain is INVALID!", file=sys.stderr)
            sys.exit(1)

    elif ns.command == "pending":
        if not blockchain.pending_transactions:
            print("No pending transactions.")
        else:
            print(f"Pending transactions ({len(blockchain.pending_transactions)}):")
            for tx in blockchain.pending_transactions:
                print(f"  {tx}")

    elif ns.command == "resolve":
        try:
            with open(ns.file, "r", encoding="utf-8") as f:
                neighbour_chains_data = json.load(f)
            if not isinstance(neighbour_chains_data, list):
                raise ValueError
        except Exception:
            print("Error: failed to load neighbour chains file", file=sys.stderr)
            sys.exit(1)
        replaced = blockchain.resolve_conflicts(neighbour_chains_data)
        if replaced:
            blockchain.save_chain()
            print("Chain was replaced with a longer valid chain.")
        else:
            print("Current chain is authoritative; no replacement occurred.")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])