# Plan d'implémentation — Module Gestion de Stock / Inventaire (multi-commerçant)

> **Pour Hermes :** Utiliser `subagent-driven-development` pour implémenter ce plan tâche par tâche après validation du user.

**Goal :** Créer un module FastAPI + SQLite autonome et multi-tenant permettant à chaque commerçant (et ses employés / responsables logistiques) de gérer ses propres produits, entrepôts, mouvements de stock, transferts entre entrepôts, et alertes de seuil. Valorisation FIFO. Authentification et réservations/commandes fournisseurs reportées en v2.

**Architecture :** API REST en FastAPI, persistance SQLite via SQLModel, tests avec pytest/TestClient, structure modulaire multi-commerçant dès le MVP.

**Tech Stack :** Python 3.11, FastAPI, SQLModel, Pydantic v2, SQLite, pytest, uvicorn.

---

## Contexte et contraintes

- Un seul dépôt : `/Users/smartech/gestion-stock`
- Module totalement indépendant du module hébergement (aucun lien prévu).
- Multi-tenant dès le MVP : chaque commerçant isole ses données par `commercant_id`.
- Pas d'authentification dans le MVP : les endpoints filtrent par `commercant_id` passé en paramètre ou path. Auth en v2.
- Stock négatif autorisé temporairement : un mouvement de sortie ou un transfert peut laisser le stock négatif, mais il est remonté en alerte.
- Dates de péremption optionnelles sur les mouvements (pas sur les produits).
- Transferts entre entrepôts du même commerçant dans le MVP.
- Réservations et commandes fournisseurs en v2.

---

## Structure du projet

```
/Users/smartech/gestion-stock
├── src/
│   ├── gestion_stock/
│   │   ├── __init__.py
│   │   ├── main.py              # App FastAPI + lifespan
│   │   ├── config.py            # Settings (DATABASE_URL)
│   │   ├── database.py          # Engine + Session + get_session
│   │   ├── models.py            # SQLModel : Commercant, Produit, Entrepot, MouvementStock
│   │   ├── schemas.py           # Pydantic request/response si nécessaire
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── commercants.py   # CRUD commerçants
│   │   │   ├── produits.py      # CRUD produits (par commerçant)
│   │   │   ├── entrepots.py     # CRUD entrepôts (par commerçant)
│   │   │   ├── mouvements.py    # Entrées / sorties / ajustements
│   │   │   ├── transferts.py    # Transferts entre entrepôts
│   │   │   └── alertes.py       # Alertes de stock + valorisation FIFO
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── stock.py         # Calcul stock, valorisation FIFO
│   │   │   └── alertes.py       # Détection alertes
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_commercants.py
│   │       ├── test_produits.py
│   │       ├── test_entrepots.py
│   │       ├── test_mouvements.py
│   │       ├── test_transferts.py
│   │       └── test_alertes.py
├── .env.example
├── pyproject.toml
├── README.md
└── .hermes/plans/2026-07-24_104500-stock-fastapi-plan.md
```

---

## Tâches d'implémentation

### Task 1 : Initialiser le projet et les dépendances

**Objective :** Créer l'arborescence et le fichier de configuration Python minimal.

**Files :**
- Créer : `pyproject.toml`
- Créer : `.env.example`
- Créer : `src/gestion_stock/__init__.py`
- Créer : `src/gestion_stock/config.py`

**Step 1 :** Créer `pyproject.toml`

```toml
[project]
name = "gestion-stock"
version = "0.1.0"
description = "Module multi-commerçant de gestion de stock / inventaire FastAPI + SQLite"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlmodel>=0.0.22",
    "pydantic-settings>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "httpx>=0.27.0",
    "ruff>=0.7.0",
]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["src/gestion_stock/tests"]
```

**Step 2 :** Créer `.env.example`

```
DATABASE_URL=sqlite:///./stock.db
```

**Step 3 :** Créer `src/gestion_stock/__init__.py`

```python
__version__ = "0.1.0"
```

**Step 4 :** Créer `src/gestion_stock/config.py`

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./stock.db"

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 5 :** Vérification

Run : `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
Expected : installation réussie.

**Step 6 :** Commit

```bash
git add pyproject.toml .env.example src/gestion_stock/__init__.py src/gestion_stock/config.py
git commit -m "chore: init multi-tenant stock project with FastAPI + SQLModel"
```

---

### Task 2 : Configurer la base de données SQLModel

**Objective :** Mettre en place l'engine SQLite, la session, et le schéma multi-tenant.

**Files :**
- Créer : `src/gestion_stock/database.py`
- Créer : `src/gestion_stock/models.py`

**Step 1 :** Créer `src/gestion_stock/database.py`

```python
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

from gestion_stock.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    echo=False,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


@contextmanager
def session_scope():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

**Step 2 :** Créer `src/gestion_stock/models.py`

```python
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class TypeMouvement(str, Enum):
    ENTREE = "entree"
    SORTIE = "sortie"
    AJUSTEMENT = "ajustement"
    TRANSFERT_SORTIE = "transfert_sortie"
    TRANSFERT_ENTREE = "transfert_entree"


class Commercant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Produit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    sku: str = Field(index=True)
    libelle: str
    categorie: Optional[str] = None
    unite: str = "unité"
    prix_unitaire: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    stock_minimal: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        unique_together = [["commercant_id", "sku"]]


class Entrepot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    nom: str
    adresse: Optional[str] = None
    contact: Optional[str] = None
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MouvementStock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    produit_id: int = Field(foreign_key="produit.id", index=True)
    entrepot_id: int = Field(foreign_key="entrepot.id", index=True)
    entrepot_destination_id: Optional[int] = Field(default=None, foreign_key="entrepot.id", index=True)
    type_mouvement: TypeMouvement
    quantite: Decimal = Field(max_digits=12, decimal_places=2)
    prix_unitaire_mouvement: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    date_peremption: Optional[date] = None
    reference_document: Optional[str] = None
    notes: Optional[str] = None
    date_mouvement: datetime = Field(default_factory=datetime.utcnow, index=True)
```

**Step 3 :** Vérification

Run : `python -c "from gestion_stock.database import init_db; init_db(); print('OK')"` depuis `src/` avec venv activé.
Expected : `OK` et fichier `stock.db` créé.

**Step 4 :** Commit

```bash
git add src/gestion_stock/database.py src/gestion_stock/models.py
git commit -m "feat: add multi-tenant SQLModel schema with merchants, products, warehouses, movements"
```

---

### Task 3 : Créer l'application FastAPI avec lifespan

**Objective :** Monter l'app FastAPI, initialiser la DB au démarrage, router `health`.

**Files :**
- Créer : `src/gestion_stock/main.py`
- Créer : stubs `src/gestion_stock/routers/*.py`

**Step 1 :** Créer `src/gestion_stock/main.py`

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from gestion_stock.database import init_db
from gestion_stock.routers import commercants, produits, entrepots, mouvements, transferts, alertes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Gestion de Stock API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(commercants.router, prefix="/commercants", tags=["commercants"])
app.include_router(produits.router, prefix="/commercants/{commercant_id}/produits", tags=["produits"])
app.include_router(entrepots.router, prefix="/commercants/{commercant_id}/entrepots", tags=["entrepots"])
app.include_router(mouvements.router, prefix="/commercants/{commercant_id}/mouvements", tags=["mouvements"])
app.include_router(transferts.router, prefix="/commercants/{commercant_id}/transferts", tags=["transferts"])
app.include_router(alertes.router, prefix="/commercants/{commercant_id}/alertes", tags=["alertes"])
```

**Step 2 :** Créer les stubs router.

**Step 3 :** Vérification

Run : `uvicorn gestion_stock.main:app --reload --port 8001` puis `curl http://localhost:8001/health`
Expected : `{"status":"ok"}`

**Step 4 :** Commit

```bash
git add src/gestion_stock/main.py src/gestion_stock/routers/
git commit -m "feat: add FastAPI app with multi-tenant routers and health endpoint"
```

---

### Task 4 : CRUD Commerçants

**Objective :** Gérer les commerçants (tenants).

**Files :**
- Modifier : `src/gestion_stock/routers/commercants.py`
- Créer : `src/gestion_stock/tests/test_commercants.py`

**Step 1 :** Failing test — `test_create_commercant`

```python
def test_create_commercant(client):
    response = client.post("/commercants/", json={
        "nom": "Boutique Alpha",
        "email": "contact@alpha.example",
        "telephone": "+33100000000",
        "adresse": "10 rue du Commerce, 75001 Paris",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Boutique Alpha"
```

**Step 2 :** Implémenter `src/gestion_stock/routers/commercants.py` avec POST, GET list, GET one, PATCH, DELETE logique.

**Step 3 :** Lancer le test.
Expected : PASS.

**Step 5 :** Commit

```bash
git add src/gestion_stock/routers/commercants.py src/gestion_stock/tests/test_commercants.py
git commit -m "feat: add merchant CRUD endpoints and tests"
```

---

### Task 5 : CRUD Produits (par commerçant)

**Objective :** Gérer les produits d'un commerçant. SKU unique par commerçant.

**Files :**
- Modifier : `src/gestion_stock/routers/produits.py`
- Créer : `src/gestion_stock/tests/test_produits.py`

**Step 1 :** Failing test — `test_create_produit`

```python
def test_create_produit(client, commercant):
    response = client.post(f"/commercants/{commercant['id']}/produits/", json={
        "sku": "SKU-001",
        "libelle": "Réfrigérateur 300L",
        "categorie": "Électroménager",
        "unite": "pièce",
        "prix_unitaire": "350.00",
        "stock_minimal": "5.00",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["commercant_id"] == commercant["id"]
```

**Step 2 :** Implémenter les endpoints :
- POST /commercants/{commercant_id}/produits/
- GET /commercants/{commercant_id}/produits/
- GET /commercants/{commercant_id}/produits/{produit_id}
- PATCH /commercants/{commercant_id}/produits/{produit_id}
- DELETE /commercants/{commercant_id}/produits/{produit_id} (logique)

Vérifier que `sku` est unique par `commercant_id`.
Vérifier que le produit appartient bien au commerçant.

**Step 3 :** Lancer les tests.
Expected : PASS.

**Step 4 :** Commit

```bash
git add src/gestion_stock/routers/produits.py src/gestion_stock/tests/test_produits.py
git commit -m "feat: add merchant-scoped product CRUD and tests"
```

---

### Task 6 : CRUD Entrepôts (par commerçant)

**Objective :** Gérer les entrepôts d'un commerçant.

**Files :**
- Modifier : `src/gestion_stock/routers/entrepots.py`
- Créer : `src/gestion_stock/tests/test_entrepots.py`

**Step 1 :** Failing test — `test_create_entrepot`

```python
def test_create_entrepot(client, commercant):
    response = client.post(f"/commercants/{commercant['id']}/entrepots/", json={
        "nom": "Entrepôt Drancy",
        "adresse": "12 avenue de la division Leclerc, 93700 Drancy",
        "contact": "logistique@example.com",
    })
    assert response.status_code == 201
    assert response.json()["nom"] == "Entrepôt Drancy"
    assert response.json()["commercant_id"] == commercant["id"]
```

**Step 2 :** Implémenter CRUD entrepôts (même pattern que produits).

**Step 3 :** Lancer les tests.
Expected : PASS.

**Step 4 :** Commit

```bash
git add src/gestion_stock/routers/entrepots.py src/gestion_stock/tests/test_entrepots.py
git commit -m "feat: add merchant-scoped warehouse CRUD and tests"
```

---

### Task 7 : Service de calcul de stock

**Objective :** Créer un service utilitaire qui calcule le stock théorique d'un produit dans un entrepôt.

**Files :**
- Créer : `src/gestion_stock/services/stock.py`
- Créer : `src/gestion_stock/tests/test_stock_service.py`

**Step 1 :** Écrire le service

```python
from decimal import Decimal

from sqlmodel import Session, select

from gestion_stock.models import MouvementStock, TypeMouvement


def stock_produit_entrepot(session: Session, produit_id: int, entrepot_id: int) -> Decimal:
    mouvements = session.exec(
        select(MouvementStock).where(
            MouvementStock.produit_id == produit_id,
            MouvementStock.entrepot_id == entrepot_id,
        )
    ).all()
    total = Decimal("0.00")
    for m in mouvements:
        if m.type_mouvement in (TypeMouvement.SORTIE, TypeMouvement.TRANSFERT_SORTIE):
            total -= m.quantite
        elif m.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE, TypeMouvement.AJUSTEMENT):
            total += m.quantite
    return total


def stock_global_produit(session: Session, produit_id: int) -> Decimal:
    mouvements = session.exec(
        select(MouvementStock).where(MouvementStock.produit_id == produit_id)
    ).all()
    total = Decimal("0.00")
    for m in mouvements:
        if m.type_mouvement in (TypeMouvement.SORTIE, TypeMouvement.TRANSFERT_SORTIE):
            total -= m.quantite
        elif m.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE, TypeMouvement.AJUSTEMENT):
            total += m.quantite
    return total
```

**Step 2 :** Tests.

**Step 3 :** Commit

```bash
git add src/gestion_stock/services/stock.py src/gestion_stock/tests/test_stock_service.py
git commit -m "feat: add stock calculation service"
```

---

### Task 8 : Endpoints Mouvements de stock

**Objective :** Enregistrer entrées, sorties et ajustements, avec stock négatif autorisé temporairement et date de péremption optionnelle.

**Files :**
- Modifier : `src/gestion_stock/routers/mouvements.py`
- Créer : `src/gestion_stock/tests/test_mouvements.py`

**Step 1 :** Failing test — `test_mouvement_sortie_autorise_stock_negatif`

```python
def test_mouvement_sortie_autorise_stock_negatif(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "sortie",
        "quantite": "5.00",
        "reference_document": "BL-001",
    })
    assert response.status_code == 201
    assert response.json()["stock_apres"] == "-5.00"
```

**Step 2 :** Implémenter `src/gestion_stock/routers/mouvements.py`

- Vérifier que `produit_id` et `entrepot_id` appartiennent au commerçant.
- Vérifier que le type est `entree`, `sortie` ou `ajustement`.
- Calculer stock_avant via `stock_produit_entrepot`.
- Appliquer la règle du type de mouvement.
- Accepter `date_peremption` optionnelle.
- Retourner un objet enrichi avec `stock_avant`, `stock_apres`.

**Step 3 :** Lancer les tests.
Expected : PASS.

**Step 4 :** Commit

```bash
git add src/gestion_stock/routers/mouvements.py src/gestion_stock/tests/test_mouvements.py
git commit -m "feat: add stock movement endpoints with expiry date and negative-stock tolerance"
```

---

### Task 9 : Endpoints Transferts entre entrepôts

**Objective :** Permettre le transfert d'un produit d'un entrepôt A vers un entrepôt B du même commerçant.

**Files :**
- Modifier : `src/gestion_stock/routers/transferts.py`
- Créer : `src/gestion_stock/tests/test_transferts.py`

**Step 1 :** Failing test — `test_transfert_entre_entrepots`

```python
def test_transfert_entre_entrepots(client, commercant, produit, entrepot_source, entrepot_dest):
    response = client.post(f"/commercants/{commercant['id']}/transferts/", json={
        "produit_id": produit["id"],
        "entrepot_source_id": entrepot_source["id"],
        "entrepot_destination_id": entrepot_dest["id"],
        "quantite": "10.00",
        "reference_document": "BT-001",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["source_stock_apres"] == "-10.00"
    assert data["destination_stock_apres"] == "10.00"
```

**Step 2 :** Implémenter `src/gestion_stock/routers/transferts.py`

- Vérifier que les deux entrepôts appartiennent au commerçant.
- Vérifier que les deux entrepôts sont différents.
- Créer deux mouvements : `transfert_sortie` sur l'entrepôt source et `transfert_entree` sur l'entrepôt destination.
- Accepter le stock négatif sur la source.

**Step 3 :** Lancer les tests.
Expected : PASS.

**Step 4 :** Commit

```bash
git add src/gestion_stock/routers/transferts.py src/gestion_stock/tests/test_transferts.py
git commit -m "feat: add inter-warehouse transfer endpoints and tests"
```

---

### Task 10 : Valorisation FIFO

**Objective :** Calculer la valorisation FIFO d'un produit dans un entrepôt.

**Files :**
- Modifier : `src/gestion_stock/services/stock.py`
- Créer : `src/gestion_stock/tests/test_valorisation.py`

**Step 1 :** Ajouter dans `stock.py`

```python
def valorisation_fifo(session: Session, produit_id: int, entrepot_id: int) -> Decimal:
    entrees = session.exec(
        select(MouvementStock).where(
            MouvementStock.produit_id == produit_id,
            MouvementStock.entrepot_id == entrepot_id,
            MouvementStock.type_mouvement.in_([TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE]),
        ).order_by(MouvementStock.date_mouvement)
    ).all()

    total = Decimal("0.00")
    for e in entrees:
        prix = e.prix_unitaire_mouvement or Decimal("0.00")
        total += e.quantite * prix
    return total
```

**Step 2 :** Tests.

**Step 3 :** Commit

```bash
git add src/gestion_stock/services/stock.py src/gestion_stock/tests/test_valorisation.py
git commit -m "feat: add FIFO valuation service"
```

---

### Task 11 : Endpoints Alertes de stock

**Objective :** Lister les alertes par commerçant (sous seuil / stock négatif / péremption proche).

**Files :**
- Créer : `src/gestion_stock/services/alertes.py`
- Modifier : `src/gestion_stock/routers/alertes.py`
- Créer : `src/gestion_stock/tests/test_alertes.py`

**Step 1 :** Écrire le service

```python
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from sqlmodel import Session, select

from gestion_stock.models import Produit, Entrepot, MouvementStock
from gestion_stock.services.stock import stock_produit_entrepot


def detecter_alertes(session: Session, commercant_id: int, jours_peremption: int = 30) -> List[Dict[str, Any]]:
    alertes = []
    produits = session.exec(
        select(Produit).where(Produit.commercant_id == commercant_id, Produit.actif == True)
    ).all()
    entrepots = session.exec(
        select(Entrepot).where(Entrepot.commercant_id == commercant_id, Entrepot.actif == True)
    ).all()

    for p in produits:
        for e in entrepots:
            stock = stock_produit_entrepot(session, p.id, e.id)
            if stock < p.stock_minimal or stock < Decimal("0"):
                alertes.append({
                    "type": "negatif" if stock < Decimal("0") else "sous_seuil",
                    "produit_id": p.id,
                    "produit_sku": p.sku,
                    "produit_libelle": p.libelle,
                    "entrepot_id": e.id,
                    "entrepot_nom": e.nom,
                    "stock": str(stock),
                    "seuil_min": str(p.stock_minimal),
                })

    # Alertes péremption
    peremption_limite = date.today() + timedelta(days=jours_peremption)
    mouvements_perimant = session.exec(
        select(MouvementStock).where(
            MouvementStock.commercant_id == commercant_id,
            MouvementStock.date_peremption != None,
            MouvementStock.date_peremption <= peremption_limite,
        )
    ).all()
    for m in mouvements_perimant:
        alertes.append({
            "type": "peremption",
            "produit_id": m.produit_id,
            "entrepot_id": m.entrepot_id,
            "date_peremption": m.date_peremption.isoformat(),
            "quantite": str(m.quantite),
        })

    return alertes
```

**Step 2 :** Implémenter `src/gestion_stock/routers/alertes.py`

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session

from gestion_stock.database import get_session
from gestion_stock.services.alertes import detecter_alertes
from gestion_stock.services.stock import valorisation_fifo

router = APIRouter()


@router.get("/")
def list_alertes(commercant_id: int, session: Session = Depends(get_session), jours_peremption: int = 30):
    return detecter_alertes(session, commercant_id, jours_peremption)


@router.get("/resume")
def resume_alertes(commercant_id: int, session: Session = Depends(get_session)):
    alertes = detecter_alertes(session, commercant_id)
    return {
        "total_alertes": len(alertes),
        "stocks_negatifs": sum(1 for a in alertes if a["type"] == "negatif"),
        "sous_seuils": sum(1 for a in alertes if a["type"] == "sous_seuil"),
        "peremptions": sum(1 for a in alertes if a["type"] == "peremption"),
    }
```

**Step 3 :** Tests.

**Step 4 :** Commit

```bash
git add src/gestion_stock/services/alertes.py src/gestion_stock/routers/alertes.py src/gestion_stock/tests/test_alertes.py
git commit -m "feat: add stock alerts including expiry, threshold and negative stock"
```

---

### Task 12 : Tests d'intégration, fixtures et README

**Objective :** S'assurer que toute la suite passe et documenter l'API.

**Files :**
- Créer : `src/gestion_stock/tests/conftest.py`
- Créer : `README.md`

**Step 1 :** Créer `src/gestion_stock/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from gestion_stock.main import app
from gestion_stock.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="commercant")
def commercant_fixture(client):
    response = client.post("/commercants/", json={
        "nom": "Boutique Test",
        "email": "test@example.com",
    })
    return response.json()
```

**Step 2 :** Lancer la suite complète

Run : `pytest src/gestion_stock/tests -v`
Expected : all passed.

**Step 3 :** Créer `README.md`

```markdown
# Gestion de Stock

Module multi-commerçant FastAPI + SQLite de gestion de stock / inventaire.

## Lancer

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn gestion_stock.main:app --reload --port 8001
```

## Endpoints principaux

- `GET /health`
- `GET|POST /commercants`, `GET|PATCH|DELETE /commercants/{id}`
- `GET|POST /commercants/{id}/produits`, `GET|PATCH|DELETE /commercants/{id}/produits/{produit_id}`
- `GET|POST /commercants/{id}/entrepots`, `GET|PATCH|DELETE /commercants/{id}/entrepots/{entrepot_id}`
- `POST /commercants/{id}/mouvements` (entrée / sortie / ajustement)
- `GET /commercants/{id}/mouvements?produit_id=&entrepot_id=`
- `POST /commercants/{id}/transferts`
- `GET /commercants/{id}/alertes`, `GET /commercants/{id}/alertes/resume`

## Règles métier

- Multi-commerçant : chaque commerçant isole ses produits, entrepôts et mouvements.
- Stock négatif autorisé temporairement (alerte `negatif`).
- Transferts entre entrepôts du même commerçant.
- Valorisation FIFO.
- Dates de péremption optionnelles sur les mouvements.
```

**Step 4 :** Commit

```bash
git add README.md src/gestion_stock/tests/conftest.py
git commit -m "docs: add README, fixtures and full test suite"
```

---

## Validation finale

- [ ] `pytest src/gestion_stock/tests -v` : tous les tests passent
- [ ] `uvicorn gestion_stock.main:app --port 8001` démarre sans erreur
- [ ] `curl http://localhost:8001/health` retourne `{"status":"ok"}`
- [ ] Créer un commerçant, un produit, un entrepôt, puis une sortie de 5 avec stock 0 => stock -5
- [ ] `GET /commercants/{id}/alertes` remonte l'alerte négative
- [ ] Transfert 10 d'un entrepôt à un autre => source -10, destination +10

---

## Risques / Ouvertures

- **Risque :** Pas d'authentification dans le MVP : n'importe qui peut lire/écrire les données d'un commerçant en connaissant son `id`. À corriger impérativement en v2.
- **Risque :** `unique_together` SQLModel via `Config` peut ne pas être pris en charge de façon standard ; vérifier et fallbacker à une contrainte manuelle dans le router si besoin.
- **Ouverture v2 :** Authentification JWT / API key + rôles (commerçant, employé, responsable logistique).
- **Ouverture v2 :** Réservations de stock et commandes fournisseurs.
- **Ouverture v2 :** Export CSV / Excel et tableau de bord.
- **Ouverture v2 :** Valorisation moyenne pondérée au choix.
