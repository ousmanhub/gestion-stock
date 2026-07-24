import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from gestion_stock.database import get_session
from gestion_stock.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="commercant")
def commercant_fixture(client):
    response = client.post("/commercants/", json={
        "nom": "Boutique Test",
        "email": "test@example.com",
        "telephone": "+33100000000",
        "adresse": "10 rue du Test, 75001 Paris",
    })
    return response.json()


@pytest.fixture(name="produit")
def produit_fixture(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/produits/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "sku": "SKU-TEST-001",
            "libelle": "Réfrigérateur 300L",
            "categorie": "Électroménager",
            "unite": "pièce",
            "prix_unitaire": "350.00",
            "stock_minimal": "5.00",
        },
    )
    return response.json()


@pytest.fixture(name="entrepot")
def entrepot_fixture(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/entrepots/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "nom": "Entrepôt Test",
            "adresse": "12 avenue de la division Leclerc, 93700 Drancy",
            "contact": "logistique@test.com",
        },
    )
    return response.json()


@pytest.fixture(name="entrepot_dest")
def entrepot_dest_fixture(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/entrepots/",
        headers={"X-API-Key": commercant["api_key"]},
        json={
            "nom": "Entrepôt Destination",
            "adresse": "20 rue de la Livraison, 75002 Paris",
            "contact": "dest@test.com",
        },
    )
    return response.json()


@pytest.fixture(name="employe")
def employe_fixture(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/utilisateurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={"nom": "Employé Test", "email": "emp@test.com", "role": "employe"},
    )
    return response.json()


@pytest.fixture(name="responsable")
def responsable_fixture(client, commercant):
    response = client.post(
        f"/commercants/{commercant['id']}/utilisateurs",
        headers={"X-API-Key": commercant["api_key"]},
        json={"nom": "Responsable Test", "email": "resp@test.com", "role": "responsable_logistique"},
    )
    return response.json()
