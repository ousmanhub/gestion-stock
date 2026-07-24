# Plan d'implémentation — Interface web React + Vite (v3)

**Goal :** Ajouter un frontend React + Vite dans le dépôt existant, qui consomme l'API FastAPI. CRUD complet pour commerçants, produits, entrepôts, mouvements, transferts, réservations, commandes fournisseurs, alertes. Authentification par API key stockée dans le localStorage.

**Architecture :**
- Backend FastAPI continue de servir l'API sur `/`.
- Frontend dans `frontend/`, servi en production via `StaticFiles` depuis FastAPI.
- En dev : `npm run dev` sur Vite (port 5173) avec proxy vers FastAPI (port 8001).
- CORS activé pour le dev.

**Stack :**
- React 18 + Vite
- React Router DOM
- Tailwind CSS
- Axios

---

## Tâches

### Task 1 : Initialiser le frontend

```bash
cd /Users/smartech/gestion-stock
npm create vite@latest frontend -- --template react
```

### Task 2 : Installer dépendances

```bash
cd frontend
npm install
npm install axios react-router-dom lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Task 3 : Configurer Tailwind

`tailwind.config.js` : content `src/**/*.{js,jsx,ts,tsx}`
`src/index.css` : `@tailwind` directives

### Task 4 : Configurer Vite proxy + CORS backend

`vite.config.js` :
```js
server: {
  proxy: {
    '/api': 'http://127.0.0.1:8001',
  },
}
```

Backend `main.py` : ajouter CORS + optionnellement `StaticFiles`.

### Task 5 : Créer l'App React

- `App.jsx` avec React Router
- `Login.jsx` : saisie API key → stockage localStorage
- `Layout.jsx` : sidebar + header
- Pages : `Dashboard.jsx`, `Produits.jsx`, `Entrepots.jsx`, `Mouvements.jsx`, `Transferts.jsx`, `Reservations.jsx`, `CommandesFournisseurs.jsx`, `Alertes.jsx`, `Utilisateurs.jsx`

### Task 6 : Service API

`src/api.js` : Axios instance avec baseURL `/api`, header X-API-Key.

### Task 7 : Lancer et vérifier

- `npm run dev` dans un terminal
- `uvicorn ...` dans un autre
- Tester la navigation et un CRUD.

### Task 8 : Build et intégrer FastAPI

```bash
cd frontend
npm run build
```

Servir `frontend/dist` via `StaticFiles` dans `main.py`.

### Task 9 : README + commit + push

---

## Endpoints API que le frontend consomme

- `POST /commercants/` puis stocke la clé retournée
- Tous les autres endpoints avec `X-API-Key`

## Permissions simplifiées dans l'UI

- Si rôle = employé : masquer les menus création utilisateur, commandes fournisseurs, modification produit/entrepôt.
