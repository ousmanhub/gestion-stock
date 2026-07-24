# Plan d'implémentation — Réservations de stock (v2)

> **Pour Hermes :** Utiliser `subagent-driven-development` pour implémenter ce plan tâche par tâche après validation du user.

**Goal :** Ajouter une couche de réservations de stock. Un employé ou responsable peut bloquer une quantité de produits dans un entrepôt pour un client / dossier / commande. Cette quantité n'est pas encore sortie physiquement, mais elle ne doit plus être disponible pour d'autres réservations. Les sorties effectives décrémentent la réservation.

**Architecture :** Nouvelle table `Reservation` liée à `Commercant`, `Produit`, `Entrepot`. Statuts : `EN_COURS`, `HONOREE`, `ANNULEE`. Calcul de stock disponible = stock théorique - réservations en cours. Les mouvements de sortie liés à une réservation la passeront en `HONOREE`.

---

## Contexte et contraintes

- Une réservation concerne un produit, un entrepôt, une quantité, un motif (client, dossier, commande).
- La réservation reste en statut `EN_COURS` jusqu'à ce qu'on fasse un mouvement de sortie lié.
- On ne peut réserver plus que le stock disponible (stock théorique - réservations en cours).
- Stock négatif autorisé temporairement, mais la réservation doit être refusée si stock disponible insuffisant.
- Permissions :
  - `commercant`, `responsable_logistique`, `employe` : créer une réservation
  - `commercant`, `responsable_logistique` : annuler une réservation
  - Tous les rôles authentifiés : lire les réservations

---

## Nouveaux fichiers / modifications

- Modifier `src/gestion_stock/models.py` : ajouter `Reservation`, `StatutReservation`, et `reservation_id` optionnel dans `MouvementStock`.
- Créer `src/gestion_stock/routers/reservations.py` : CRUD réservations.
- Modifier `src/gestion_stock/routers/mouvements.py` : accepter un `reservation_id` optionnel, honorer la réservation à la sortie.
- Modifier `src/gestion_stock/services/stock.py` : ajouter `stock_disponible`.
- Modifier `src/gestion_stock/main.py` : monter le router.
- Créer `src/gestion_stock/tests/test_reservations.py`.

---

## Tâches d'implémentation

### Task 1 : Modèle Reservation

**Files :** `src/gestion_stock/models.py`

**Step 1 :** Ajouter enum

```python
class StatutReservation(str, Enum):
    EN_COURS = "en_cours"
    HONOREE = "honoree"
    ANNULEE = "annulee"
```

**Step 2 :** Ajouter modèle

```python
class Reservation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    produit_id: int = Field(foreign_key="produit.id", index=True)
    entrepot_id: int = Field(foreign_key="entrepot.id", index=True)
    quantite: Decimal = Field(max_digits=12, decimal_places=2)
    quantite_honoree: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    statut: StatutReservation = StatutReservation.EN_COURS
    reference_client: str | None = None
    reference_dossier: str | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 3 :** Ajouter `reservation_id` optionnel dans `MouvementStock`

```python
reservation_id: int | None = Field(default=None, foreign_key="reservation.id", index=True)
```

---

### Task 2 : Stock disponible

**Files :** `src/gestion_stock/services/stock.py`

```python
def stock_disponible(session: Session, produit_id: int, entrepot_id: int) -> Decimal:
    from gestion_stock.models import Reservation, StatutReservation
    theorique = stock_produit_entrepot(session, produit_id, entrepot_id)
    reserve = session.exec(
        select(func.coalesce(func.sum(Reservation.quantite - Reservation.quantite_honoree), Decimal("0.00")))
        .where(
            Reservation.produit_id == produit_id,
            Reservation.entrepot_id == entrepot_id,
            Reservation.statut == StatutReservation.EN_COURS,
        )
    ).one()
    return theorique - reserve
```

---

### Task 3 : Router réservations

**Files :** `src/gestion_stock/routers/reservations.py`

- `POST /commercants/{id}/reservations` : créer une réservation. Vérifier stock disponible.
- `GET /commercants/{id}/reservations` : lister.
- `GET /commercants/{id}/reservations/{reservation_id}` : détail.
- `POST /commercants/{id}/reservations/{reservation_id}/annuler` : annuler.

---

### Task 4 : Lier mouvements et réservations

**Files :** `src/gestion_stock/routers/mouvements.py`

- Ajouter `reservation_id: int | None` dans `MouvementCreate`.
- Si `type_mouvement == SORTIE` et `reservation_id` fourni :
  - vérifier que la réservation existe, appartient au tenant, est `EN_COURS`
  - la quantité sortie ne doit pas dépasser la quantité restante
  - incrémenter `quantite_honoree`
  - si `quantite_honoree == quantite` → statut `HONOREE`

---

### Task 5 : Tests

**Files :** `src/gestion_stock/tests/test_reservations.py`

- Créer une réservation
- Refuser si stock insuffisant
- Vérifier stock disponible après réservation
- Honorer la réservation via un mouvement de sortie
- Annuler une réservation

---

### Task 6 : Validation

- `pytest src/gestion_stock/tests -v` OK
- `ruff check src/gestion_stock` OK
- commit + push
