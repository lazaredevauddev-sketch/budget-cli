#!/usr/bin/env python3
"""
budget-cli : un petit gestionnaire de dépenses en ligne de commande.

Exemples :
    python budget.py ajouter 12.50 courses "Carrefour"
    python budget.py lister --mois 2026-10
    python budget.py stats
    python budget.py supprimer 3
    python budget.py graphique
    python budget.py exporter depenses.csv
"""

import argparse
import csv
import json
import os
import sys
from datetime import date

FICHIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "depenses.json")


# ---------- Stockage ----------

def charger():
    """Lit les dépenses depuis le fichier JSON (liste vide si absent)."""
    if not os.path.exists(FICHIER):
        return []
    with open(FICHIER, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Erreur : le fichier depenses.json est corrompu.")
            sys.exit(1)


def sauvegarder(depenses):
    """Écrit la liste des dépenses dans le fichier JSON."""
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(depenses, f, ensure_ascii=False, indent=2)


def prochain_id(depenses):
    return max((d["id"] for d in depenses), default=0) + 1


def filtrer(depenses, mois=None, categorie=None):
    """Garde les dépenses d'un mois (AAAA-MM) et/ou d'une catégorie."""
    resultat = depenses
    if mois:
        resultat = [d for d in resultat if d["date"].startswith(mois)]
    if categorie:
        resultat = [d for d in resultat if d["categorie"] == categorie.lower()]
    return resultat


# ---------- Commandes ----------

def cmd_ajouter(args):
    if args.montant <= 0:
        print("Erreur : le montant doit être positif.")
        return
    depenses = charger()
    depense = {
        "id": prochain_id(depenses),
        "date": args.date or date.today().isoformat(),
        "montant": round(args.montant, 2),
        "categorie": args.categorie.lower(),
        "description": args.description,
    }
    depenses.append(depense)
    sauvegarder(depenses)
    print(f"Dépense n°{depense['id']} ajoutée : {depense['montant']:.2f} € "
          f"({depense['categorie']}) le {depense['date']}")


def cmd_lister(args):
    depenses = filtrer(charger(), args.mois, args.categorie)
    if not depenses:
        print("Aucune dépense trouvée.")
        return
    print(f"{'ID':>4}  {'Date':<10}  {'Montant':>10}  {'Catégorie':<12}  Description")
    print("-" * 60)
    for d in sorted(depenses, key=lambda d: d["date"]):
        print(f"{d['id']:>4}  {d['date']:<10}  {d['montant']:>8.2f} €  "
              f"{d['categorie']:<12}  {d['description']}")
    total = sum(d["montant"] for d in depenses)
    print("-" * 60)
    print(f"{'Total':<16}  {total:>8.2f} €")


def totaux_par_categorie(depenses):
    totaux = {}
    for d in depenses:
        totaux[d["categorie"]] = totaux.get(d["categorie"], 0) + d["montant"]
    return dict(sorted(totaux.items(), key=lambda x: x[1], reverse=True))


def cmd_stats(args):
    depenses = filtrer(charger(), args.mois)
    if not depenses:
        print("Aucune dépense trouvée.")
        return
    totaux = totaux_par_categorie(depenses)
    total = sum(totaux.values())
    titre = f"Statistiques {args.mois}" if args.mois else "Statistiques (tout)"
    print(titre)
    print("-" * 45)
    for cat, montant in totaux.items():
        part = montant / total * 100
        barre = "█" * int(part / 5)
        print(f"{cat:<12} {montant:>9.2f} €  {part:5.1f} %  {barre}")
    print("-" * 45)
    print(f"{'Total':<12} {total:>9.2f} €")
    print(f"Nombre de dépenses : {len(depenses)}")


def cmd_supprimer(args):
    depenses = charger()
    restantes = [d for d in depenses if d["id"] != args.id]
    if len(restantes) == len(depenses):
        print(f"Aucune dépense avec l'ID {args.id}.")
        return
    sauvegarder(restantes)
    print(f"Dépense n°{args.id} supprimée.")


def cmd_graphique(args):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib n'est pas installé. Lance : pip install matplotlib")
        return
    depenses = filtrer(charger(), args.mois)
    if not depenses:
        print("Aucune dépense trouvée.")
        return
    totaux = totaux_par_categorie(depenses)
    plt.pie(totaux.values(), labels=totaux.keys(), autopct="%1.1f%%")
    plt.title(f"Dépenses par catégorie {args.mois or ''}".strip())
    plt.axis("equal")
    plt.show()


def cmd_exporter(args):
    depenses = filtrer(charger(), args.mois, args.categorie)
    if not depenses:
        print("Aucune dépense à exporter.")
        return
    with open(args.fichier, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "montant", "categorie", "description"])
        writer.writeheader()
        writer.writerows(sorted(depenses, key=lambda d: d["date"]))
    print(f"{len(depenses)} dépense(s) exportée(s) dans {args.fichier}")


# ---------- Interface ----------

def main():
    parser = argparse.ArgumentParser(description="Gestionnaire de dépenses en ligne de commande")
    sous = parser.add_subparsers(dest="commande", required=True)

    p = sous.add_parser("ajouter", help="Ajouter une dépense")
    p.add_argument("montant", type=float, help="Montant en euros (ex : 12.50)")
    p.add_argument("categorie", help="Catégorie (ex : courses, transport)")
    p.add_argument("description", nargs="?", default="", help="Description facultative")
    p.add_argument("--date", help="Date AAAA-MM-JJ (par défaut : aujourd'hui)")
    p.set_defaults(func=cmd_ajouter)

    p = sous.add_parser("lister", help="Lister les dépenses")
    p.add_argument("--mois", help="Filtrer par mois, format AAAA-MM")
    p.add_argument("--categorie", help="Filtrer par catégorie")
    p.set_defaults(func=cmd_lister)

    p = sous.add_parser("stats", help="Totaux par catégorie")
    p.add_argument("--mois", help="Filtrer par mois, format AAAA-MM")
    p.set_defaults(func=cmd_stats)

    p = sous.add_parser("supprimer", help="Supprimer une dépense par son ID")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_supprimer)

    p = sous.add_parser("graphique", help="Camembert des dépenses (nécessite matplotlib)")
    p.add_argument("--mois", help="Filtrer par mois, format AAAA-MM")
    p.set_defaults(func=cmd_graphique)

    p = sous.add_parser("exporter", help="Exporter les dépenses en CSV")
    p.add_argument("fichier", nargs="?", default="depenses.csv", help="Nom du fichier CSV")
    p.add_argument("--mois", help="Filtrer par mois, format AAAA-MM")
    p.add_argument("--categorie", help="Filtrer par catégorie")
    p.set_defaults(func=cmd_exporter)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
