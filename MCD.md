---
config:
  theme: dark
---
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