from decimal import Decimal

from sqlmodel import Session, select

from gestion_stock.models import MouvementStock, TypeMouvement


def stock_produit_entrepot(session: Session, produit_id: int, entrepot_id: int) -> Decimal:
    mouvements = session.exec(
        select(MouvementStock).where(
            MouvementStock.produit_id == produit_id,
            MouvementStock.entrepot_id == entrepot_id,
        )
    ).all()
    total = Decimal("0.00")
    for m in mouvements:
        if m.type_mouvement in (TypeMouvement.SORTIE, TypeMouvement.TRANSFERT_SORTIE):
            total -= m.quantite
        elif m.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE, TypeMouvement.AJUSTEMENT):
            total += m.quantite
    return total


def stock_global_produit(session: Session, produit_id: int) -> Decimal:
    mouvements = session.exec(
        select(MouvementStock).where(MouvementStock.produit_id == produit_id)
    ).all()
    total = Decimal("0.00")
    for m in mouvements:
        if m.type_mouvement in (TypeMouvement.SORTIE, TypeMouvement.TRANSFERT_SORTIE):
            total -= m.quantite
        elif m.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE, TypeMouvement.AJUSTEMENT):
            total += m.quantite
    return total


def valorisation_fifo(session: Session, produit_id: int, entrepot_id: int) -> Decimal:
    entrees = session.exec(
        select(MouvementStock).where(
            MouvementStock.produit_id == produit_id,
            MouvementStock.entrepot_id == entrepot_id,
            MouvementStock.type_mouvement.in_([TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE]),
        ).order_by(MouvementStock.date_mouvement)
    ).all()

    total = Decimal("0.00")
    for e in entrees:
        prix = e.prix_unitaire_mouvement or Decimal("0.00")
        total += e.quantite * prix
    return total
