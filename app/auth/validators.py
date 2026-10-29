from datetime import datetime
from sqlmodel import Session, select, func
from app.models.salles import Salle
from app.models.sessions import SessionFormation, StatutSessionEnum
from app.models.inscriptions import Inscription, StatutInscriptionEnum
from app.schemas.inscriptions_schemas import InscriptionCreate


class ChevauchementSessionError(Exception):
    """Conflit d'horaire détecté entre deux sessions."""


class SessionPleineError(Exception):
    """La session a atteint sa capacité maximale."""


def is_salle_disponible(
    db: Session, salle_id: int, debut: datetime, fin: datetime
) -> bool:
    conflit = db.exec(
        select(SessionFormation).where(
            SessionFormation.salle_id == salle_id,
            SessionFormation.statut != StatutSessionEnum.ARCHIVED,
            SessionFormation.date_debut < fin,
            SessionFormation.date_fin > debut,
        )
    ).first()

    return conflit is None


def inscrire_apprenant(db: Session, data: InscriptionCreate) -> Inscription:
    nouvelle = db.get(SessionFormation, data.session_id)
    if nouvelle is None:
        raise ValueError(f"Session {data.session_id} introuvable.")

    if nouvelle.statut != StatutSessionEnum.OPEN:
        raise ValueError("Cette session n'est pas ouverte aux inscriptions.")

    # 1. Vérifier la capacité maximale
    nb_inscrits = db.exec(
        select(func.count(Inscription.id)).where(
            Inscription.session_id == data.session_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
        )
    ).one()

    if nb_inscrits >= nouvelle.capacite_max:
        raise SessionPleineError(
            f"Session '{nouvelle.titre}' complète ({nb_inscrits}/{nouvelle.capacite_max})."
        )

    # 2. Vérifier le chevauchement horaire pour l'apprenant
    conflit = db.exec(
        select(SessionFormation)
        .join(Inscription, Inscription.session_id == SessionFormation.id)
        .where(
            Inscription.apprenant_id == data.apprenant_id,
            Inscription.statut_inscription == StatutInscriptionEnum.ENREGISTRE,
            SessionFormation.date_debut < nouvelle.date_fin,
            SessionFormation.date_fin > nouvelle.date_debut,
        )
    ).first()

    if conflit:
        raise ChevauchementSessionError(
            f"Conflit horaire avec la session '{conflit.titre}'."
        )

    # 3. Enregistrement en base
    inscription = Inscription(**data.model_dump())
    db.add(inscription)
    db.commit()
    db.refresh(inscription)
    return inscription