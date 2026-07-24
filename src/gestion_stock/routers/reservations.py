from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from gestion_stock.auth import get_current_user, require_role, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import (
    Commercant,
    Entrepot,
    Produit,
    Reservation,
    RoleUtilisateur,
    StatutReservation,
    Utilisateur,
)
from gestion_stock.services.stock import stock_disponible

router = APIRouter()


class ReservationCreate(BaseModel):
    produit_id: int
    entrepot_id: int
    quantite: Decimal
    reference_client: str | None = None
    reference_dossier: str | None = None
    notes: str | None = None


def _verifier_commercant(session: Session, commercant_id: int) -> Commercant:
    commercant = session.get(Commercant, commercant_id)
    if not commercant:
        raise HTTPException(status_code=404, detail="Commerçant non trouvé")
    return commercant


def _verifier_produit(session: Session, commercant_id: int, produit_id: int) -> Produit:
    produit = session.exec(
        select(Produit).where(Produit.id == produit_id, Produit.commercant_id == commercant_id, Produit.actif)
    ).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit


def _verifier_entrepot(session: Session, commercant_id: int, entrepot_id: int) -> Entrepot:
    entrepot = session.exec(
        select(Entrepot).where(Entrepot.id == entrepot_id, Entrepot.commercant_id == commercant_id, Entrepot.actif)
    ).first()
    if not entrepot:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    return entrepot


def _reservation_response(reservation: Reservation) -> dict[str, Any]:
    return {
        "id": reservation.id,
        "commercant_id": reservation.commercant_id,
        "produit_id": reservation.produit_id,
        "entrepot_id": reservation.entrepot_id,
        "quantite": str(reservation.quantite),
        "quantite_honoree": str(reservation.quantite_honoree),
        "statut": reservation.statut.value,
        "reference_client": reservation.reference_client,
        "reference_dossier": reservation.reference_dossier,
        "notes": reservation.notes,
        "created_at": reservation.created_at.isoformat(),
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_reservation(
    commercant_id: int,
    data: ReservationCreate,
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
    _verifier_entrepot(session, commercant_id, data.entrepot_id)

    disponible = stock_disponible(session, data.produit_id, data.entrepot_id)
    if data.quantite > disponible:
        raise HTTPException(
            status_code=400,
            detail=f"Stock disponible insuffisant: {disponible} demandé: {data.quantite}",
        )

    reservation = Reservation(
        commercant_id=commercant_id,
        produit_id=data.produit_id,
        entrepot_id=data.entrepot_id,
        quantite=data.quantite,
        quantite_honoree=Decimal("0.00"),
        statut=StatutReservation.EN_COURS,
        reference_client=data.reference_client,
        reference_dossier=data.reference_dossier,
        notes=data.notes,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return _reservation_response(reservation)


@router.get("/", response_model=list[dict])
def list_reservations(
    commercant_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
    produit_id: int | None = None,
    entrepot_id: int | None = None,
    statut: StatutReservation | None = None,
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    query = select(Reservation).where(Reservation.commercant_id == commercant_id)
    if produit_id:
        query = query.where(Reservation.produit_id == produit_id)
    if entrepot_id:
        query = query.where(Reservation.entrepot_id == entrepot_id)
    if statut:
        query = query.where(Reservation.statut == statut)
    reservations = session.exec(query).all()
    return [_reservation_response(r) for r in reservations]


@router.get("/{reservation_id}", response_model=dict)
def get_reservation(
    commercant_id: int,
    reservation_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    reservation = session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.commercant_id == commercant_id,
        )
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    return _reservation_response(reservation)


@router.post("/{reservation_id}/annuler", response_model=dict)
def annuler_reservation(
    commercant_id: int,
    reservation_id: int,
    user: Utilisateur = Depends(
        require_role(
            RoleUtilisateur.COMMERCANT,
            RoleUtilisateur.RESPONSABLE_LOGISTIQUE,
        )
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    reservation = session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.commercant_id == commercant_id,
            Reservation.statut == StatutReservation.EN_COURS,
        )
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée ou déjà terminée")
    reservation.statut = StatutReservation.ANNULEE
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return _reservation_response(reservation)
