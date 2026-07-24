def test_transfert_entre_entrepots(client, commercant, produit, entrepot, entrepot_dest):
    response = client.post(f"/commercants/{commercant['id']}/transferts/", json={
        "produit_id": produit["id"],
        "entrepot_source_id": entrepot["id"],
        "entrepot_destination_id": entrepot_dest["id"],
        "quantite": "10.00",
        "reference_document": "BT-001",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["source_stock_apres"] == "-10.00"
    assert data["destination_stock_apres"] == "10.00"


def test_transfert_meme_entrepot_refuse(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/transferts/", json={
        "produit_id": produit["id"],
        "entrepot_source_id": entrepot["id"],
        "entrepot_destination_id": entrepot["id"],
        "quantite": "5.00",
    })
    assert response.status_code == 400
