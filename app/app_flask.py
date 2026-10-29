from flask import Flask, render_template, request, redirect, url_for, flash
from pydantic import ValidationError
from sqlmodel import Session, select, func
from app.database import engine, create_db_and_tables
from app.models.users import Apprenant, Formateur, StaffPedagogique, Admin
from app.models.salles import Salle
from app.models.sessions import SessionFormation
from app.models.inscriptions import Inscription
from app.schemas.users_schemas import (
    ApprenantCreate,
    FormateurCreate,
    StaffCreate,
    AdminCreate,
)
from app.schemas.sessions_schemas import SalleCreate, SessionCreate
from app.schemas.inscriptions_schemas import InscriptionCreate
from app.auth.validators import is_salle_disponible, inscrire_apprenant

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
        type_user = request.form.get("type_user", "apprenant")
        try:
            with Session(engine) as session:
                if type_user == "apprenant":
                    data = ApprenantCreate(
                        nom=request.form.get("nom"),
                        prenom=request.form.get("prenom"),
                        email=request.form.get("email"),
                        date_naissance=request.form.get("date_naissance"),
                        niveau_etude=request.form.get("niveau_etude"),
                        telephone=request.form.get("telephone") or None,
                    )
                    session.add(Apprenant(**data.model_dump()))

                elif type_user == "formateur":
                    data = FormateurCreate(
                        nom=request.form.get("nom"),
                        prenom=request.form.get("prenom"),
                        email=request.form.get("email"),
                        specialite=request.form.get("specialite"),
                        date_embauche=request.form.get("date_embauche"),
                        taux_horaire=request.form.get("taux_horaire"),
                    )
                    session.add(Formateur(**data.model_dump()))

                elif type_user == "staff":
                    raw_resp = request.form.get("responsabilites", "").strip()
                    resp_dict = (
                        {"missions": [r.strip() for r in raw_resp.split(",") if r.strip()]}
                        if raw_resp
                        else None
                    )
                    data = StaffCreate(
                        nom=request.form.get("nom"),
                        prenom=request.form.get("prenom"),
                        email=request.form.get("email"),
                        poste=request.form.get("poste"),
                        date_prise_fonction=request.form.get("date_prise_fonction"),
                        responsabilites=resp_dict,
                    )
                    session.add(StaffPedagogique(**data.model_dump()))

                elif type_user == "admin":
                    data = AdminCreate(
                        nom=request.form.get("nom"),
                        prenom=request.form.get("prenom"),
                        email=request.form.get("email"),
                        niveau_acces=request.form.get("niveau_acces"),
                        date_promotion=request.form.get("date_promotion"),
                    )
                    session.add(Admin(**data.model_dump()))

                session.commit()

            flash(f"✅ {type_user.capitalize()} ajouté avec succès !", "success")
            return redirect(url_for("manage_users"))

        except ValidationError as e:
            flash(f"❌ Erreur Pydantic : {e.errors()[0]['msg']}", "danger")
        except Exception as e:
            flash(f"❌ Erreur BDD : {e}", "danger")

    with Session(engine) as session:
        apprenants = session.exec(select(Apprenant).limit(50)).all()
        formateurs = session.exec(select(Formateur).limit(50)).all()
        staffs = session.exec(select(StaffPedagogique).limit(50)).all()
        admins = session.exec(select(Admin).limit(50)).all()

    return render_template(
        "users.html",
        apprenants=apprenants,
        formateurs=formateurs,
        staffs=staffs,
        admins=admins,
    )


@app.route("/sessions", methods=["GET", "POST"])
def manage_sessions():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            with Session(engine) as session:
                if action == "creer_salle":
                    raw_eq = request.form.get("equipements", "").strip()
                    eq_dict = (
                        {"materiel": [e.strip() for e in raw_eq.split(",") if e.strip()]}
                        if raw_eq
                        else None
                    )
                    data_salle = SalleCreate(
                        nom=request.form.get("nom"),
                        capacite=request.form.get("capacite"),
                        localisation=request.form.get("localisation"),
                        equipements=eq_dict,
                    )
                    session.add(Salle(**data_salle.model_dump()))
                    session.commit()
                    flash("✅ Salle créée avec succès !", "success")

                elif action == "creer_session":
                    data_sess = SessionCreate(
                        titre=request.form.get("titre"),
                        date_debut=request.form.get("date_debut"),
                        date_fin=request.form.get("date_fin"),
                        salle_id=request.form.get("salle_id"),
                        formateur_id=request.form.get("formateur_id"),
                        capacite_max=request.form.get("capacite_max"),
                    )

                    salle = session.get(Salle, data_sess.salle_id)
                    if data_sess.capacite_max > salle.capacite:
                        raise ValueError(
                            f"Capacité max ({data_sess.capacite_max}) > capacité de la salle ({salle.capacite}) !"
                        )

                    if not is_salle_disponible(
                        session, data_sess.salle_id, data_sess.date_debut, data_sess.date_fin
                    ):
                        raise ValueError(
                            "Conflit horaire : Cette salle est déjà occupée sur ce créneau !"
                        )

                    session.add(SessionFormation(**data_sess.model_dump()))
                    session.commit()
                    flash("✅ Session planifiée avec succès !", "success")

                elif action == "inscrire":
                    data_insc = InscriptionCreate(
                        apprenant_id=request.form.get("apprenant_id"),
                        session_id=request.form.get("session_id"),
                    )
                    inscrire_apprenant(session, data_insc)
                    flash("✅ Apprenant inscrit à la session avec succès !", "success")

            return redirect(url_for("manage_sessions"))

        except ValidationError as e:
            flash(f"❌ Erreur Pydantic : {e.errors()[0]['msg']}", "danger")
        except Exception as e:
            flash(f"❌ Règle Métier bloquée : {e}", "danger")

    with Session(engine) as session:
        sessions_list = session.exec(select(SessionFormation)).all()
        salles = session.exec(select(Salle)).all()
        formateurs = session.exec(select(Formateur)).all()
        apprenants = session.exec(select(Apprenant)).all()
        inscriptions = session.exec(select(Inscription)).all()

    return render_template(
        "sessions.html",
        sessions=sessions_list,
        salles=salles,
        formateurs=formateurs,
        apprenants=apprenants,
        inscriptions=inscriptions,
    )


if __name__ == "__main__":
    create_db_and_tables()
    app.run(debug=True)