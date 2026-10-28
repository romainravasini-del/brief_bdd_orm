from flask import Flask, render_template, request, redirect, url_for, flash
from pydantic import ValidationError
from sqlmodel import Session, select, func

from app.database import engine, create_db_and_tables
from app.models.users import Apprenant, Formateur, StaffPedagogique, Admin
from app.models.salles import Salle
from app.models.sessions import SessionFormation
from app.models.inscriptions import Inscription
from app.schemas.users_schemas import ApprenantCreate

app = Flask(__name__)
app.secret_key = "cftech-secret-key"


@app.route("/")
def index():
    with Session(engine) as session:
        nb_apprenants = session.exec(select(func.count(Apprenant.id))).one()
        nb_formateurs = session.exec(select(func.count(Formateur.id))).one()
        nb_salles = session.exec(select(func.count(Salle.id))).one()
        nb_sessions = session.exec(select(func.count(SessionFormation.id))).one()

    return render_template(
        "index.html",
        nb_apprenants=nb_apprenants,
        nb_formateurs=nb_formateurs,
        nb_salles=nb_salles,
        nb_sessions=nb_sessions,
    )


@app.route("/users", methods=["GET", "POST"])
def manage_users():
    if request.method == "POST":
        try:
            donnees_valides = ApprenantCreate(
                nom=request.form.get("nom"),
                prenom=request.form.get("prenom"),
                email=request.form.get("email"),
                date_naissance=request.form.get("date_naissance"),
                niveau_etude=request.form.get("niveau_etude"),
                telephone=request.form.get("telephone") or None,
            )

            nouvel_eleve = Apprenant(**donnees_valides.model_dump())
            with Session(engine) as session:
                session.add(nouvel_eleve)
                session.commit()

            flash("✅ Apprenant ajouté avec succès !", "success")
            return redirect(url_for("manage_users"))

        except ValidationError as e:
            message_erreur = e.errors()[0]["msg"]
            flash(f"❌ Erreur Pydantic : {message_erreur}", "danger")
        except Exception as e:
            flash(f"❌ Erreur BDD : {e}", "danger")

    with Session(engine) as session:
        apprenants = session.exec(select(Apprenant).limit(50)).all()
        formateurs = session.exec(select(Formateur).limit(50)).all()

    return render_template("users.html", apprenants=apprenants, formateurs=formateurs)


if __name__ == "__main__":
    create_db_and_tables()
    app.run(debug=True)
