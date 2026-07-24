
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.database import get_session
from gestion_stock.models import Commercant

router = APIRouter()


@router.post("/", response_model=Commercant, status_code=status.HTTP_201_CREATED)
def create_commercant(commercant: Commercant, session: Session = Depends(get_session)):
    session.add(commercant)
    session.commit()
    session.refresh(commercant)
    return commercant


@router.get("/", response_model=list[Commercant])
def list_commercants(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    return session.exec(select(Commercant).where(Commercant.actif).offset(skip).limit(limit)).all()


@router.get("/{commercant_id}", response_model=Commercant)
def get_commercant(commercant_id: int, session: Session = Depends(get_session)):
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


@router.patch("/{commercant_id}", response_model=Commercant)
def update_commercant(commercant_id: int, updates: Commercant, session: Session = Depends(get_session)):
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    data = updates.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(commercant, key, value)
    session.add(commercant)
    session.commit()
    session.refresh(commercant)
    return commercant


@router.delete("/{commercant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_commercant(commercant_id: int, session: Session = Depends(get_session)):
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    commercant.actif = False
    session.add(commercant)
    session.commit()
