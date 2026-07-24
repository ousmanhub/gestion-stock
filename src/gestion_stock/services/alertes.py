from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlmodel import Session, select

from gestion_stock.models import Entrepot, MouvementStock, Produit
from gestion_stock.services.stock import stock_produit_entrepot


def detecter_alertes(session: Session, commercant_id: int, jours_peremption: int = 30) -> list[dict[str, Any]]:
    alertes = []
    produits = session.exec(
        select(Produit).where(Produit.commercant_id == commercant_id, Produit.actif)
    ).all()
    entrepots = session.exec(
        select(Entrepot).where(Entrepot.commercant_id == commercant_id, Entrepot.actif)
    ).all()

    for p in produits:
        for e in entrepots:
            stock = stock_produit_entrepot(session, p.id, e.id)
            if stock < p.stock_minimal or stock < Decimal("0"):
                alertes.append({
                    "type": "negatif" if stock < Decimal("0") else "sous_seuil",
                    "produit_id": p.id,
                    "produit_sku": p.sku,
                    "produit_libelle": p.libelle,
                    "entrepot_id": e.id,
                    "entrepot_nom": e.nom,
                    "stock": str(stock),
                    "seuil_min": str(p.stock_minimal),
                })

    peremption_limite = datetime.now(UTC).date() + timedelta(days=jours_peremption)
    mouvements_perimant = session.exec(
        select(MouvementStock).where(
            MouvementStock.commercant_id == commercant_id,
            MouvementStock.date_peremption is not None,
            MouvementStock.date_peremption <= peremption_limite,
        )
    ).all()
    for m in mouvements_perimant:
        produit = session.get(Produit, m.produit_id)
        entrepot = session.get(Entrepot, m.entrepot_id)
        alertes.append({
            "type": "peremption",
            "produit_id": m.produit_id,
            "produit_sku": produit.sku if produit else None,
            "produit_libelle": produit.libelle if produit else None,
            "entrepot_id": m.entrepot_id,
            "entrepot_nom": entrepot.nom if entrepot else None,
            "date_peremption": m.date_peremption.isoformat(),
            "quantite": str(m.quantite),
        })

    return alertes
