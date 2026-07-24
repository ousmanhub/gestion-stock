def test_sans_api_key_refuse(client, commercant):
    response = client.get(f"/commercants/{commercant['id']}/produits/")
    assert response.status_code == 401


def test_acces_tenant_etranger_refuse(client, commercant):
    autre = client.post("/commercants/", json={"nom": "Autre"}).json()
    response = client.get(
        f"/commercants/{autre['id']}/produits/",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 403


def test_employe_ne_peut_pas_modifier_produit(client, employe, produit):
    response = client.patch(
        f"/commercants/{employe['commercant_id']}/produits/{produit['id']}",
        headers={"X-API-Key": employe["api_key"]},
        json={"stock_minimal": "1.00"},
    )
    assert response.status_code == 403


def test_responsable_peut_creer_produit(client, responsable, produit):
    response = client.post(
        f"/commercants/{responsable['commercant_id']}/produits/",
        headers={"X-API-Key": responsable["api_key"]},
        json={"sku": "RESP-001", "libelle": "Produit resp", "prix_unitaire": "10.00"},
    )
    assert response.status_code == 201


def test_responsable_peut_voir_alertes(client, responsable, produit, entrepot):
    response = client.get(
        f"/commercants/{responsable['commercant_id']}/alertes/",
        headers={"X-API-Key": responsable["api_key"]},
    )
    assert response.status_code == 200
