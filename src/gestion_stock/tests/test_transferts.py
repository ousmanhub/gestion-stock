def test_transfert_entre_entrepots(client, commercant, produit, entrepot, entrepot_dest):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "50.00",
        },
    )
    response = client.post(
        f"/commercants/{commercant['id']}/transferts/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_source_id": entrepot["id"],
            "entrepot_destination_id": entrepot_dest["id"],
            "quantite": "10.00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_stock_apres"] == "40.00"
    assert data["destination_stock_apres"] == "10.00"


def test_employe_peut_creer_transfert(client, employe, produit, entrepot, entrepot_dest):
    response = client.post(
        f"/commercants/{employe['commercant_id']}/transferts/",
        headers={"X-API-Key": employe["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_source_id": entrepot["id"],
            "entrepot_destination_id": entrepot_dest["id"],
            "quantite": "1.00",
        },
    )
    assert response.status_code == 201


def test_transfert_meme_entrepot_refuse(client, commercant, produit, entrepot):
    response = client.post(
        f"/commercants/{commercant['id']}/transferts/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_source_id": entrepot["id"],
            "entrepot_destination_id": entrepot["id"],
            "quantite": "5.00",
        },
    )
    assert response.status_code == 400
