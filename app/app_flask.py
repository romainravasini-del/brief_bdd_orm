from flask import Flask, render_template, request, redirect, url_for, flash
from sqlmodel import Session, select, func
from pydantic import ValidationError
from app.schemas.users_schemas import ApprenantCreate
from app.database import engine, create_db_and_tables
from app.models.users import Apprenant, Formateur, StaffPedagogique, Admin
from app.models.salles import Salle
from app.models.sessions import SessionFormation
from app.models.inscriptions import Inscription

# 1. Initialiser l'application Flask
app = Flask(__name__)
app.secret_key = "cftech-secret-key"  # Nécessaire pour afficher les messages d'alerte (flash)


# 2. Créer la route de la page d'accueil (Dashboard)
@app.route("/")
def index():
    with Session(engine) as session:  # Ouvre une session SQLModel
        nb_apprenants = session.exec(select(func.count(Apprenant.id))).one()
        nb_formateurs = session.exec(select(func.count(Formateur.id))).one()
        nb_salles = session.exec(select(func.count(Salle.id))).one()
        nb_sessions = session.exec(select(func.count(SessionFormation.id))).one()

    # Renvoie la page HTML index.html avec les 4 compteurs
    return render_template("index.html",
        nb_apprenants=nb_apprenants,
        nb_formateurs=nb_formateurs,
        nb_salles=nb_salles,
        nb_sessions=nb_sessions
    )


if __name__ == "__main__":
    create_db_and_tables()  # Crée les tables si elles n'existent pas encore
    app.run(debug=True)      # Mettre True pour que le serveur se recharge tout seul !

@app.___("/users", methods=["GET", "POST"])
def manage_users():
    # 1. Si l'utilisateur a cliqué sur "Ajouter un apprenant" (Formulaire POST)
    if request.method == "___":
        try:
            # On récupère les données du formulaire HTML et on les donne au vigile Pydantic
            donnees_valides = ApprenantCreate(
                nom=request.form.get("nom"),
                prenom=request.form.get("___"),
                email=request.form.get("___"),
                date_naissance=request.form.get("date_naissance"),
                niveau_etude=request.form.get("niveau_etude"),
                telephone=request.form.get("telephone") or None,
            )

            # Si Pydantic n'a pas levé d'erreur, on transforme en modèle SQLModel et on sauvegarde !
            nouvel_eleve = Apprenant(**donnees_valides.model_dump())
            with ___(engine) as session:
                session.___(nouvel_eleve)
                session.___()

            flash("✅ Apprenant ajouté avec succès !", "success")
            return redirect(url_for("manage_users"))

        except ValidationError as e:
            # Si l'élève a moins de 16 ans ou un faux email, Pydantic bloque ici !
            message_erreur = e.errors()[0]["msg"]
            flash(f"❌ Erreur de validation Pydantic : {message_erreur}", "danger")
        except Exception as e:
            flash(f"❌ Erreur base de données (ex: email déjà utilisé) : {e}", "danger")

    # 2. Dans tous les cas (GET), on récupère la liste des utilisateurs pour les afficher
    with Session(engine) as session:
        # On limite à 50 pour que la page soit rapide même avec 2000 utilisateurs
        apprenants = session.exec(select(___).limit(50)).all()
        formateurs = session.exec(select(___).limit(50)).all()

    return ___("users.html", apprenants=apprenants, formateurs=formateurs)