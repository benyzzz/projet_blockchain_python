"""
Interface web pour la blockchain.

Ce module utilise le micro‑framework Flask pour fournir une interface web
simple autour de la classe :class:`blockchain.blockchain.Blockchain`. Les
utilisateurs peuvent visualiser la chaîne, ajouter des transactions, miner
des blocs et valider l’intégrité de la blockchain via un navigateur.

Pour lancer le serveur web :

```
pip install flask
python web_app.py
```

Le serveur écoute par défaut sur http://localhost:5000.
"""

from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from blockchain.blockchain import Blockchain
import os

app = Flask(__name__)
app.secret_key = "change-me"  # clé secrète pour les messages flash

# Chemin de stockage par défaut ; peut être modifié via variable d’environnement
STORAGE_PATH = os.environ.get("BLOCKCHAIN_STORAGE", "blockchain.json")
DIFFICULTY = int(os.environ.get("BLOCKCHAIN_DIFFICULTY", 2))

# Initialisation du blockchain en mode autosave pour conserver l’état entre
# différentes requêtes. Cette instance est utilisée dans toutes les routes.
blockchain = Blockchain(difficulty=DIFFICULTY, autosave=True, storage_path=STORAGE_PATH)


@app.route("/")
def index():
    """Page d’accueil affichant quelques statistiques et liens rapides."""
    labels = [str(b.index) for b in blockchain.chain]
    tx_counts = [len(b.transactions) for b in blockchain.chain]
    return render_template(
        "index.html",
        chain_length=len(blockchain.chain),
        difficulty=blockchain.difficulty,
        labels=labels,
        tx_counts=tx_counts,
    )


@app.route("/chain")
def show_chain():
    """Affiche la liste des blocs avec leurs transactions."""
    table_data = []
    for b in blockchain.chain:
        total = sum(
            float(tx.get("amount", 0))
            for tx in b.transactions
            if isinstance(tx.get("amount"), (int, float))
        )
        table_data.append(
            {
                "index": b.index,
                "timestamp": datetime.fromtimestamp(b.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "tx_count": len(b.transactions),
                "total": total,
            }
        )
    return render_template("chain.html", chain=blockchain.chain, table_data=table_data)


@app.route("/pending")
def show_pending():
    """Affiche les transactions en attente de minage."""
    return render_template(
        "pending.html", pending=blockchain.pending_transactions
    )


@app.route("/transactions/new", methods=["GET", "POST"])
def new_transaction():
    """Formulaire pour ajouter une nouvelle transaction."""
    if request.method == "POST":
        sender = request.form.get("sender")
        recipient = request.form.get("recipient")
        amount = request.form.get("amount")
        metadata = request.form.get("metadata")
        try:
            amount_value = float(amount)
        except (TypeError, ValueError):
            flash("Le montant doit être un nombre.", "danger")
            return redirect(url_for("new_transaction"))
        # Construire la transaction et éventuellement ajouter des métadonnées
        tx = {"sender": sender, "recipient": recipient, "amount": amount_value}
        if metadata:
            tx.update({"metadata": metadata})
        try:
            blockchain.add_transaction(tx)
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("new_transaction"))
        flash("Transaction ajoutée avec succès.", "success")
        return redirect(url_for("show_pending"))
    return render_template("add_transaction.html")


@app.route("/mine")
def mine_block():
    """Mine un nouveau bloc avec toutes les transactions en attente."""
    try:
        block = blockchain.mine_pending_transactions()
        flash(
            f"Bloc miné ! Index : {block.index}, hash : {block.hash}, transactions : {len(block.transactions)}",
            "success",
        )
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("show_chain"))


@app.route("/validate")
def validate_chain():
    """Vérifie l’intégrité de la blockchain et affiche un message."""
    valid = blockchain.is_valid_chain()
    if valid:
        flash("La blockchain est valide.", "success")
    else:
        flash("La blockchain est invalide !", "danger")
    return redirect(url_for("show_chain"))


if __name__ == "__main__":
    # Exécution du serveur Flask en mode debug pour un développement aisé
    app.run(debug=True)