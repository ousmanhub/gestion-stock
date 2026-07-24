# Plan d'implémentation — Commandes fournisseurs (v2)

**Goal :** Ajouter la gestion des commandes fournisseurs. Un commerçant ou responsable logistique peut enregistrer une commande chez un fournisseur (produit, quantité prévue, prix unitaire prévu, date de livraison estimée). Quand la marchandise arrive, on la réceptionne : cela crée automatiquement un mouvement d'entrée et met à jour la commande.

**Architecture :** Nouvelle table `CommandeFournisseur` liée à `Commercant` et `Produit`. Statuts : `BROUILLON`, `ENVOYEE`, `PARTIELLEMENT_RECUE`, `RECUE`, `ANNULEE`. Endpoint de réception qui crée un `MouvementStock` de type `ENTREE`.

---

## Contexte et contraintes

- Une commande concerne un produit d'un commerçant, un fournisseur (nom, contact), une quantité commandée et un prix unitaire prévu.
- Plusieurs réceptions partielles possibles (cumulative).
- La réception est autorisée tant que `quantite_recue < quantite_commandee`.
- Quand `quantite_recue == quantite_commandee`, statut = `RECUE`.
- Permissions :
  - `commercant`, `responsable_logistique` : créer, modifier, annuler, réceptionner
  - `employe` : lecture seule

---

## Nouveaux fichiers / modifications

- Modifier `src/gestion_stock/models.py` : ajouter `CommandeFournisseur`, `StatutCommandeFournisseur`.
- Créer `src/gestion_stock/routers/commandes_fournisseurs.py`.
- Modifier `src/gestion_stock/main.py` : monter le router.
- Créer `src/gestion_stock/tests/test_commandes_fournisseurs.py`.
- Mettre à jour `README.md`.

---

## Endpoints

- `POST /commercants/{id}/commandes-fournisseurs` : créer
- `GET /commercants/{id}/commandes-fournisseurs` : lister (filtrer par statut, produit)
- `GET /commercants/{id}/commandes-fournisseurs/{commande_id}` : détail
- `PATCH /commercants/{id}/commandes-fournisseurs/{commande_id}` : modifier (brouillon uniquement)
- `POST /commercants/{id}/commandes-fournisseurs/{commande_id}/envoyer` : passer à ENVOYEE
- `POST /commercants/{id}/commandes-fournisseurs/{commande_id}/receptionner` : réceptionner une quantité → crée un mouvement d'entrée
- `POST /commercants/{id}/commandes-fournisseurs/{commande_id}/annuler` : annuler

---

## Validation finale

- `pytest src/gestion_stock/tests -v` OK
- `ruff check src/gestion_stock` OK
- commit + push
