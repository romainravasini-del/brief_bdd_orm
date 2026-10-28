# brief_bdd_orm
Brief base de donnée en ORM de Oussama Xavier et Romain

MLD

```mermaid
flowchart TB

    APPRENANTS["apprenants
    ──────────────
    id : integer (PK)
    nom : varchar(50)
    prenom : varchar(50)
    email : varchar(255) (UK)
    date_creation : datetime
    is_active : boolean
    role : varchar(50)
    date_naissance : date
    niveau_etude : varchar(50)
    telephone : varchar(20)
    date_inscription_plateforme : datetime"]

    FORMATEURS["formateurs
    ──────────────
    id : integer (PK)
    nom : varchar(50)
    prenom : varchar(50)
    email : varchar(255) (UK)
    date_creation : datetime
    is_active : boolean
    role : varchar(50)
    specialite : varchar(100)
    date_embauche : date
    taux_horaire : float
    bio : text"]

    STAFF["staff_pedagogiques
    ──────────────
    id : integer (PK)
    nom : varchar(50)
    prenom : varchar(50)
    email : varchar(255) (UK)
    date_creation : datetime
    is_active : boolean
    role : varchar(50)
    poste : varchar(100)
    date_prise_fonction : date
    responsabilites : text"]

    ADMINS["admins
    ──────────────
    id : integer (PK)
    nom : varchar(50)
    prenom : varchar(50)
    email : varchar(255) (UK)
    date_creation : datetime
    is_active : boolean
    role : varchar(50)
    niveau_acces : varchar(50)
    date_promotion : date"]

    SALLES["salles
    ──────────────
    id : integer (PK)
    nom : varchar(50) (UK)
    capacite : integer
    localisation : varchar(150)
    equipements : text
    is_active : boolean"]

    SESSIONS["sessions
    ──────────────
    id : integer (PK)
    titre : varchar(100)
    description : text
    date_debut : datetime
    date_fin : datetime
    #salle_id : integer (FK)
    #formateur_id : integer (FK)
    capacite_max : integer
    statut : varchar(50)
    prerequis : text"]

    INSCRIPTIONS["inscriptions
    ──────────────
    id : integer (PK)
    #apprenant_id : integer (FK)
    #session_id : integer (FK)
    date_inscription : datetime
    statut_inscription : varchar(50)
    presence : boolean"]

    SESSIONS -->|"salle_id > id"| SALLES
    SESSIONS -->|"formateur_id > id"| FORMATEURS
    INSCRIPTIONS -->|"apprenant_id > id"| APPRENANTS
    INSCRIPTIONS -->|"session_id > id"| SESSIONS
```

MCD

```mermaid
flowchart TB

    USER["UTILISATEUR
    ──────────────
    id_utilisateur (PK)
    nom
    prenom
    email
    date_creation
    is_active
    role"]

    HERITAGE{"Héritage (XT)"}

    APPRENANT["APPRENANT
    ──────────────
    date_naissance
    niveau_etude
    telephone
    date_inscription_plateforme
    certification_obtenue"]

    FORMATEUR["FORMATEUR
    ──────────────
    specialite
    date_embauche
    taux_horaire
    bio"]

    STAFF["STAFF_PEDAGOGIQUE
    ──────────────
    poste
    date_prise_fonction
    responsabilites"]

    ADMIN["ADMIN
    ──────────────
    niveau_acces
    date_promotion"]

    SALLE["SALLE
    ──────────────
    id_salle (PK)
    nom
    capacite
    localisation
    equipements
    is_active"]

    SESSION["SESSION
    ──────────────
    id_session (PK)
    titre
    description
    date_debut
    date_fin
    capacite_max
    statut
    prerequis"]

    ASSOC_INSCRIRE(["S'INSCRIRE
    ──────────────
    date_inscription
    statut_inscription
    presence"])

    ASSOC_ANIMER(["ANIMER"])
    ASSOC_SE_DEROULER(["SE DÉROULER"])

    USER --- HERITAGE
    HERITAGE --> APPRENANT
    HERITAGE --> FORMATEUR
    HERITAGE --> STAFF
    HERITAGE --> ADMIN

    APPRENANT ---|"0,n"| ASSOC_INSCRIRE
    ASSOC_INSCRIRE ---|"0,n"| SESSION

    FORMATEUR ---|"0,n"| ASSOC_ANIMER
    ASSOC_ANIMER ---|"1,1"| SESSION

    SALLE ---|"0,n"| ASSOC_SE_DEROULER
    ASSOC_SE_DEROULER ---|"1,1"| SESSION
```

from sqlmodel import Session, select, func
from models.inscriptions import Inscription, StatutInscriptionEnum
from models.sessions import SessionFormation
from schemas.inscriptions_schemas import InscriptionCreate


class ChevauchementSessionError(Exception):
    """L'apprenant est déjà inscrit à une session qui se chevauche."""


class SessionPleineError(Exception):
    """La session a atteint sa capacité maximale."""


def inscrire_apprenant(db: Session, data: InscriptionCreate) -> Inscription:
    nouvelle = db.get(SessionFormation, data.session_id)
    if nouvelle is None:
        raise ValueError(f"Session {data.session_id} introuvable")

    # Capa
    nb_inscrits = db.exec(
        select(func.count())
        .select_from(Inscription)
        .where(
            Inscription.session_id == data.session_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
        )
    ).one()

    if nb_inscrits >= nouvelle.capacite_max:
        raise SessionPleineError(
            f"Session « {nouvelle.titre} » pleine ({nb_inscrits}/{nouvelle.capacite_max})"
        )

    # Chevauch
    conflit = db.exec(
        select(SessionFormation)
        .join(Inscription, Inscription.session_id == SessionFormation.id)
        .where(
            Inscription.apprenant_id == data.apprenant_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
            SessionFormation.date_debut < nouvelle.date_fin,
            SessionFormation.date_fin > nouvelle.date_debut,
        )
    ).first()

    if conflit:
        raise ChevauchementSessionError(
            f"Chevauchement avec la session « {conflit.titre} »"
        )

    # Enregistrement
    inscription = Inscription(apprenant_id=data.apprenant_id, session_id=data.session_id)
    db.add(inscription)
    db.commit()
    db.refresh(inscription)
    return inscription