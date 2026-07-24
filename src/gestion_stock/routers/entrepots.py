
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.database import get_session
from gestion_stock.models import Commercant, Entrepot

router = APIRouter()


def _verifier_commercant(session: Session, commercant_id: int) -> Commercant:
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


@router.post("/", response_model=Entrepot, status_code=status.HTTP_201_CREATED)
def create_entrepot(commercant_id: int, entrepot: Entrepot, session: Session = Depends(get_session)):
    _verifier_commercant(session, commercant_id)
    entrepot.commercant_id = commercant_id
    session.add(entrepot)
    session.commit()
    session.refresh(entrepot)
    return entrepot


@router.get("/", response_model=list[Entrepot])
def list_entrepots(commercant_id: int, session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    _verifier_commercant(session, commercant_id)
    return session.exec(
        select(Entrepot)
        .where(Entrepot.commercant_id == commercant_id, Entrepot.actif)
        .offset(skip)
        .limit(limit)
    ).all()


@router.get("/{entrepot_id}", response_model=Entrepot)
def get_entrepot(commercant_id: int, entrepot_id: int, session: Session = Depends(get_session)):
    _verifier_commercant(session, commercant_id)
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


@router.patch("/{entrepot_id}", response_model=Entrepot)
def update_entrepot(commercant_id: int, entrepot_id: int, updates: Entrepot, session: Session = Depends(get_session)):
    _verifier_commercant(session, commercant_id)
    entrepot = session.exec(
        select(Entrepot).where(
            Entrepot.id == entrepot_id,
            Entrepot.commercant_id == commercant_id,
        )
    ).first()
    if not entrepot:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    data = updates.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(entrepot, key, value)
    session.add(entrepot)
    session.commit()
    session.refresh(entrepot)
    return entrepot


@router.delete("/{entrepot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entrepot(commercant_id: int, entrepot_id: int, session: Session = Depends(get_session)):
    _verifier_commercant(session, commercant_id)
    entrepot = session.exec(
        select(Entrepot).where(
            Entrepot.id == entrepot_id,
            Entrepot.commercant_id == commercant_id,
        )
    ).first()
    if not entrepot:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    entrepot.actif = False
    session.add(entrepot)
    session.commit()
