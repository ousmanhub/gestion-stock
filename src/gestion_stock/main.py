from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from gestion_stock.database import init_db
from gestion_stock.routers import (
    alertes,
    commandes_fournisseurs,
    commercants,
    entrepots,
    mouvements,
    produits,
    reservations,
    transferts,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Gestion de Stock API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(commercants.router, prefix="/commercants", tags=["commercants"])
app.include_router(produits.router, prefix="/commercants/{commercant_id}/produits", tags=["produits"])
app.include_router(entrepots.router, prefix="/commercants/{commercant_id}/entrepots", tags=["entrepots"])
app.include_router(mouvements.router, prefix="/commercants/{commercant_id}/mouvements", tags=["mouvements"])
app.include_router(transferts.router, prefix="/commercants/{commercant_id}/transferts", tags=["transferts"])
app.include_router(alertes.router, prefix="/commercants/{commercant_id}/alertes", tags=["alertes"])
app.include_router(
    reservations.router, prefix="/commercants/{commercant_id}/reservations", tags=["reservations"]
)
app.include_router(
    commandes_fournisseurs.router,
    prefix="/commercants/{commercant_id}/commandes-fournisseurs",
    tags=["commandes-fournisseurs"],
)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(request: Request, full_path: str):
    if request.url.path.startswith('/commercants') or request.url.path.startswith('/health'):
        return None
    dist_file = Path("frontend/dist") / full_path
    if dist_file.is_file():
        return FileResponse(str(dist_file))
    return FileResponse("frontend/dist/index.html")
