from gestion_stock.services.stock import stock_disponible


def test_creer_reservation(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
        },
    )
    response = client.post(
        f"/commercants/{commercant['id']}/reservations/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "10.00",
            "reference_client": "Client A",
            "reference_dossier": "DOSSIER-123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["statut"] == "en_cours"
    assert data["quantite"] == "10.00"


def test_reservation_refusee_si_stock_insuffisant(client, commercant, produit, entrepot):
    response = client.post(
        f"/commercants/{commercant['id']}/reservations/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "10.00",
        },
    )
    assert response.status_code == 400


def test_stock_disponible_apres_reservation(client, commercant, produit, entrepot, session):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
        },
    )
    assert stock_disponible(session, produit["id"], entrepot["id"]) == 20
    client.post(
        f"/commercants/{commercant['id']}/reservations/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "8.00",
        },
    )
    assert stock_disponible(session, produit["id"], entrepot["id"]) == 12


def test_honorer_reservation_via_sortie(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
        },
    )
    res = client.post(
        f"/commercants/{commercant['id']}/reservations/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "10.00",
        },
    ).json()
    response = client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "sortie",
            "quantite": "10.00",
            "reservation_id": res["id"],
        },
    )
    assert response.status_code == 201

    detail = client.get(
        f"/commercants/{commercant['id']}/reservations/{res['id']}",
        headers={"X-API-Key": commercant["api_key"]},
    ).json()
    assert detail["statut"] == "honoree"
    assert detail["quantite_honoree"] == "10.00"


def test_annuler_reservation(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
        },
    )
    res = client.post(
        f"/commercants/{commercant['id']}/reservations/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "5.00",
        },
    ).json()
    response = client.post(
        f"/commercants/{commercant['id']}/reservations/{res['id']}/annuler",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"


def test_employe_ne_peut_pas_annuler(client, employe, produit, entrepot):
    client.post(
        f"/commercants/{employe['commercant_id']}/mouvements/",
        headers={"X-API-Key": employe["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
        },
    )
    res = client.post(
        f"/commercants/{employe['commercant_id']}/reservations/",
        headers={"X-API-Key": employe["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "quantite": "5.00",
        },
    ).json()
    response = client.post(
        f"/commercants/{employe['commercant_id']}/reservations/{res['id']}/annuler",
        headers={"X-API-Key": employe["api_key"]},
    )
    assert response.status_code == 403
