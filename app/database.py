import random
import sqlite3
import csv
import json
from datetime import date, datetime, timedelta

random.seed(42)

PRENOMS = [
    "Lucas", "Emma", "Gabriel", "Jade", "Léo", "Louise", "Raphaël", "Ambre", "Arthur", "Alice",
    "Louis", "Chloé", "Jules", "Lina", "Adam", "Mia", "Maël", "Léa", "Paul", "Manon",
    "Hugo", "Rose", "Valentin", "Anna", "Gabin", "Inès", "Sacha", "Camille", "Noah", "Lola",
    "Théo", "Julia", "Tom", "Zoe", "Nathan", "Sarah", "Mathis", "Eva", "Ethan", "Juliette",
    "Maxime", "Lucie", "Antoine", "Romane", "Yanis", "Agathe", "Alexandre", "Nina", "Victor", "Clémence",
    "Mohamed", "Yasmine", "Amine", "Sofia", "Mehdi", "Nour", "Karim", "Farah", "Rayan", "Salma",
    "Nicolas", "Marie", "Julien", "Laura", "Sébastien", "Julie", "Thomas", "Céline", "Romain", "Aurélie",
    "Florian", "Élodie", "Guillaume", "Mathilde", "Kévin", "Pauline", "Quentin", "Charlotte", "Jérémy", "Marine",
    "Benoît", "Justine", "Vincent", "Morgane", "Adrien", "Marion", "Clément", "Océane", "Pierre", "Margaux",
    "Bastien", "Anaïs", "Corentin", "Claire", "Dorian", "Mélanie", "Thibault", "Estelle", "Baptiste", "Fanny"
]

NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent",
    "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard",
    "Bonnet", "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller", "Lefevre", "Faure", "Andre",
    "Mercier", "Blanc", "Guerin", "Boyer", "Garnier", "Chevalier", "Francois", "Legrand", "Gauthier", "Garcia",
    "Perrin", "Robin", "Clement", "Morin", "Nicolas", "Henry", "Roussel", "Mathieu", "Gautier", "Masson",
    "Marchand", "Duval", "Denis", "Dumont", "Marie", "Lemaire", "Noel", "Meyer", "Dufour", "Meunier",
    "Brun", "Blanchard", "Giraud", "Joly", "Riviere", "Lucas", "Brunet", "Gaillard", "Barbier", "Arnaud",
    "Martinez", "Gerard", "Roche", "Renard", "Schmitt", "Roy", "Leroux", "Colin", "Vidal", "Caron",
    "Picard", "Roger", "Fabre", "Aubert", "Lemoine", "Renaud", "Dumas", "Lacroix", "Olivier", "Philippe",
    "Bourgeois", "Pierre", "Benoit", "Rey", "Leclerc", "Payet", "Rolland", "Leclercq", "Guillaume", "Lecomte"
]

DOMAINES = ["gmail.com", "orange.fr", "free.fr", "wanadoo.fr", "outlook.fr", "yahoo.fr", "cf-tech.fr", "laposte.net", "sfr.fr"]
NIVEAUX_ETUDE = ["Sans diplôme", "CAP/BEP", "Bac", "Bac+2", "Bac+3", "Bac+5", "Doctorat"]
CERTIFICATIONS = [None, None, None, "RNCP Niveau 5 - Dev Web", "RNCP Niveau 6 - Data Engineer", "AWS Cloud Practitioner", "PCAP Python", "Cisco CCNA", "Azure Fundamentals"]
SPECIALITES = ["Data Science", "DevOps", "Cybersécurité", "Développement Web Python", "Administration Réseau & Linux", "Intelligence Artificielle", "Cloud AWS/Azure", "Bases de données SQL/NoSQL", "Gestion de projet Agile"]
POSTES_STAFF = ["Responsable pédagogique", "Chargé(e) de projet formation", "Coordinateur(trice) pédagogique", "Référent(e) handicap & suivi", "Assistant(e) administratif(ve)", "Conseiller(ère) en insertion"]
NIVEAUX_ADMIN = ["ADMIN_STANDARD", "SUPERADMIN", "ADMIN_RESEAU"]

def strip_accents(s: str) -> str:
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'œ': 'oe'
    }
    res = s.lower()
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res

def random_date(start_year: int, end_year: int) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(1, delta)))

def random_datetime(start_year: int, end_year: int) -> str:
    d = random_date(start_year, end_year)
    h = random.randint(8, 19)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{d.isoformat()} {h:02d}:{m:02d}:{s:02d}"

def generate_valid_phone() -> str:
    prefix = random.choice(["06", "07", "01", "02", "03", "04", "05", "09"])
    digits = "".join(str(random.randint(0, 9)) for _ in range(8))
    return prefix + digits

def main():
    total_users = 2000
    # Repartition: 1750 apprenants, 150 formateurs, 60 staff_pedagogiques, 40 admins (dont admins réseau)
    # Taux d'anomalies visé: ~12.5% (soit ~250 enregistrements corrompus/inexploitables à filtrer par Pydantic)
    records = []
    used_emails = set()
    valid_emails_pool = []

    roles_distribution = (
        ["apprenant"] * 1750 +
        ["formateur"] * 150 +
        ["staff"] * 60 +
        ["admin"] * 40
    )
    random.shuffle(roles_distribution)

    anomalies_count = 0

    for idx, role in enumerate(roles_distribution, start=1):
        is_corrupted = (random.random() < 0.13)  # ~13% de données sales héritées d'Excel/ERP
        anomaly_type = None
        if is_corrupted:
            anomalies_count += 1
            if role == "apprenant":
                anomaly_type = random.choice([
                    "age_mineur_16", "age_mineur_16", "email_invalide", "email_doublon",
                    "telephone_invalide", "nom_vide_ou_trop_long", "date_naissance_future", "role_invalide"
                ])
            elif role == "formateur":
                anomaly_type = random.choice([
                    "taux_horaire_negatif", "date_embauche_future", "email_invalide",
                    "email_doublon", "nom_vide_ou_trop_long", "specialite_vide"
                ])
            elif role == "staff":
                anomaly_type = random.choice([
                    "email_invalide", "json_responsabilites_corrompu", "nom_vide_ou_trop_long", "role_invalide"
                ])
            elif role == "admin":
                anomaly_type = random.choice([
                    "email_invalide", "niveau_acces_invalide", "date_promotion_future", "email_doublon"
                ])

        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)

        # Generation email propre de base
        base_email = f"{strip_accents(prenom)}.{strip_accents(nom)}{idx}@{random.choice(DOMAINES)}"
        while base_email in used_emails:
            base_email = f"{strip_accents(prenom)}.{strip_accents(nom)}{idx}_{random.randint(1,999)}@{random.choice(DOMAINES)}"
        used_emails.add(base_email)
        if not is_corrupted:
            valid_emails_pool.append(base_email)

        email = base_email
        date_creation = random_datetime(2022, 2025)
        is_active = 1 if random.random() < 0.92 else 0
        db_role = role

        # Champs spécifiques par défaut (NULL pour les autres rôles ou selon table)
        date_naissance = None
        niveau_etude = None
        telephone = None
        date_inscription_plateforme = None
        certification_obtenue = None

        specialite = None
        date_embauche = None
        taux_horaire = None
        bio = None

        poste = None
        date_prise_fonction = None
        responsabilites = None

        niveau_acces = None
        date_promotion = None

        if role == "apprenant":
            date_naissance = random_date(1975, 2008).isoformat()  # >= 18 ans en 2026
            niveau_etude = random.choice(NIVEAUX_ETUDE)
            telephone = generate_valid_phone()
            date_inscription_plateforme = date_creation
            certification_obtenue = random.choice(CERTIFICATIONS)

        elif role == "formateur":
            specialite = random.choice(SPECIALITES)
            date_embauche = random_date(2015, 2025).isoformat()
            taux_horaire = round(random.uniform(35.0, 95.0), 2)
            bio = f"Formateur expert en {specialite} avec plusieurs années d'expérience terrain."

        elif role == "staff":
            poste = random.choice(POSTES_STAFF)
            date_prise_fonction = random_date(2016, 2025).isoformat()
            responsabilites = json.dumps(
                {"missions": ["Suivi apprenants", "Planning", "Gestion salles"], "campus": random.choice(["Paris", "Lyon", "Nantes", "Lille", "Bordeaux"])},
                ensure_ascii=False
            )

        elif role == "admin":
            niveau_acces = random.choice(NIVEAUX_ADMIN)
            date_promotion = random_date(2018, 2025).isoformat()

        # Injection des anomalies "Legacy Excel / ERP"
        if anomaly_type == "age_mineur_16":
            # Apprenant entre 8 et 15 ans (ex: né entre 2012 et 2019)
            date_naissance = random_date(2012, 2020).isoformat()
        elif anomaly_type == "date_naissance_future":
            date_naissance = random_date(2027, 2035).isoformat()
        elif anomaly_type == "email_invalide":
            email = random.choice([
                f"{strip_accents(prenom)}.{strip_accents(nom)}_at_gmail.com",
                f"{strip_accents(prenom)}@@wanadoo..fr",
                "pas_un_email_du_tout",
                f"{strip_accents(nom)}@domaine-sans-extension",
                ""
            ])
        elif anomaly_type == "email_doublon":
            if valid_emails_pool:
                email = random.choice(valid_emails_pool)
            else:
                email = "doublon.erp@cf-tech.fr"
        elif anomaly_type == "telephone_invalide":
            telephone = random.choice([
                "06123",                # Trop court
                "06.12.34.XX.YY",       # Lettres dans le numéro
                "999999999999999",      # Trop long / préfixe invalide
                "N/A - voir Excel",     # Texte libre d'Excel
                "+33(0)612"             # Incomplet
            ])
        elif anomaly_type == "nom_vide_ou_trop_long":
            if random.random() < 0.5:
                nom = ""
            else:
                nom = "X" * 75  # Dépasse max_length=50
        elif anomaly_type == "role_invalide":
            db_role = random.choice(["stagiaire_fantome", "inconnu_erp", "root_legacy", "invite"])
        elif anomaly_type == "taux_horaire_negatif":
            taux_horaire = round(random.uniform(-85.0, -5.0), 2)
        elif anomaly_type == "date_embauche_future":
            date_embauche = random_date(2027, 2032).isoformat()
        elif anomaly_type == "specialite_vide":
            specialite = ""
        elif anomaly_type == "json_responsabilites_corrompu":
            responsabilites = "{erreur_json_excel: 'valeur non fermée"
        elif anomaly_type == "niveau_acces_invalide":
            niveau_acces = random.choice(["DIEU_DU_RESEAU", "STAGIAIRE_ADMIN", "UNKNOWN_LEVEL"])
        elif anomaly_type == "date_promotion_future":
            date_promotion = random_date(2028, 2035).isoformat()

        records.append({
            "id": idx,
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "date_creation": date_creation,
            "is_active": is_active,
            "role": db_role,
            "date_naissance": date_naissance,
            "niveau_etude": niveau_etude,
            "telephone": telephone,
            "date_inscription_plateforme": date_inscription_plateforme,
            "certification_obtenue": certification_obtenue,
            "specialite": specialite,
            "date_embauche": date_embauche,
            "taux_horaire": taux_horaire,
            "bio": bio,
            "poste": poste,
            "date_prise_fonction": date_prise_fonction,
            "responsabilites": responsabilites,
            "niveau_acces": niveau_acces,
            "date_promotion": date_promotion,
            "anomalie_simulee": anomaly_type or "VALIDE"
        })

    print(f"Total généré: {len(records)} utilisateurs | Anomalies: {anomalies_count} ({anomalies_count/len(records)*100:.1f}%)")

    # 1. Création du fichier SQL complet (avec à la fois la table brute legacy_erp_users ET les 4 tables séparées)
    sql_path = "/home/romain/.gemini/antigravity/brain/096ecec2-4874-485c-a20d-45e9cb7f1a4f/seed_legacy_2000_users.sql"
    db_path = "/home/romain/.gemini/antigravity/brain/096ecec2-4874-485c-a20d-45e9cb7f1a4f/legacy_erp_cftech.db"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    schema_sql = """-- ============================================================================
-- BASE DE DONNÉES LEGACY CF-TECH (2000 UTILISATEURS FRANCOPHONES)
-- Contient ~13% d'anomalies issues de l'ancien ERP / fichiers Excel
-- à filtrer avec vos schémas Pydantic et règles métier avant migration !
-- ============================================================================

DROP TABLE IF EXISTS legacy_erp_users;
DROP TABLE IF EXISTS apprenants_brut;
DROP TABLE IF EXISTS formateurs_brut;
DROP TABLE IF EXISTS staff_pedagogiques_brut;
DROP TABLE IF EXISTS admins_brut;

-- 1. Table unifiée de l'ancien ERP (idéale pour faire un script d'ETL / tri vers vos 4 tables SQLModel)
CREATE TABLE legacy_erp_users (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(255),
    date_creation DATETIME,
    is_active BOOLEAN,
    role VARCHAR(50),
    date_naissance DATE,
    niveau_etude VARCHAR(50),
    telephone VARCHAR(50),
    date_inscription_plateforme DATETIME,
    certification_obtenue VARCHAR(100),
    specialite VARCHAR(100),
    date_embauche DATE,
    taux_horaire FLOAT,
    bio TEXT,
    poste VARCHAR(100),
    date_prise_fonction DATE,
    responsabilites TEXT,
    niveau_acces VARCHAR(50),
    date_promotion DATE
);

-- 2. Les 4 tables séparées brutes (sans contraintes strictes pour permettre le chargement des erreurs à trier)
CREATE TABLE apprenants_brut (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(255),
    date_creation DATETIME,
    is_active BOOLEAN,
    role VARCHAR(50),
    date_naissance DATE,
    niveau_etude VARCHAR(50),
    telephone VARCHAR(50),
    date_inscription_plateforme DATETIME,
    certification_obtenue VARCHAR(100)
);

CREATE TABLE formateurs_brut (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(255),
    date_creation DATETIME,
    is_active BOOLEAN,
    role VARCHAR(50),
    specialite VARCHAR(100),
    date_embauche DATE,
    taux_horaire FLOAT,
    bio TEXT
);

CREATE TABLE staff_pedagogiques_brut (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(255),
    date_creation DATETIME,
    is_active BOOLEAN,
    role VARCHAR(50),
    poste VARCHAR(100),
    date_prise_fonction DATE,
    responsabilites TEXT
);

CREATE TABLE admins_brut (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(255),
    date_creation DATETIME,
    is_active BOOLEAN,
    role VARCHAR(50),
    niveau_acces VARCHAR(50),
    date_promotion DATE
);
"""
    cur.executescript(schema_sql)

    for r in records:
        cur.execute("""
            INSERT INTO legacy_erp_users VALUES (
                :id, :nom, :prenom, :email, :date_creation, :is_active, :role,
                :date_naissance, :niveau_etude, :telephone, :date_inscription_plateforme, :certification_obtenue,
                :specialite, :date_embauche, :taux_horaire, :bio,
                :poste, :date_prise_fonction, :responsabilites,
                :niveau_acces, :date_promotion
            )
        """, r)

        if r["date_naissance"] is not None:
            cur.execute("""
                INSERT INTO apprenants_brut VALUES (
                    :id, :nom, :prenom, :email, :date_creation, :is_active, :role,
                    :date_naissance, :niveau_etude, :telephone, :date_inscription_plateforme, :certification_obtenue
                )
            """, r)
        elif r["taux_horaire"] is not None:
            cur.execute("""
                INSERT INTO formateurs_brut VALUES (
                    :id, :nom, :prenom, :email, :date_creation, :is_active, :role,
                    :specialite, :date_embauche, :taux_horaire, :bio
                )
            """, r)
        elif r["poste"] is not None:
            cur.execute("""
                INSERT INTO staff_pedagogiques_brut VALUES (
                    :id, :nom, :prenom, :email, :date_creation, :is_active, :role,
                    :poste, :date_prise_fonction, :responsabilites
                )
            """, r)
        else:
            cur.execute("""
                INSERT INTO admins_brut VALUES (
                    :id, :nom, :prenom, :email, :date_creation, :is_active, :role,
                    :niveau_acces, :date_promotion
                )
            """, r)

    conn.commit()

    # Export du dump SQL complet
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- DUMP SQL COMPLET : 2000 UTILISATEURS FRANCOPHONES (AVEC ~13% D'ERREURS LEGACY)\n")
        for line in conn.iterdump():
            f.write(f"{line}\n")

    conn.close()
    print(f"Fichier SQL généré : {sql_path}")
    print(f"Base SQLite générée : {db_path}")

if __name__ == "__main__":
    main()
