from contextlib import asynccontextmanager

from fastapi import FastAPI

from gestion_stock.database import init_db
from gestion_stock.routers import alertes, commercants, entrepots, mouvements, produits, transferts


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
