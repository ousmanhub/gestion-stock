def test_create_entrepot(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/entrepots/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "nom": "Entrepôt Drancy",
            "adresse": "12 avenue de la division Leclerc, 93700 Drancy",
            "contact": "logistique@example.com",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Entrepôt Drancy"
    assert data["commercant_id"] == commercant["id"]


def test_list_entrepots(client, commercant, entrepot):
    response = client.get(
        f"/commercants/{commercant['id']}/entrepots/",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert any(e["id"] == entrepot["id"] for e in data)


def test_get_entrepot(client, commercant, entrepot):
    response = client.get(
        f"/commercants/{commercant['id']}/entrepots/{entrepot['id']}",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["id"] == entrepot["id"]


def test_update_entrepot(client, commercant, entrepot):
    response = client.patch(
        f"/commercants/{commercant['id']}/entrepots/{entrepot['id']}",
        headers={"X-API-Key": commercant["api_key"]},
        json={"contact": "new@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["contact"] == "new@example.com"


def test_delete_entrepot(client, commercant, entrepot):
    response = client.delete(
        f"/commercants/{commercant['id']}/entrepots/{entrepot['id']}",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 204
    response = client.get(
        f"/commercants/{commercant['id']}/entrepots/{entrepot['id']}",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 404
