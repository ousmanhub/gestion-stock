from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from gestion_stock.auth import get_current_user, require_role, verifier_acces_tenant
from gestion_stock.database import get_session
from gestion_stock.models import (
    CommandeFournisseur,
    Commercant,
    Entrepot,
    MouvementStock,
    Produit,
    RoleUtilisateur,
    StatutCommandeFournisseur,
    TypeMouvement,
    Utilisateur,
)

router = APIRouter()


class CommandeCreate(BaseModel):
    produit_id: int
    entrepot_destination_id: int
    fournisseur_nom: str
    fournisseur_contact: str | None = None
    quantite_commandee: Decimal
    prix_unitaire_prevu: Decimal | None = None
    date_livraison_estimee: date | None = None
    reference_commande: str | None = None
    notes: str | None = None


class CommandeUpdate(BaseModel):
    fournisseur_nom: str | None = None
    fournisseur_contact: str | None = None
    quantite_commandee: Decimal | None = None
    prix_unitaire_prevu: Decimal | None = None
    date_livraison_estimee: date | None = None
    reference_commande: str | None = None
    notes: str | None = None


class ReceptionCreate(BaseModel):
    quantite: Decimal
    date_peremption: date | None = None
    reference_document: str | None = None


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


def _commande_response(commande: CommandeFournisseur) -> dict[str, Any]:
    return {
        "id": commande.id,
        "commercant_id": commande.commercant_id,
        "produit_id": commande.produit_id,
        "entrepot_destination_id": commande.entrepot_destination_id,
        "fournisseur_nom": commande.fournisseur_nom,
        "fournisseur_contact": commande.fournisseur_contact,
        "quantite_commandee": str(commande.quantite_commandee),
        "quantite_recue": str(commande.quantite_recue),
        "prix_unitaire_prevu": str(commande.prix_unitaire_prevu) if commande.prix_unitaire_prevu else None,
        "date_livraison_estimee": (
            commande.date_livraison_estimee.isoformat() if commande.date_livraison_estimee else None
        ),
        "statut": commande.statut.value,
        "reference_commande": commande.reference_commande,
        "notes": commande.notes,
        "created_at": commande.created_at.isoformat(),
        "updated_at": commande.updated_at.isoformat(),
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_commande(
    commercant_id: int,
    data: CommandeCreate,
    user: Utilisateur = Depends(
        require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    _verifier_produit(session, commercant_id, data.produit_id)
    _verifier_entrepot(session, commercant_id, data.entrepot_destination_id)

    commande = CommandeFournisseur(
        commercant_id=commercant_id,
        produit_id=data.produit_id,
        entrepot_destination_id=data.entrepot_destination_id,
        fournisseur_nom=data.fournisseur_nom,
        fournisseur_contact=data.fournisseur_contact,
        quantite_commandee=data.quantite_commandee,
        quantite_recue=Decimal("0.00"),
        prix_unitaire_prevu=data.prix_unitaire_prevu,
        date_livraison_estimee=data.date_livraison_estimee,
        statut=StatutCommandeFournisseur.BROUILLON,
        reference_commande=data.reference_commande,
        notes=data.notes,
    )
    session.add(commande)
    session.commit()
    session.refresh(commande)
    return _commande_response(commande)


@router.get("/", response_model=list[dict])
def list_commandes(
    commercant_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
    produit_id: int | None = None,
    statut: StatutCommandeFournisseur | None = None,
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    query = select(CommandeFournisseur).where(CommandeFournisseur.commercant_id == commercant_id)
    if produit_id:
        query = query.where(CommandeFournisseur.produit_id == produit_id)
    if statut:
        query = query.where(CommandeFournisseur.statut == statut)
    commandes = session.exec(query).all()
    return [_commande_response(c) for c in commandes]


@router.get("/{commande_id}", response_model=dict)
def get_commande(
    commercant_id: int,
    commande_id: int,
    user: Utilisateur = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    commande = session.exec(
        select(CommandeFournisseur).where(
            CommandeFournisseur.id == commande_id,
            CommandeFournisseur.commercant_id == commercant_id,
        )
    ).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return _commande_response(commande)


@router.patch("/{commande_id}", response_model=dict)
def update_commande(
    commercant_id: int,
    commande_id: int,
    data: CommandeUpdate,
    user: Utilisateur = Depends(
        require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    commande = session.exec(
        select(CommandeFournisseur).where(
            CommandeFournisseur.id == commande_id,
            CommandeFournisseur.commercant_id == commercant_id,
        )
    ).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    if commande.statut != StatutCommandeFournisseur.BROUILLON:
        raise HTTPException(status_code=400, detail="Modification uniquement autorisée en statut brouillon")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(commande, key, value)
    session.add(commande)
    session.commit()
    session.refresh(commande)
    return _commande_response(commande)


@router.post("/{commande_id}/envoyer", response_model=dict)
def envoyer_commande(
    commercant_id: int,
    commande_id: int,
    user: Utilisateur = Depends(
        require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    commande = session.exec(
        select(CommandeFournisseur).where(
            CommandeFournisseur.id == commande_id,
            CommandeFournisseur.commercant_id == commercant_id,
            CommandeFournisseur.statut == StatutCommandeFournisseur.BROUILLON,
        )
    ).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée ou déjà envoyée")
    commande.statut = StatutCommandeFournisseur.ENVOYEE
    session.add(commande)
    session.commit()
    session.refresh(commande)
    return _commande_response(commande)


@router.post("/{commande_id}/receptionner", response_model=dict)
def receptionner_commande(
    commercant_id: int,
    commande_id: int,
    data: ReceptionCreate,
    user: Utilisateur = Depends(
        require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    commande = session.exec(
        select(CommandeFournisseur).where(
            CommandeFournisseur.id == commande_id,
            CommandeFournisseur.commercant_id == commercant_id,
            CommandeFournisseur.statut.in_(
                [StatutCommandeFournisseur.ENVOYEE, StatutCommandeFournisseur.PARTIELLEMENT_RECUE]
            ),
        )
    ).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée ou non réceptionnable")

    reste = commande.quantite_commandee - commande.quantite_recue
    if data.quantite > reste:
        raise HTTPException(
            status_code=400,
            detail=f"Quantité reçue {data.quantite} supérieure au reste à recevoir {reste}",
        )

    mouvement = MouvementStock(
        commercant_id=commercant_id,
        produit_id=commande.produit_id,
        entrepot_id=commande.entrepot_destination_id,
        type_mouvement=TypeMouvement.ENTREE,
        quantite=data.quantite,
        prix_unitaire_mouvement=commande.prix_unitaire_prevu,
        date_peremption=data.date_peremption,
        reference_document=data.reference_document,
    )
    session.add(mouvement)

    commande.quantite_recue += data.quantite
    if commande.quantite_recue >= commande.quantite_commandee:
        commande.statut = StatutCommandeFournisseur.RECUE
    else:
        commande.statut = StatutCommandeFournisseur.PARTIELLEMENT_RECUE
    session.add(commande)

    session.commit()
    session.refresh(commande)
    session.refresh(mouvement)
    return {
        "commande": _commande_response(commande),
        "mouvement_id": mouvement.id,
    }


@router.post("/{commande_id}/annuler", response_model=dict)
def annuler_commande(
    commercant_id: int,
    commande_id: int,
    user: Utilisateur = Depends(
        require_role(RoleUtilisateur.COMMERCANT, RoleUtilisateur.RESPONSABLE_LOGISTIQUE)
    ),
    session: Session = Depends(get_session),
):
    _verifier_commercant(session, commercant_id)
    verifier_acces_tenant(user, commercant_id)
    commande = session.exec(
        select(CommandeFournisseur).where(
            CommandeFournisseur.id == commande_id,
            CommandeFournisseur.commercant_id == commercant_id,
            CommandeFournisseur.statut != StatutCommandeFournisseur.ANNULEE,
        )
    ).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée ou déjà annulée")
    if commande.statut == StatutCommandeFournisseur.RECUE:
        raise HTTPException(status_code=400, detail="Impossible d'annuler une commande entièrement reçue")
    commande.statut = StatutCommandeFournisseur.ANNULEE
    session.add(commande)
    session.commit()
    session.refresh(commande)
    return _commande_response(commande)
