# Gestion de Stock — Frontend

Interface web React + Vite pour l'API de gestion de stock.

## Prérequis

- Node.js 18+
- API backend lancée sur http://127.0.0.1:8001

## Installation

```bash
cd /Users/smartech/gestion-stock/frontend
npm install
```

## Lancer en développement

Terminal 1 (backend) :
```bash
cd /Users/smartech/gestion-stock
source .venv/bin/activate
uvicorn gestion_stock.main:app --reload --port 8001
```

Terminal 2 (frontend) :
```bash
cd /Users/smartech/gestion-stock/frontend
npm run dev
```

Ouvrir http://localhost:5173

## Connexion

Collez une clé API valide (X-API-Key). La clé admin est fournie à la création d'un commerçant via `POST /commercants/`.

## Build pour production

```bash
cd /Users/smartech/gestion-stock/frontend
npm run build
```

Le build se trouve dans `frontend/dist`.
