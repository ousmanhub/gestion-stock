# Gestion de Stock

Module multi-commerçant FastAPI + SQLite de gestion de stock / inventaire.

## Lancer

```bash
python3.11 -m venv .venv
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
