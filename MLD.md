Table apprenants {
  id integer [primary key]
  nom varchar(50)
  prenom varchar(50)
  email varchar(255)
  date_naissance date
  niveau_etude varchar(50)
  telephone varchar(20)
  date_inscription_plateforme datetime
}

Table formateurs {
  id integer [primary key]
  nom varchar(50)
  prenom varchar(50)
  email varchar(255)
  specialite varchar(100)
  date_embauche date
  taux_horaire float
  bio text
}

Table staff_pedagogiques {
  id integer [primary key]
  nom varchar(50)
  prenom varchar(50)
  email varchar(255)
  poste varchar(100)
  date_prise_fonction date
  responsabilites text
}

Table admins {
  id integer [primary key]
  nom varchar(50)
  prenom varchar(50)
  email varchar(255)
  niveau_acces varchar(50)
  date_promotion date
}

Table salles {
  id integer [primary key]
  nom varchar(50) [unique]
  capacite integer
  localisation varchar(150)
  equipements text
  is_active boolean
}

Table sessions {
  id integer [primary key]
  titre varchar(100)
  description text
  date_debut datetime
  date_fin datetime
  salle_id integer
  formateur_id integer
  capacite_max integer
  statut varchar(50)
  prerequis text
}

Table inscriptions {
  id integer [primary key]
  apprenant_id integer
  session_id integer
  date_inscription datetime
  statut_inscription varchar(50)
  presence boolean
}

Ref: sessions.salle_id > salles.id
Ref: sessions.formateur_id > formateurs.id
Ref: inscriptions.apprenant_id > apprenants.id
Ref: inscriptions.session_id > sessions.id