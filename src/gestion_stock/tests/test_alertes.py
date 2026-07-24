def test_alerte_stock_negatif(client, commercant, produit, entrepot):
    client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "sortie",
        "quantite": "3.00",
    })
    response = client.get(f"/commercants/{commercant['id']}/alertes/")
    assert response.status_code == 200
    alertes = response.json()
    assert any(a["type"] == "negatif" and a["stock"] == "-3.00" for a in alertes)


def test_alerte_sous_seuil(client, commercant, produit, entrepot):
    # produit a stock_minimal = 5
    client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "entree",
        "quantite": "3.00",
    })
    response = client.get(f"/commercants/{commercant['id']}/alertes/")
    assert response.status_code == 200
    alertes = response.json()
    assert any(a["type"] == "sous_seuil" and a["stock"] == "3.00" for a in alertes)


def test_alerte_peremption(client, commercant, produit, entrepot):
    client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "entree",
        "quantite": "5.00",
        "date_peremption": "2026-08-01",
    })
    response = client.get(f"/commercants/{commercant['id']}/alertes/?jours_peremption=60")
    assert response.status_code == 200
    alertes = response.json()
    assert any(a["type"] == "peremption" for a in alertes)


def test_resume_alertes(client, commercant, produit, entrepot):
    client.post(f"/commercants/{commercant['id']}/mouvements/", json={
        "produit_id": produit["id"],
        "entrepot_id": entrepot["id"],
        "type_mouvement": "sortie",
        "quantite": "1.00",
    })
    response = client.get(f"/commercants/{commercant['id']}/alertes/resume")
    assert response.status_code == 200
    data = response.json()
    assert data["total_alertes"] >= 1
    assert data["stocks_negatifs"] >= 1
