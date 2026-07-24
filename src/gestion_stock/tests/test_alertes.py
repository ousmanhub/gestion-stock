def test_alerte_stock_negatif(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "sortie",
            "quantite": "25.00",
        },
    )
    response = client.get(
        f"/commercants/{commercant['id']}/alertes/",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert any(a["type"] == "negatif" for a in data)


def test_alerte_resume(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "sortie",
            "quantite": "25.00",
        },
    )
    response = client.get(
        f"/commercants/{commercant['id']}/alertes/resume",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_alertes"] >= 1


def test_employe_peut_voir_alertes(client, employe, produit, entrepot):
    response = client.get(
        f"/commercants/{employe['commercant_id']}/alertes/",
        headers={"X-API-Key": employe["api_key"]},
    )
    assert response.status_code == 200
