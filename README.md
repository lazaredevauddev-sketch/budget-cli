# budget-cli 💸

Un petit gestionnaire de dépenses en ligne de commande, écrit en Python.
Les dépenses sont enregistrées localement dans un fichier `depenses.json`.

## Fonctionnalités

- Ajouter une dépense (montant, catégorie, description, date)
- Lister les dépenses, avec filtre par mois ou par catégorie
- Afficher les totaux par catégorie avec un mini graphique en barres
- Supprimer une dépense
- Exporter les dépenses en CSV
- Générer un camembert des dépenses (optionnel, avec `matplotlib`)

## Prérequis

- Python 3.8 ou plus
- (Optionnel) `matplotlib` pour la commande `graphique` :

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Ajouter une dépense
python budget.py ajouter 12.50 courses "Carrefour"
python budget.py ajouter 45 transport "Pass Navigo" --date 2026-10-01

# Lister
python budget.py lister
python budget.py lister --mois 2026-10
python budget.py lister --categorie courses

# Statistiques
python budget.py stats
python budget.py stats --mois 2026-10

# Supprimer la dépense n°3
python budget.py supprimer 3

# Exporter en CSV
python budget.py exporter
python budget.py exporter octobre.csv --mois 2026-10

# Camembert
python budget.py graphique
```

## Exemple de sortie

```
Statistiques (tout)
---------------------------------------------
transport        45.00 €   62.1 %  ████████████
courses          27.50 €   37.9 %  ███████
---------------------------------------------
Total            72.50 €
Nombre de dépenses : 3
```

## Idées d'amélioration

- [ ] Définir un budget mensuel et afficher une alerte en cas de dépassement
- [x] Exporter les dépenses en CSV
- [ ] Ajouter des revenus en plus des dépenses
- [ ] Écrire des tests unitaires
