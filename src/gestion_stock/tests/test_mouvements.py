def test_mouvement_entree(client, commercant, produit, entrepot):
    response = client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "20.00",
            "prix_unitaire_mouvement": "150.00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type_mouvement"] == "entree"
    assert data["stock_apres"] == "20.00"


def test_mouvement_sortie_negatif_autorise(client, commercant, produit, entrepot):
    response = client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "sortie",
            "quantite": "25.00",
        },
    )
    assert response.status_code == 201
    assert response.json()["stock_apres"] == "-25.00"


def test_list_mouvements(client, commercant, produit, entrepot):
    client.post(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "10.00",
        },
    )
    response = client.get(
        f"/commercants/{commercant['id']}/mouvements/",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_employe_peut_creer_mouvement(client, employe, produit, entrepot):
    response = client.post(
        f"/commercants/{employe['commercant_id']}/mouvements/",
        headers={"X-API-Key": employe["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_id": entrepot["id"],
            "type_mouvement": "entree",
            "quantite": "5.00",
        },
    )
    assert response.status_code == 201


def test_employe_ne_peut_pas_creer_produit(client, employe, produit):
    response = client.post(
        f"/commercants/{employe['commercant_id']}/produits/",
        headers={"X-API-Key": employe["api_key"]},
        json={"sku": "EMP-001", "libelle": "Test"},
    )
    assert response.status_code == 403
