from sqlmodel import Session, select, func

from models.inscription import Inscription, StatutInscriptionEnum
from schemas.inscription_schemas import InscriptionCreate
from models.session import SessionFormation


class ChevauchementSessionError(Exception):
    """L'apprenant est déjà inscrit à une session qui se chevauche."""


class SessionPleineError(Exception):
    """La session a atteint sa capacité maximale."""


def inscrire_apprenant(db: Session, apprenant_id: int, session_id: int) -> Inscription:
    """Inscrit un apprenant si la session a de la place et ne chevauche pas une autre de ses sessions."""
    nouvelle = db.get(SessionFormation, session_id)
    if nouvelle is None:
        raise ValueError(f"Session {session_id} introuvable")

    # 1 Capacité
    nb_inscrits = db.exec(
        select(func.count())
        .select_from(Inscription)
        .where(
            Inscription.session_id == session_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
        )
    ).one()

    if nb_inscrits >= nouvelle.capacite_max:
        raise SessionPleineError(
            f"Session « {nouvelle.titre} » pleine ({nb_inscrits}/{nouvelle.capacite_max})"
        )

    # Chevauchement avec les autres sessions de l'apprenant
    conflit = db.exec(
        select(SessionFormation)
        .join(Inscription, Inscription.session_id == SessionFormation.id)
        .where(
            Inscription.apprenant_id == apprenant_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
            SessionFormation.date_debut < nouvelle.date_fin,
            SessionFormation.date_fin > nouvelle.date_debut,
        )
    ).first()

    if conflit:
        raise ChevauchementSessionError(
            f"Chevauchement avec la session « {conflit.titre} »"
        )

    inscription = InscriptionCreate(apprenant_id=apprenant_id, session_id=session_id)
    db.add(inscription)
    db.commit()
    db.refresh(inscription)
    return inscription