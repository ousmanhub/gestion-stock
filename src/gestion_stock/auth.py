import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from gestion_stock.database import get_session
from gestion_stock.models import RoleUtilisateur, Utilisateur


def generate_api_key() -> str:
    return str(uuid.uuid4())


def get_current_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: Session = Depends(get_session),
) -> Utilisateur:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-API-Key manquant",
        )
    user = session.exec(select(Utilisateur).where(Utilisateur.api_key == x_api_key)).first()
    if not user or not user.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalide",
        )
    return user


def require_role(*roles: RoleUtilisateur):
    def checker(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle insuffisant",
            )
        return user
    return checker


def verifier_acces_tenant(user: Utilisateur, commercant_id: int) -> None:
    if user.commercant_id != commercant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit à ce tenant",
        )
