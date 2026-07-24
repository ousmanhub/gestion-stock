
from fastapi import APIRouter, Depends
from sqlmodel import Session

from gestion_stock.auth import get_current_user, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import Utilisateur
from gestion_stock.services.alertes import detecter_alertes

router = APIRouter()


@router.get("/")
def list_alertes(
    commercant_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
    jours_peremption: int = 30,
):
    verifier_acces_tenant(user, commercant_id)
    return detecter_alertes(session, commercant_id, jours_peremption)


@router.get("/resume")
def resume_alertes(
    commercant_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verifier_acces_tenant(user, commercant_id)
    alertes = detecter_alertes(session, commercant_id)
    return {
        "total_alertes": len(alertes),
        "stocks_negatifs": sum(1 for a in alertes if a["type"] == "negatif"),
        "sous_seuils": sum(1 for a in alertes if a["type"] == "sous_seuil"),
        "peremptions": sum(1 for a in alertes if a["type"] == "peremption"),
    }
