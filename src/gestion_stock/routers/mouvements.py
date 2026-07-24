
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.database import get_session
from gestion_stock.models import Commercant, Entrepot, MouvementStock, Produit, TypeMouvement
from gestion_stock.schemas import MouvementCreate
from gestion_stock.services.stock import stock_produit_entrepot

router = APIRouter()


def _verifier_commercant(session: Session, commercant_id: int) -> Commercant:
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


def _verifier_produit(session: Session, commercant_id: int, produit_id: int) -> Produit:
    produit = session.exec(
        select(Produit).where(
            Produit.id == produit_id,
            Produit.commercant_id == commercant_id,
            Produit.actif,
        )
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit


def _verifier_entrepot(session: Session, commercant_id: int, entrepot_id: int) -> Entrepot:
    entrepot = session.exec(
        select(Entrepot).where(
            Entrepot.id == entrepot_id,
            Entrepot.commercant_id == commercant_id,
            Entrepot.actif,
        )
    ).first()
    if not entrepot:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    return entrepot


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_mouvement(
    commercant_id: int,
    data: MouvementCreate,
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    _verifier_produit(session, commercant_id, data.produit_id)
    _verifier_entrepot(session, commercant_id, data.entrepot_id)

    if data.type_mouvement not in (TypeMouvement.ENTREE, TypeMouvement.SORTIE, TypeMouvement.AJUSTEMENT):
        raise HTTPException(
            status_code=400,
            detail="Type de mouvement non autorisé pour ce endpoint (utiliser /transferts pour les transferts)",
        )

    stock_avant = stock_produit_entrepot(session, data.produit_id, data.entrepot_id)

    if data.type_mouvement == TypeMouvement.ENTREE:
        stock_apres = stock_avant + data.quantite
        mouvement_quantite = data.quantite
    elif data.type_mouvement == TypeMouvement.SORTIE:
        stock_apres = stock_avant - data.quantite
        mouvement_quantite = data.quantite
    else:  # ajustement
        stock_apres = data.quantite
        mouvement_quantite = stock_apres - stock_avant

    mouvement = MouvementStock(
        commercant_id=commercant_id,
        produit_id=data.produit_id,
        entrepot_id=data.entrepot_id,
        type_mouvement=data.type_mouvement,
        quantite=mouvement_quantite,
        prix_unitaire_mouvement=data.prix_unitaire_mouvement,
        date_peremption=data.date_peremption,
        reference_document=data.reference_document,
        notes=data.notes,
    )
    session.add(mouvement)
    session.commit()
    session.refresh(mouvement)

    prix_str = str(mouvement.prix_unitaire_mouvement) if mouvement.prix_unitaire_mouvement else None
    peremption_str = mouvement.date_peremption.isoformat() if mouvement.date_peremption else None
    return {
        "id": mouvement.id,
        "commercant_id": mouvement.commercant_id,
        "produit_id": mouvement.produit_id,
        "entrepot_id": mouvement.entrepot_id,
        "type_mouvement": mouvement.type_mouvement.value,
        "quantite": str(mouvement.quantite),
        "prix_unitaire_mouvement": prix_str,
        "date_peremption": peremption_str,
        "reference_document": mouvement.reference_document,
        "stock_avant": str(stock_avant),
        "stock_apres": str(stock_apres),
        "date_mouvement": mouvement.date_mouvement.isoformat(),
    }


@router.get("/", response_model=list[MouvementStock])
def list_mouvements(
    commercant_id: int,
    session: Session = Depends(get_session),
    produit_id: int | None = None,
    entrepot_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    _verifier_commercant(session, commercant_id)
    query = select(MouvementStock).where(MouvementStock.commercant_id == commercant_id)
    if produit_id:
        query = query.where(MouvementStock.produit_id == produit_id)
    if entrepot_id:
        query = query.where(MouvementStock.entrepot_id == entrepot_id)
    return session.exec(query.offset(skip).limit(limit)).all()
