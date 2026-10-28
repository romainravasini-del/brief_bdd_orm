from flask import Flask, render_template, request, redirect, url_for, flash
from sqlmodel import Session, select, func

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
    