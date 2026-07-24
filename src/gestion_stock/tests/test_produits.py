def test_create_produit(client, commercant):
    response = client.post(f"/commercants/{commercant['id']}/produits/", json={
        "sku": "SKU-001",
        "libelle": "Réfrigérateur 300L",
        "categorie": "Électroménager",
        "unite": "pièce",
        "prix_unitaire": "350.00",
        "stock_minimal": "5.00",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["commercant_id"] == commercant["id"]


def test_duplicate_sku_same_commercant(client, commercant, produit):
    response = client.post(f"/commercants/{commercant['id']}/produits/", json={
        "sku": produit["sku"],
        "libelle": "Autre",
    })
    assert response.status_code == 400


def test_list_produits(client, commercant, produit):
    response = client.get(f"/commercants/{commercant['id']}/produits/")
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == produit["id"] for p in data)


def test_get_produit(client, commercant, produit):
    response = client.get(f"/commercants/{commercant['id']}/produits/{produit['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == produit["id"]


def test_update_produit(client, commercant, produit):
    response = client.patch(f"/commercants/{commercant['id']}/produits/{produit['id']}", json={
        "stock_minimal": "10.00",
    })
    assert response.status_code == 200
    assert response.json()["stock_minimal"] == "10.00"


def test_delete_produit(client, commercant, produit):
    response = client.delete(f"/commercants/{commercant['id']}/produits/{produit['id']}")
    assert response.status_code == 204
    response = client.get(f"/commercants/{commercant['id']}/produits/{produit['id']}")
    assert response.status_code == 404
