from decimal import Decimal

from gestion_stock.models import MouvementStock, TypeMouvement
from gestion_stock.services.stock import stock_global_produit, stock_produit_entrepot, valorisation_fifo


def test_stock_produit_entrepot(session, produit, entrepot):
    m1 = MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("10.00"),
    )
    session.add(m1)
    session.commit()
    assert stock_produit_entrepot(session, produit["id"], entrepot["id"]) == Decimal("10.00")


def test_stock_global_produit(session, produit, entrepot, entrepot_dest):
    session.add(MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("5.00"),
    ))
    session.add(MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot_dest["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("7.00"),
    ))
    session.commit()
    assert stock_global_produit(session, produit["id"]) == Decimal("12.00")


def test_valorisation_fifo(session, produit, entrepot):
    session.add(MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("10.00"),
        prix_unitaire_mouvement=Decimal("100.00"),
    ))
    session.add(MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("10.00"),
        prix_unitaire_mouvement=Decimal("120.00"),
    ))
    session.add(MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.SORTIE,
        quantite=Decimal("15.00"),
    ))
    session.commit()
    valeur, _ = valorisation_fifo(session, produit["id"], entrepot["id"])
    assert valeur == Decimal("600.00")  # reste 5 unités du lot à 120
