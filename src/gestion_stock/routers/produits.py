
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.auth import get_current_user, require_role, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import Commercant, Produit, RoleUtilisateur, Utilisateur

router = APIRouter()


def _verifier_commercant(session: Session, commercant_id: int) -> Commercant:
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


@router.post("/", response_model=Produit, status_code=status.HTTP_201_CREATED)
def create_produit(
    commercant_id: int,
    produit: Produit,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    existing = session.exec(
        select(Produit).where(Produit.commercant_id == commercant_id, Produit.sku == produit.sku, Produit.actif)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU déjà utilisé pour ce commerçant")
    produit.commercant_id = commercant_id
    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit


@router.get("/", response_model=list[Produit])
def list_produits(
    commercant_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    return session.exec(
        select(Produit).where(Produit.commercant_id == commercant_id, Produit.actif).offset(skip).limit(limit)
    ).all()


@router.get("/{produit_id}", response_model=Produit)
def get_produit(
    commercant_id: int,
    produit_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    produit = session.exec(
        select(Produit).where(Produit.id == produit_id, Produit.commercant_id == commercant_id, Produit.actif)
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit


@router.patch("/{produit_id}", response_model=Produit)
def update_produit(
    commercant_id: int,
    produit_id: int,
    updates: Produit,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    produit = session.exec(
        select(Produit).where(Produit.id == produit_id, Produit.commercant_id == commercant_id, Produit.actif)
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    data = updates.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(produit, key, value)
    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit


@router.delete("/{produit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produit(
    commercant_id: int,
    produit_id: int,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    produit = session.exec(
        select(Produit).where(Produit.id == produit_id, Produit.commercant_id == commercant_id, Produit.actif)
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    produit.actif = False
    session.add(produit)
    session.commit()
    return None
