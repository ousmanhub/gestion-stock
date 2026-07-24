
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.auth import generate_api_key, require_role, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import Commercant, RoleUtilisateur, Utilisateur

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_commercant(commercant: Commercant, session: Session = Depends(get_session)):
    session.add(commercant)
    session.commit()
    session.refresh(commercant)

    admin = Utilisateur(
        commercant_id=commercant.id,
        nom=commercant.nom,
        email=commercant.email,
        role=RoleUtilisateur.COMMERCANT,
        api_key=generate_api_key(),
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    return {
        "id": commercant.id,
        "nom": commercant.nom,
        "email": commercant.email,
        "telephone": commercant.telephone,
        "adresse": commercant.adresse,
        "api_key": admin.api_key,
    }


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
def update_commercant(
    commercant_id: int,
    updates: Commercant,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT)),
    session: Session = Depends(get_session),
):
    verifier_acces_tenant(user, commercant_id)
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
def delete_commercant(
    commercant_id: int,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT)),
    session: Session = Depends(get_session),
):
    verifier_acces_tenant(user, commercant_id)
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    commercant.actif = False
    session.add(commercant)
    session.commit()
    return None


@router.post("/{commercant_id}/utilisateurs", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_utilisateur(
    commercant_id: int,
    utilisateur: Utilisateur,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT)),
    session: Session = Depends(get_session),
):
    verifier_acces_tenant(user, commercant_id)
    if utilisateur.role == RoleUtilisateur.COMMERCANT:
        raise HTTPException(status_code=400, detail="Impossible de créer un autre commerçant via cet endpoint")
    utilisateur.commercant_id = commercant_id
    utilisateur.api_key = generate_api_key()
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return {
        "id": utilisateur.id,
        "commercant_id": utilisateur.commercant_id,
        "nom": utilisateur.nom,
        "email": utilisateur.email,
        "role": utilisateur.role.value,
        "api_key": utilisateur.api_key,
    }


@router.get("/{commercant_id}/utilisateurs", response_model=list[Utilisateur])
def list_utilisateurs(
    commercant_id: int,
    user: Utilisateur = Depends(require_role(RoleUtilisateur.COMMERCANT)),
    session: Session = Depends(get_session),
):
    verifier_acces_tenant(user, commercant_id)
    return session.exec(
        select(Utilisateur).where(Utilisateur.commercant_id == commercant_id, Utilisateur.actif)
    ).all()
