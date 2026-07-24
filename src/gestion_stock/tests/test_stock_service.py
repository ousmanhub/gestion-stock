from decimal import Decimal

from gestion_stock.models import MouvementStock, TypeMouvement
from gestion_stock.services.stock import (
    stock_produit_entrepot,
    valorisation_fifo,
)


def test_stock_produit_entrepot(session, produit, entrepot):
    m1 = MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("10.00"),
    )
    m2 = MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.SORTIE,
        quantite=Decimal("3.00"),
    )
    session.add(m1)
    session.add(m2)
    session.commit()
    assert stock_produit_entrepot(session, produit["id"], entrepot["id"]) == Decimal("7.00")


def test_valorisation_fifo(session, produit, entrepot):
    m1 = MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("10.00"),
        prix_unitaire_mouvement=Decimal("5.00"),
    )
    m2 = MouvementStock(
        commercant_id=produit["commercant_id"],
        produit_id=produit["id"],
        entrepot_id=entrepot["id"],
        type_mouvement=TypeMouvement.ENTREE,
        quantite=Decimal("5.00"),
        prix_unitaire_mouvement=Decimal("7.00"),
    )
    session.add(m1)
    session.add(m2)
    session.commit()
    assert valorisation_fifo(session, produit["id"], entrepot["id"]) == Decimal("85.00")
