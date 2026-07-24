def test_creer_commande(client, commercant, produit, entrepot):
    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "fournisseur_contact": "contact@fournisseur.cn",
            "quantite_commandee": "100.00",
            "prix_unitaire_prevu": "50.00",
            "date_livraison_estimee": "2026-08-15",
            "reference_commande": "CMD-2026-001",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["statut"] == "brouillon"
    assert data["quantite_commandee"] == "100.00"


def test_modifier_commande_brouillon(client, commercant, produit, entrepot):
    cmd = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "100.00",
        },
    ).json()
    response = client.patch(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}",
        headers={"X-API-Key": commercant["api_key"]},
        json={"quantite_commandee": "150.00"},
    )
    assert response.status_code == 200
    assert response.json()["quantite_commandee"] == "150.00"


def test_envoyer_commande(client, commercant, produit, entrepot):
    cmd = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "100.00",
        },
    ).json()
    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/envoyer",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "envoyee"


def test_receptionner_commande_cree_mouvement(client, commercant, produit, entrepot):
    cmd = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "100.00",
            "prix_unitaire_prevu": "50.00",
        },
    ).json()
    client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/envoyer",
        headers={"X-API-Key": commercant["api_key"]},
    )
    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/receptionner",
        headers={"X-API-Key": commercant["api_key"]},
        json={"quantite": "40.00"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["commande"]["statut"] == "partiellement_recue"
    assert data["commande"]["quantite_recue"] == "40.00"
    assert data["mouvement_id"] > 0

    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/receptionner",
        headers={"X-API-Key": commercant["api_key"]},
        json={"quantite": "60.00"},
    )
    assert response.status_code == 200
    assert response.json()["commande"]["statut"] == "recue"
    assert response.json()["commande"]["quantite_recue"] == "100.00"


def test_reception_trop_elevee_refusee(client, commercant, produit, entrepot):
    cmd = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "100.00",
        },
    ).json()
    client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/envoyer",
        headers={"X-API-Key": commercant["api_key"]},
    )
    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/receptionner",
        headers={"X-API-Key": commercant["api_key"]},
        json={"quantite": "120.00"},
    )
    assert response.status_code == 400


def test_employe_ne_peut_pas_creer_commande(client, employe, produit, entrepot):
    response = client.post(
        f"/commercants/{employe['commercant_id']}/commandes-fournisseurs",
        headers={"X-API-Key": employe["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "10.00",
        },
    )
    assert response.status_code == 403


def test_annuler_commande(client, commercant, produit, entrepot):
    cmd = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "produit_id": produit["id"],
            "entrepot_destination_id": entrepot["id"],
            "fournisseur_nom": "Fournisseur Chine",
            "quantite_commandee": "100.00",
        },
    ).json()
    response = client.post(
        f"/commercants/{commercant['id']}/commandes-fournisseurs/{cmd['id']}/annuler",
        headers={"X-API-Key": commercant["api_key"]},
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"
