from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel


class TypeMouvement(StrEnum):
    ENTREE = "entree"
    SORTIE = "sortie"
    AJUSTEMENT = "ajustement"
    TRANSFERT_SORTIE = "transfert_sortie"
    TRANSFERT_ENTREE = "transfert_entree"


class RoleUtilisateur(StrEnum):
    COMMERCANT = "commercant"
    RESPONSABLE_LOGISTIQUE = "responsable_logistique"
    EMPLOYE = "employe"


class Commercant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    email: str | None = None
    telephone: str | None = None
    adresse: str | None = None
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Utilisateur(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    nom: str
    email: str | None = None
    role: RoleUtilisateur
    api_key: str = Field(index=True, unique=True)
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Produit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    sku: str = Field(index=True)
    libelle: str
    categorie: str | None = None
    unite: str = "unité"
    prix_unitaire: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    stock_minimal: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        unique_together = ("commercant_id", "sku")


class Entrepot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    nom: str
    adresse: str | None = None
    contact: str | None = None
    actif: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MouvementStock(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    commercant_id: int = Field(foreign_key="commercant.id", index=True)
    produit_id: int = Field(foreign_key="produit.id", index=True)
    entrepot_id: int = Field(foreign_key="entrepot.id", index=True)
    entrepot_destination_id: int | None = Field(default=None, foreign_key="entrepot.id", index=True)
    type_mouvement: TypeMouvement
    quantite: Decimal = Field(max_digits=12, decimal_places=2)
    prix_unitaire_mouvement: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    date_peremption: date | None = None
    reference_document: str | None = None
    notes: str | None = None
    date_mouvement: datetime = Field(default_factory=datetime.utcnow, index=True)
