def test_create_commercant(client):
    response = client.post("/commercants/", json={
        "nom": "Boutique Alpha",
        "email": "contact@alpha.example",
        "telephone": "+33100000000",
        "adresse": "10 rue du Commerce, 75001 Paris",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Boutique Alpha"
    assert data["email"] == "contact@alpha.example"


def test_list_commercants(client, commercant):
    response = client.get("/commercants/")
    assert response.status_code == 200
    data = response.json()
    assert any(c["id"] == commercant["id"] for c in data)


def test_get_commercant(client, commercant):
    response = client.get(f"/commercants/{commercant['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == commercant["id"]


def test_update_commercant(client, commercant):
    response = client.patch(f"/commercants/{commercant['id']}", json={
        "telephone": "+33111111111",
    })
    assert response.status_code == 200
    assert response.json()["telephone"] == "+33111111111"


def test_delete_commercant(client, commercant):
    response = client.delete(f"/commercants/{commercant['id']}")
    assert response.status_code == 204
    response = client.get(f"/commercants/{commercant['id']}")
    assert response.status_code == 200
    assert response.json()["actif"] is False
