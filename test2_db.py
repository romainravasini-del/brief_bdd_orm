import os
import random
import shutil
import sqlite3
from datetime import date, datetime, timedelta, timezone
from sqlmodel import Session, delete

from app.database import engine, create_db_and_tables
from app.models.users import (
    Apprenant,
    Formateur,
    StaffPedagogique,
    Admin,
    NiveauAccesEnum,
)
from app.models.salles import Salle
from app.models.sessions import SessionFormation, StatutSessionEnum
from app.models.inscriptions import Inscription
from app.schemas.users_schemas import (
    ApprenantCreate,
    FormateurCreate,
    StaffCreate,
    AdminCreate,
)
from app.schemas.sessions_schemas import SalleCreate, SessionCreate
from app.schemas.inscriptions_schemas import InscriptionCreate
from app.auth.validators import (
    is_salle_disponible,
    inscrire_apprenant,
    ChevauchementSessionError,
    SessionPleineError,
)


PRENOMS = [
    "Lucas", "Emma", "Hugo", "Chloé", "Nathan", "Léa", "Maxime", "Manon",
    "Antoine", "Camille", "Yanis", "Inès", "Théo", "Clara", "Enzo", "Sarah",
    "Alexandre", "Juliette", "Tom", "Marie", "Nicolas", "océane", "Gabriel", "Eva",
    "Arthur", "Romane", "Louis", "Anaïs", "Jules", "Lucie", "Mathis", " Pauline",
    "Raphaël", "Laura", "Paul", "Célia", "Baptiste", "Margaux", "Mehdi", "Yasmine",
    "Sofiane", "Amel", "Karim", "Nadia", "Rayan", "Lina", "Sami", "farah",
    "Quentin", "Charlotte",
]

NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
    "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David",
    "Bertrand", "Morel", "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine",
    "Rousseau", "Vincent", "Muller", "Lefevre", "Faure", "Andre", "Mercier", "Blanc",
    "Guerin", "Boyer", "Garnier", "Chevalier", "Francois", "Legrand", "Gauthier", "Garcia",
    "Perrin", "Robin", "Clement", "Morin", "Nicolas", "Henry", "Roussel", "Mathieu",
    "Gautier", "Masson",
]

NIVEAUX_ETUDE = [
    "Bac Général (Spé NSI)",
    "Bac+2 BTS SIO",
    "Bac+2 BTS CIEL",
    "Bac+3 BUT Informatique",
    "Bac+3 BUT Science des Données",
    "Bac+3 Licence Informatique",
    "Bac+4 Master 1 MIAGE",
    "Bac+5 Master Data Engineering",
    "Bac+5 École d'Ingénieurs",
    "Reconversion Professionnelle",
]

CERTIFICATIONS = [
    None,
    None,
    "PCAP Certified Associate in Python",
    "AWS Certified Cloud Practitioner",
    "Azure Data Fundamentals (DP-900)",
    "RNCP Niveau 6 - Concepteur Développeur",
    "Linux Professional Institute (LPIC-1)",
    "GitLab Certified Associate",
    "PostgreSQL Associate Certification",
    "Cisco CCNA",
]

SPECIALITES_FORMATEURS = [
    ("Python Avancé & SQLModel", "Architecte logiciel Python avec 12 ans d'expérience en Data Engineering.", 75.0),
    ("Bases de Données SQL & Alembic", "DBA PostgreSQL / SQLite spécialisée dans la modélisation MCD/MLD et les migrations.", 70.0),
    ("Data Science & Machine Learning", "Lead Data Scientist passionné par l'IA générative et l'analyse prédictive.", 85.0),
    ("Développement Web Flask & FastAPI", "Développeuse Fullstack spécialisée dans les API REST et architectures micro-services.", 68.0),
    ("DevOps, Docker & Kubernetes", "Ingénieur Cloud & DevOps certifié CKA et automatisation Linux.", 80.0),
    ("Cybersécurité & Pentesting", "Auditeur sécurité offensive (OSCP) et protection des infrastructures critiques.", 90.0),
    ("Data Engineering & Apache Spark", "Spécialiste des pipelines ETL distribués, Kafka et Airflow.", 82.0),
    ("Administration Réseaux & Cisco", "Ingénieur réseau senior spécialisé en routage BGP, VLAN et pare-feux.", 65.0),
    ("Business Intelligence & PowerBI", "Consultante BI experte en modélisation décisionnelle et DAX.", 62.0),
    ("Cloud Architecture AWS & Terraform", "Solutions Architect accompagnant les migrations Infrastructure-as-Code.", 88.0),
]


def generer_base_presentation():
    """
    Générateur officiel à grand volume de la base de données CF-Tech pour la soutenance.
    Utilise EXCLUSIVEMENT les vrais modèles SQLModel (app/models/) et
    les vrais schémas Pydantic (app/schemas/).
    """
    random.seed(42)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    src_db = os.path.join(base_dir, "cftech.db")

    # 0. Supprimer les anciennes tables parasites au singulier si elles existent
    if os.path.exists(src_db):
        conn = sqlite3.connect(src_db)
        for old_tbl in ("salle", "apprenant", "formateur", "staff_pedagogique", "admin", "session", "inscription"):
            conn.execute(f"DROP TABLE IF EXISTS {old_tbl}")
        conn.commit()
        conn.close()

    print("🚀 1. Recréation des tables initiales (V1 sans statut/equipements/SUPERADMIN) dans cftech.db...")
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()

    with Session(engine) as db:
        # =====================================================================
        # A. ADMINS (8 Admins - Table : admins - sans SUPERADMIN en V1)
        # =====================================================================
        print("👑 2. Insertion de 8 Administrateurs (ADMIN_STANDARD / ADMIN_RESEAU)...")
        admins_data = [
            ("Dupont", "Romain", "romain.admin@cftech.fr", NiveauAccesEnum.ADMIN_STANDARD, date(2022, 9, 1)),
            ("Martin", "Xavier", "xavier.reseau@cftech.fr", NiveauAccesEnum.ADMIN_RESEAU, date(2023, 1, 15)),
            ("Benali", "Oussama", "oussama.admin@cftech.fr", NiveauAccesEnum.ADMIN_STANDARD, date(2023, 3, 10)),
            ("Moreau", "Hélène", "helene.moreau@cftech.fr", NiveauAccesEnum.ADMIN_STANDARD, date(2021, 6, 1)),
            ("Legrand", "Stéphane", "stephane.legrand@cftech.fr", NiveauAccesEnum.ADMIN_RESEAU, date(2023, 9, 12)),
            ("Garnier", "Céline", "celine.garnier@cftech.fr", NiveauAccesEnum.ADMIN_STANDARD, date(2024, 1, 20)),
            ("Chevalier", "Marc", "marc.chevalier@cftech.fr", NiveauAccesEnum.ADMIN_RESEAU, date(2024, 4, 5)),
            ("Perrin", "Sonia", "sonia.perrin@cftech.fr", NiveauAccesEnum.ADMIN_STANDARD, date(2024, 6, 18)),
        ]
        for nom, prenom, email, acces, dt_promo in admins_data:
            schema = AdminCreate(
                nom=nom,
                prenom=prenom,
                email=email,
                niveau_acces=acces,
                date_promotion=dt_promo,
            )
            db.add(Admin(**schema.model_dump()))
        db.commit()

        # =====================================================================
        # B. STAFF PÉDAGOGIQUE (10 Staffs - Table : staff_pedagogiques)
        # =====================================================================
        print("🗂️  3. Insertion de 10 membres du Staff Pédagogique...")
        staffs_data = [
            ("Moreau", "Claire", "claire.moreau@cftech.fr", "Directrice Pédagogique", date(2021, 9, 1), ["Validation des programmes", "Supervision des formateurs", "Audit Qualiopi"]),
            ("Lefebvre", "Thomas", "thomas.lefebvre@cftech.fr", "Coordinateur Planning & Salles", date(2022, 5, 15), ["Affectation des salles", "Gestion des conflits horaires", "Suivi matériel"]),
            ("Garnier", "Sarah", "sarah.garnier@cftech.fr", "Chargée des Relations Entreprises", date(2023, 2, 1), ["Suivi alternance", "Placement des apprenants", "Forum entreprises"]),
            ("Blanc", "Julien", "julien.blanc@cftech.fr", "Responsable Pédagogique Pôle Data", date(2022, 10, 10), ["Suivi promo Data Engineer", "Jurys de certification RNCP", "Recrutement formateurs"]),
            ("Fontaine", "Aurélie", "aurelie.fontaine@cftech.fr", "Responsable Pédagogique Pôle Cyber", date(2023, 3, 20), ["Suivi promo Cybersécurité", "Organisation CTF", "Partenariats ANSSI"]),
            ("Roussel", "Damien", "damien.roussel@cftech.fr", "Gestionnaire Administratif & OPCO", date(2023, 7, 1), ["Dossiers de financement", "Feuilles d'émargement", "Facturation"]),
            ("Muller", "Élodie", "elodie.muller@cftech.fr", "Référente Handicap & Inclusion", date(2022, 11, 15), ["Aménagement des examens", "Accompagnement individuel", "Accessibilité salles"]),
            ("Faure", "Benoît", "benoit.faure@cftech.fr", "Coordinateur Pédagogique Cloud/DevOps", date(2024, 1, 8), ["Labs Cloud AWS/Azure", "Planning des soutenances", "Veille technologique"]),
            ("Gauthier", "Myriam", "myriam.gauthier@cftech.fr", "Chargée d'Admissions & Tests", date(2024, 2, 19), ["Entretiens de motivation", "Tests techniques d'entrée", "Inscriptions plateforme"]),
            ("Morin", "Vincent", "vincent.morin@cftech.fr", "Responsable Vie Étudiante & Campus", date(2023, 9, 4), ["Accueil des promotions", "Événements Tech & Meetups", "Gestion des badges"]),
        ]
        for nom, prenom, email, poste, dt_fonc, missions in staffs_data:
            schema = StaffCreate(
                nom=nom,
                prenom=prenom,
                email=email,
                poste=poste,
                date_prise_fonction=dt_fonc,
                responsabilites={"missions": missions},
            )
            db.add(StaffPedagogique(**schema.model_dump()))
        db.commit()

        # =====================================================================
        # C. FORMATEURS (20 Formateurs - Table : formateurs)
        # =====================================================================
        print("👨‍🏫 4. Insertion de 20 Formateurs...")
        formateurs_objs = []
        for i in range(20):
            nom = NOMS[(i * 3) % len(NOMS)]
            prenom = PRENOMS[(i * 2 + 1) % len(PRENOMS)].strip().capitalize()
            spec, bio, taux = SPECIALITES_FORMATEURS[i % len(SPECIALITES_FORMATEURS)]
            email = f"{prenom.lower()}.{nom.lower()}.form{i+1}@cftech.fr"
            for acc, sans in [("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"), ("ï", "i"), ("î", "i"), ("ô", "o"), ("ç", "c"), ("à", "a")]:
                email = email.replace(acc, sans)

            dt_embauche = date(2020 + (i % 5), ((i * 2) % 12) + 1, ((i * 3) % 25) + 1)
            schema = FormateurCreate(
                nom=nom,
                prenom=prenom,
                email=email,
                specialite=spec,
                date_embauche=dt_embauche,
                taux_horaire=taux + (i % 4) * 2.5,
                bio=bio,
            )
            obj = Formateur(**schema.model_dump())
            db.add(obj)
            formateurs_objs.append(obj)
        db.commit()
        for obj in formateurs_objs:
            db.refresh(obj)

        # =====================================================================
        # D. APPRENANTS (200 Apprenants - Table : apprenants)
        # =====================================================================
        print("🧑‍🎓 5. Insertion de 200 Apprenants...")
        apprenants_objs = []
        for i in range(1, 201):
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS).strip().capitalize()
            clean_p = prenom.lower()
            clean_n = nom.lower()
            for acc, sans in [("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"), ("ï", "i"), ("î", "i"), ("ô", "o"), ("ç", "c"), ("à", "a")]:
                clean_p = clean_p.replace(acc, sans)
                clean_n = clean_n.replace(acc, sans)

            email = f"{clean_p}.{clean_n}{i}@etu.cftech.fr"
            annee_naiss = random.randint(1988, 2006)
            mois_naiss = random.randint(1, 12)
            jour_naiss = random.randint(1, 28)
            tel = f"0{random.choice([6, 7])}{i:08d}"

            schema = ApprenantCreate(
                nom=nom,
                prenom=prenom,
                email=email,
                date_naissance=date(annee_naiss, mois_naiss, jour_naiss),
                niveau_etude=random.choice(NIVEAUX_ETUDE),
                telephone=tel,
                certification_obtenue=random.choice(CERTIFICATIONS),
            )
            obj = Apprenant(**schema.model_dump())
            db.add(obj)
            apprenants_objs.append(obj)
        db.commit()
        for obj in apprenants_objs:
            db.refresh(obj)

        # =====================================================================
        # E. SALLES (12 Salles - Table : salles - sans equipements en V1)
        # =====================================================================
        print("🏫 6. Insertion de 12 Salles (sans equipements avant Alembic v3)...")
        salles_data = [
            ("Salle A101 - Ada Lovelace", 25, "Bâtiment Nord, 1er étage"),
            ("Salle A102 - Guido van Rossum", 20, "Bâtiment Nord, 1er étage"),
            ("Labo B201 - Alan Turing (IA & GPU)", 16, "Bâtiment Sud, 2ème étage"),
            ("Labo B202 - Edgar Codd (BDD & SQL)", 24, "Bâtiment Sud, 2ème étage"),
            ("Salle C001 - Grace Hopper (Mini-Lab)", 3, "Rez-de-chaussée, Aile Est"),
            ("Salle C002 - Margaret Hamilton", 12, "Rez-de-chaussée, Aile Est"),
            ("Labo Cyber D301 - Kevin Mitnick", 18, "Bâtiment Ouest, 3ème étage"),
            ("Labo Cloud D302 - Kelsey Hightower", 20, "Bâtiment Ouest, 3ème étage"),
            ("Salle E105 - Donald Knuth", 30, "Bâtiment Central, 1er étage"),
            ("Salle E106 - Barbara Liskov", 15, "Bâtiment Central, 1er étage"),
            ("Amphithéâtre Linus Torvalds", 60, "Bâtiment Central, RDC"),
            ("Amphithéâtre Tim Berners-Lee", 80, "Bâtiment Nord, RDC"),
        ]
        salles_objs = []
        for nom, cap, loc in salles_data:
            schema = SalleCreate(
                nom=nom,
                capacite=cap,
                localisation=loc,
            )
            obj = Salle(**schema.model_dump())
            db.add(obj)
            salles_objs.append(obj)
        db.commit()
        for obj in salles_objs:
            db.refresh(obj)

        # =====================================================================
        # F. SESSIONS DE FORMATION (25 Sessions - Table : sessions - sans statut en V1)
        # =====================================================================
        print("📅 7. Planification de 25 Sessions (sans statut avant Alembic v2)...")
        titres_cours = [
            ("Modélisation BDD & ORM avec SQLModel", "Conception MCD/MLD, héritage SQLModel et validation stricte avec Pydantic v2.", "Python Intermédiaire", ["VS Code", "SQLite"]),
            ("Migrations de Schéma avec Alembic", "Gestion du cycle de vie de la base de données, upgrade/downgrade et autogenerate.", "Bases SQL", ["Alembic", "Git"]),
            ("Atelier Intensif DevOps (Mini-Lab 3 places)", "Petit groupe de 3 places max : idéal pour tester le blocage de capacité maximale en soutenance !", "Linux CLI", ["Docker", "Bash"]),
            ("Développement Web Back-End avec Flask", "Création d'interfaces d'administration ERP connectées à SQLModel et Bootstrap 5.", "Python & HTML", ["Flask", "Jinja2"]),
            ("Machine Learning & Data Cleaning", "Nettoyage d'un dataset legacy de 2000 lignes et détection d'anomalies.", "Mathématiques & Python", ["Jupyter", "Pandas"]),
            ("Architecture Cloud AWS & Terraform", "Déploiement d'infrastructures reproductibles avec Terraform et Docker.", "Réseaux & Linux", ["Terraform", "AWS CLI"]),
            ("Sécurité des Applications Web (OWASP Top 10)", "Prévention des injections SQL, XSS, CSRF et sécurisation des API.", "Développement Web", ["BurpSuite", "OWASP ZAP"]),
            ("Pipelines ETL avec Apache Airflow & Spark", "Orchestration de flux de données massifs et stockage Data Lake.", "Python & SQL avancé", ["Airflow", "PySpark"]),
            ("Administration PostgreSQL & Optimisation", "Indexation B-Tree, analyse EXPLAIN ANALYZE et réplication haute disponibilité.", "SQL Standard", ["PostgreSQL", "pgAdmin"]),
            ("API RESTful Haute Performance avec FastAPI", "Conception d'API asynchrones documentées avec OpenAPI / Swagger.", "Python POO", ["FastAPI", "Uvicorn"]),
            ("Conteneurisation & Orchestration Kubernetes", "Déploiement de pods, services, ingress et monitoring Prometheus/Grafana.", "Docker de base", ["kubectl", "Helm"]),
            ("Analyse Décisionnelle & Dashboarding PowerBI", "Création de tableaux de bord exécutifs et modélisation en étoile.", "Excel & SQL", ["PowerBI", "DAX"]),
        ]

        sessions_objs = []
        base_date = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)

        for idx in range(25):
            titre_base, desc, niv, outils = titres_cours[idx % len(titres_cours)]
            titre = titre_base if idx < len(titres_cours) else f"{titre_base} - Promo #{idx // len(titres_cours) + 1}"

            if idx == 2:
                salle_choisie = salles_objs[4]
                cap_max = 3
            else:
                salle_choisie = salles_objs[idx % len(salles_objs)]
                cap_max = max(3, min(salle_choisie.capacite, salle_choisie.capacite - (idx % 5)))

            formateur_choisi = formateurs_objs[idx % len(formateurs_objs)]

            dt_debut = base_date + timedelta(days=idx)
            dt_fin = dt_debut + timedelta(hours=8)

            schema = SessionCreate(
                titre=titre,
                description=desc,
                date_debut=dt_debut,
                date_fin=dt_fin,
                salle_id=salle_choisie.id,
                formateur_id=formateur_choisi.id,
                capacite_max=cap_max,
                prerequis={"niveau": niv, "outils": outils},
            )
            assert is_salle_disponible(
                db, schema.salle_id, schema.date_debut, schema.date_fin
            ), f"Conflit sur la salle {schema.salle_id}"

            obj = SessionFormation(**schema.model_dump())
            db.add(obj)
            sessions_objs.append(obj)

        db.commit()
        for obj in sessions_objs:
            db.refresh(obj)

        # =====================================================================
        # G. INSCRIPTIONS (~300 Inscriptions - Table : inscriptions)
        # =====================================================================
        print("📝 9. Inscription des Apprenants aux Sessions (via inscrire_apprenant)...")
        nb_inscriptions = 0

        for idx, sess_obj in enumerate(sessions_objs):
            # Pour la session Mini-Lab (idx == 2, capacité 3), on inscrit 2 personnes (reste 1 place pour la démo !)
            if idx == 2:
                cibles = apprenants_objs[:2]
            else:
                nb_a_inscrire = min(sess_obj.capacite_max - 2, random.randint(10, 22))
                cibles = random.sample(apprenants_objs, k=max(2, nb_a_inscrire))

            for app_obj in cibles:
                try:
                    inscrire_apprenant(
                        db,
                        InscriptionCreate(apprenant_id=app_obj.id, session_id=sess_obj.id),
                    )
                    nb_inscriptions += 1
                except (ChevauchementSessionError, SessionPleineError, ValueError):
                    pass

    # Supprimer d'éventuels anciens fichiers doublons (cftech-2.db / cftech2.db) pour ne garder que cftech.db
    for old_file in ("cftech-2.db", "cftech2.db"):
        old_path = os.path.join(base_dir, old_file)
        if os.path.exists(old_path):
            os.remove(old_path)

    print("\n" + "=" * 68)
    print("✨ GRANDE BASE DE DONNÉES DE SOUTENANCE GÉNÉRÉE AVEC SUCCÈS !")
    print("=" * 68)
    print("📁 Fichier unique généré : cftech.db")
    print("📊 Volume créé (100 % validé par Pydantic & SQLModel) :")
    print("   - 8   Admins             (table : admins)")
    print("   - 10  Staff Pédagogique  (table : staff_pedagogiques)")
    print("   - 20  Formateurs         (table : formateurs)")
    print("   - 200 Apprenants         (table : apprenants)")
    print("   - 12  Salles + JSON      (table : salles)")
    print("   - 25  Sessions + JSON    (table : sessions)")
    print(f"   - {nb_inscriptions} Inscriptions       (table : inscriptions)")
    print("=" * 68)


if __name__ == "__main__":
    generer_base_presentation()