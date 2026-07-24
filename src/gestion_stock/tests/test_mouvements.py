def test_mouvement_entree(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "entree",
        "quantite": "20.00",
        "prix_unitaire_mouvement": "15.00",
        "reference_document": "RC-001",
        "date_peremption": "2027-01-01",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["stock_avant"] == "0.00"
    assert data["stock_apres"] == "20.00"
    assert data["date_peremption"] == "2027-01-01"


def test_mouvement_sortie_autorise_stock_negatif(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "sortie",
        "quantite": "5.00",
        "reference_document": "BL-001",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["stock_avant"] == "0.00"
    assert data["stock_apres"] == "-5.00"


def test_mouvement_ajustement(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "ajustement",
        "quantite": "12.00",
        "reference_document": "INV-001",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["stock_avant"] == "0.00"
    assert data["stock_apres"] == "12.00"
    assert data["quantite"] == "12.00"


def test_mouvement_transfert_refuse(client, commercant, produit, entrepot):
    response = client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "transfert_sortie",
        "quantite": "1.00",
    })
    assert response.status_code == 400


def test_list_mouvements_filter(client, commercant, produit, entrepot):
    client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "entree",
        "quantite": "3.00",
    })
    response = client.get(f"/commercants/{commercant['id']}/mouvements/?produit_id={produit['id']}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
