
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from gestion_stock.auth import require_role, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import (
    Commercant,
    Entrepot,
    MouvementStock,
    Produit,
    RoleUtilisateur,
    TypeMouvement,
    Utilisateur,
)
from gestion_stock.services.stock import stock_produit_entrepot

router = APIRouter()


class TransfertCreate(BaseModel):
    produit_id: int
    entrepot_source_id: int
    entrepot_destination_id: int
    quantite: Decimal
    reference_document: str | None = None


def _verifier_commercant(session: Session, commercant_id: int) -> Commercant:
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


def _verifier_produit(session: Session, commercant_id: int, produit_id: int) -> Produit:
    produit = session.get(Produit, produit_id)
    if not produit or produit.commercant_id != commercant_id or not produit.actif:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit


def _verifier_entrepot(session: Session, commercant_id: int, entrepot_id: int) -> Entrepot:
    entrepot = session.get(Entrepot, entrepot_id)
    if not entrepot or entrepot.commercant_id != commercant_id or not entrepot.actif:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    return entrepot


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_transfert(
    commercant_id: int,
    data: TransfertCreate,
    user: Utilisateur = Depends(
        require_role(
            RoleUtilisateur.COMMERCANT,
            RoleUtilisateur.RESPONSABLE_LOGISTIQUE,
            RoleUtilisateur.EMPLOYE,
        )
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    _verifier_produit(session, commercant_id, data.produit_id)
    source = _verifier_entrepot(session, commercant_id, data.entrepot_source_id)
    dest = _verifier_entrepot(session, commercant_id, data.entrepot_destination_id)

    if data.entrepot_source_id == data.entrepot_destination_id:
        raise HTTPException(status_code=400, detail="Les entrepôts source et destination doivent être différents")

    stock_source_avant = stock_produit_entrepot(session, data.produit_id, data.entrepot_source_id)
    stock_dest_avant = stock_produit_entrepot(session, data.produit_id, data.entrepot_destination_id)
    stock_source_apres = stock_source_avant - data.quantite
    stock_dest_apres = stock_dest_avant + data.quantite

    mouvement_sortie = MouvementStock(
        commercant_id=commercant_id,
        produit_id=data.produit_id,
        entrepot_id=data.entrepot_source_id,
        entrepot_destination_id=data.entrepot_destination_id,
        type_mouvement=TypeMouvement.TRANSFERT_SORTIE,
        quantite=data.quantite,
        reference_document=data.reference_document,
    )
    mouvement_entree = MouvementStock(
        commercant_id=commercant_id,
        produit_id=data.produit_id,
        entrepot_id=data.entrepot_destination_id,
        entrepot_destination_id=data.entrepot_source_id,
        type_mouvement=TypeMouvement.TRANSFERT_ENTREE,
        quantite=data.quantite,
        reference_document=data.reference_document,
    )

    session.add(mouvement_sortie)
    session.add(mouvement_entree)
    session.commit()
    session.refresh(mouvement_sortie)
    session.refresh(mouvement_entree)

    return {
        "transfert_id": f"{mouvement_sortie.id}-{mouvement_entree.id}",
        "commercant_id": commercant_id,
        "produit_id": data.produit_id,
        "entrepot_source_id": data.entrepot_source_id,
        "entrepot_source_nom": source.nom,
        "entrepot_destination_id": data.entrepot_destination_id,
        "entrepot_destination_nom": dest.nom,
        "quantite": str(data.quantite),
        "source_stock_avant": str(stock_source_avant),
        "source_stock_apres": str(stock_source_apres),
        "destination_stock_avant": str(stock_dest_avant),
        "destination_stock_apres": str(stock_dest_apres),
    }
