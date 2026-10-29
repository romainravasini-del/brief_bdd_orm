# 🎓 CF-Tech ERP — Base de Données & ORM

**Projet Data Engineering réalisé par Oussama, Xavier & Romain**

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![SQLModel](https://img.shields.io/badge/ORM-SQLModel-red)
![Pydantic](https://img.shields.io/badge/Validation-Pydantic-green)
![Alembic](https://img.shields.io/badge/Migrations-Alembic-orange)
![Flask](https://img.shields.io/badge/Web-Flask-black)

---

## 🎯 Objectif du Projet
Remplacer la gestion manuelle (Excel / ancien ERP) du centre de formation **CF-Tech** par une base relationnelle centralisée en Python :
- **Modélisation ORM (`SQLModel`) :** 7 tables avec héritage (`UserBase`) pour gérer les *Apprenants, Formateurs, Staff, Admins, Salles, Sessions* et *Inscriptions*.
- **Validation stricte (`Pydantic`) :** Emails valides (`EmailStr`), âge $\ge$ 16 ans, téléphone (Regex), taux horaire $\ge 0$ et dates cohérentes (`date_debut < date_fin`).
- **Règles Métier (`auth/`) :** Anti-chevauchement horaire des salles et apprenants (`is_salle_disponible`), respect des capacités max et gestion des droits (`check_permission`).
- **Migrations (`Alembic`) :** Évolution versionnée du schéma (tables initiales $\rightarrow$ statut session $\rightarrow$ équipements JSON salle $\rightarrow$ rôle `SUPERADMIN`).
- **Interface Web (`Flask`) :** Dashboard, gestion CRUD des utilisateurs, planification des sessions et inscriptions.

---

## 🚀 Installation & Lancement

```bash
# 1. Activer l'environnement virtuel et installer les paquets
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Appliquer les migrations Alembic
alembic upgrade head

# 3. Lancer l'application Flask (http://127.0.0.1:5000)
python -m app.app_flask
```

---

## 🗂️ Structure du Projet

```text
brief_bdd_orm/
├── alembic/                  # Scripts de migrations (versions/) et configuration env.py
├── app/
│   ├── auth/                 # permissions.py (droits) & validators.py (anti-chevauchement)
│   ├── models/               # Tables SQLModel (users.py, salles.py, sessions.py, inscriptions.py)
│   ├── schemas/              # Validations Pydantic (users_schemas.py, sessions_schemas.py...)
│   ├── templates/            # Pages HTML Bootstrap (index.html, users.html, sessions.html)
│   ├── app_flask.py          # Serveur Web Flask
│   └── database.py           # Connexion SQLModel (Engine & Session)
├── .env                      # DATABASE_URL="sqlite:///./cftech.db"
└── requirements.txt          # Dépendances Python
```

---

## 📐 Schémas d'Architecture (UML & Merise)

### 1. Schéma des Cas d'Utilisation

```mermaid
flowchart LR
    classDef actor fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e,font-weight:bold
    classDef uc fill:#eff6ff,stroke:#2563eb,stroke-width:1.5px,rx:20,ry:20,color:#1e3a8a

    APP["🧑‍🎓 Apprenant"]:::actor
    FORM["👨‍🏫 Formateur"]:::actor
    STAFF["📋 Staff Pédagogique"]:::actor
    ADM["👑 Admin / SuperAdmin"]:::actor

    subgraph SYSTEME ["🖥️ Plateforme CF-Tech"]
        direction TB

        subgraph G1 ["Espace Apprenant & Formateur"]
            U1(["Consulter le planning des sessions"]):::uc
            U2(["S'inscrire à une session ouverte"]):::uc
            U3(["Valider la présence (Appel)"]):::uc
        end

        subgraph G2 ["Espace Pédagogique (Staff)"]
            U4(["Créer et gérer les Salles"]):::uc
            U5(["Planifier une Session (sans conflit horaire)"]):::uc
            U6(["Consulter le Dashboard"]):::uc
        end

        subgraph G3 ["Espace Administration"]
            U7(["Gérer tous les Utilisateurs (CRUD)"]):::uc
            U8(["Gérer les Rôles & Migrations"]):::uc
        end
    end

    APP --> U1
    APP --> U2
    FORM --> U1
    FORM --> U3
    STAFF --> U4
    STAFF --> U5
    STAFF --> U6
    ADM --> U7
    ADM --> U8
    ADM -.->|"Possède aussi tous les droits Staff"| G2
```

### 2. MCD (Modèle Conceptuel de Données)

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

### 3. MLD (Modèle Logique de Données)

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