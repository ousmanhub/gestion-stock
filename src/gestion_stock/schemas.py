from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from gestion_stock.models import TypeMouvement


class MouvementCreate(BaseModel):
    produit_id: int
    entrepot_id: int
    type_mouvement: TypeMouvement
    quantite: Decimal
    prix_unitaire_mouvement: Decimal | None = None
    date_peremption: date | None = None
    reference_document: str | None = None
    notes: str | None = None


class TransfertCreate(BaseModel):
    produit_id: int
    entrepot_source_id: int
    entrepot_destination_id: int
    quantite: Decimal
    reference_document: str | None = None
