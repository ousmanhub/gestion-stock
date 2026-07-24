# Gestion de Stock

Module multi-commerçant FastAPI + SQLite de gestion de stock / inventaire.

## Stack

- FastAPI
- SQLModel
- SQLite
- pytest / httpx
- ruff

## Installation

```bash
cd /Users/smartech/gestion-stock
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Lancer l'API

```bash
source .venv/bin/activate
uvicorn gestion_stock.main:app --reload --port 8001
```

- Interface Swagger : http://127.0.0.1:8001/docs
- Health check : http://127.0.0.1:8001/health

## Authentification

L'API utilise une clé API statique passée dans le header `X-API-Key`.

### Créer un commerçant (endpoint public)

```bash
curl -X POST http://127.0.0.1:8001/commercants/ \
  -H 'Content-Type: application/json' \
  -d '{"nom":"Boutique Alpha","email":"contact@alpha.example"}'
```

La réponse contient `api_key` — c'est la clé administrateur du tenant.

### Créer un utilisateur

```bash
curl -X POST http://127.0.0.1:8001/commercants/{id}/utilisateurs \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: {admin_key}' \
  -d '{"nom":"Employé","email":"emp@example.com","role":"employe"}'
```

### Rôles

- `commercant` : admin complet du tenant, peut créer des utilisateurs
- `responsable_logistique` : lecture/écriture sur produits, entrepôts, mouvements, transferts, alertes
- `employe` : saisie de mouvements et transferts uniquement, lecture restreinte

## Endpoints principaux

- `GET /health`
- `POST /commercants/`
- `GET|PATCH|DELETE /commercants/{id}`
- `POST|GET /commercants/{id}/utilisateurs`
- `POST|GET|PATCH|DELETE /commercants/{id}/produits`
- `POST|GET|PATCH|DELETE /commercants/{id}/entrepots`
- `POST|GET /commercants/{id}/mouvements`
- `POST /commercants/{id}/transferts`
- `GET /commercants/{id}/alertes`
- `GET /commercants/{id}/alertes/resume`

## Tests

```bash
source .venv/bin/activate
pytest src/gestion_stock/tests -v
```

## Lint

```bash
ruff check src/gestion_stock
```
