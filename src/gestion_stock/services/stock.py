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


def valorisation_fifo(session: Session, produit_id: int, entrepot_id: int) -> tuple[Decimal, Decimal]:
    mouvements = session.exec(
        select(MouvementStock).where(
            MouvementStock.produit_id == produit_id,
            MouvementStock.entrepot_id == entrepot_id,
        ).order_by(MouvementStock.date_mouvement)
    ).all()

    lots: list[tuple[Decimal, Decimal]] = []  # (quantité restante, prix unitaire)
    for m in mouvements:
        if m.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.TRANSFERT_ENTREE, TypeMouvement.AJUSTEMENT):
            prix = m.prix_unitaire_mouvement or Decimal("0.00")
            lots.append((m.quantite, prix))
        elif m.type_mouvement in (TypeMouvement.SORTIE, TypeMouvement.TRANSFERT_SORTIE):
            restant_a_sortir = m.quantite
            while restant_a_sortir > 0 and lots:
                lot_quantite, lot_prix = lots[0]
                if lot_quantite <= restant_a_sortir:
                    restant_a_sortir -= lot_quantite
                    lots.pop(0)
                else:
                    lots[0] = (lot_quantite - restant_a_sortir, lot_prix)
                    restant_a_sortir = Decimal("0.00")

    total_valeur = Decimal("0.00")
    total_quantite = Decimal("0.00")
    for quantite, prix in lots:
        total_valeur += quantite * prix
        total_quantite += quantite
    return total_valeur, total_quantite
