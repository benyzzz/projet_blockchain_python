# Projet Final – Blockchain en Python

Ce dépôt contient une implémentation complète d’une **blockchain simplifiée** en Python 3 conforme aux exigences du projet final. L’objectif est pédagogique : comprendre les concepts fondamentaux (blocs, hachage, preuve de travail, transactions, validation, résolution des conflits) tout en respectant les bonnes pratiques de développement (PEP 8, modularisation, tests unitaires).

## Fonctionnalités

- Création automatique d’un **bloc de genèse**.
- **Ajout de transactions** avec validation de la structure (expéditeur, destinataire, montant positif).
- **Preuve de travail** configurable via un niveau de difficulté (nombre de zéros initiaux dans le hachage).
- **Minage** d’un nouveau bloc contenant toutes les transactions en attente.
- **Hachage cryptographique** des blocs avec SHA‑256.
- **Validation** de la chaîne (continuité des index, cohérence des hachages, respect du niveau de difficulté).
- **Résolution de conflits** : remplacement par la chaîne la plus longue parmi des chaînes voisines valides.
- **Persistance** sur disque au format JSON (sauvegarde et chargement automatiques).
- **Interface en ligne de commande (CLI)** pour interagir avec la blockchain sans codage.
- **Interface web (Flask)** permettant de visualiser la chaîne, d’ajouter des transactions via un formulaire, de miner un bloc et de valider la chaîne depuis un navigateur.
- **Tests unitaires** pour valider le comportement et éviter les régressions.

## Arborescence du projet

```
projet_blockchain/
├── blockchain/            # Package principal contenant la logique
│   ├── __init__.py
│   ├── block.py           # Classe Block (index, timestamp, transactions…)
│   ├── blockchain.py      # Classe Blockchain (gestion des blocs, minage…)
│   ├── utils.py           # Fonctions utilitaires (validation des transactions…)
│   └── persistence.py     # Fonctions de sauvegarde/chargement JSON
├── tests/
│   └── test_blockchain.py # Suite de tests unitaires utilisant unittest
├── cli.py                 # Interface en ligne de commande pour manipuler la blockchain
└── README.md              # Ce fichier d’explications
```

## Pré‑requis et installation

- **Python 3.8 ou supérieur** est requis (recommandé : Python 3.10+). Vous pouvez vérifier votre version :

  ```bash
  python --version
  ```

### Créer un environnement virtuel (optionnel mais conseillé)

Pour éviter les conflits de dépendances entre projets, il est recommandé d’utiliser un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate  # sous Linux/macOS
.\.venv\Scripts\activate  # sous Windows
```

Pour utiliser la **CLI**, aucune dépendance externe n’est nécessaire : le projet repose uniquement sur la bibliothèque standard de Python.  
Pour l’**interface web**, installez simplement Flask :

```bash
pip install flask
```

Vous pouvez créer un fichier `requirements.txt` listant `flask` si vous souhaitez gérer les dépendances plus facilement.

## Utilisation de la CLI

Le fichier `cli.py` propose plusieurs commandes. Toutes acceptent les options `--storage` (chemin vers le fichier de sauvegarde JSON, par défaut `blockchain.json` dans le répertoire courant) et `--difficulty` (nombre de zéros imposés au début du hachage pour la preuve de travail).

### Ajouter une transaction

```bash
python cli.py add-transaction --sender Alice --recipient Bob --amount 10 \
    --metadata '{"message": "Paiement pour un service"}'
```

La transaction est ajoutée à la liste d’attente et sauvegardée. Les champs obligatoires sont `sender`, `recipient` et `amount` (>0). Le champ `--metadata` est optionnel et doit être une chaîne JSON valide pour ajouter des métadonnées supplémentaires.

### Miner un nouveau bloc

```bash
python cli.py mine
```

Cette commande crée un bloc avec toutes les transactions en attente, effectue la preuve de travail et ajoute le bloc à la chaîne. Les transactions en attente sont alors effacées. Les informations du bloc (index, hachage, nombre de transactions) sont affichées.

### Afficher la blockchain

```bash
python cli.py view
```

Affiche chaque bloc de la chaîne : index, timestamp, hachage, nonce et liste des transactions.

### Valider la blockchain

```bash
python cli.py validate
```

Contrôle l’intégrité de la chaîne (hachages, continuité, difficulté). En cas d’incohérence, un message d’erreur est renvoyé.

### Afficher les transactions en attente

```bash
python cli.py pending
```

Affiche la liste des transactions non encore minées.

### Résoudre les conflits

```bash
python cli.py resolve --file voisins.json
```

Le fichier passé en argument doit contenir un tableau JSON, chaque élément étant une chaîne candidate représentée comme un tableau de blocs (dictionnaires). La méthode sélectionne la chaîne la plus longue et valide (principe de « longest chain ») et remplace la chaîne locale si nécessaire.

## Utiliser l’interface web

L’interface web vous permet de manipuler la blockchain graphiquement. Après avoir installé Flask (voir section *Pré‑requis et installation*), lancez :

```bash
python web_app.py
```

Le serveur écoute par défaut sur [http://localhost:5000](http://localhost:5000). Vous pourrez :

- Consulter la liste des blocs via la page « Chaîne ».
- Ajouter des transactions grâce à un formulaire accessible depuis « Ajouter une transaction ».
- Miner un bloc en un clic (bouton « Miner un bloc » dans la barre de navigation).
- Vérifier l’intégrité de la chaîne via l’option « Valider ».

Les messages de succès ou d’erreur s’affichent sous forme d’alertes en haut des pages.

## Exécuter les tests unitaires

Pour vous assurer du bon fonctionnement de votre code et gagner des points au barème « Tests unitaires et bonnes pratiques », lancez :

```bash
python -m unittest -v tests/test_blockchain.py
```

Les tests vérifient :

1. Que le bloc de genèse est correctement créé.
2. Que l’ajout de transactions et le minage fonctionnent et effacent la liste d’attente.
3. Que toute tentative de modification (tampering) invalide la chaîne.
4. Que la résolution de conflits remplace bien la chaîne par une version plus longue et valide.

## Conseils pour maximiser votre note

- **Soignez la clarté du code** : nommage explicite, commentaires pertinents, docstrings pour les fonctions et classes. Le correcteur automatique vérifie notamment les conventions de nommage (PEP 8).
- **Modularisez** : le projet est divisé en modules logiques (blocs, blockchain, utilitaires, persistance, CLI) facilitant la lecture et la maintenance.
- **Testez votre code** : fournissez des tests unitaires complets (`tests/`) et exécutez‑les régulièrement. Un projet bien testé montrera votre maîtrise et réduira les risques de bug.
- **Respectez la consigne** : n’utilisez pas de librairies externes si elles ne sont pas nécessaires. Ici tout est réalisable avec la bibliothèque standard de Python.
- **Persistance** : assurez‑vous que votre programme sauvegarde automatiquement la chaîne (`blockchain.json`) après chaque opération de minage ou d’ajout de transaction. Cela garantit que vos données ne sont pas perdues entre deux exécutions.

En suivant ces recommandations et en vous appuyant sur cette implémentation, vous êtes en bonne voie pour obtenir la meilleure note possible pour ce projet.