from app.models.users import UserBase

PERMISSIONS_PAR_ROLE = {
    "apprenant": {"voir_sessions", "s_inscrire"},
    "formateur": {"voir_sessions", "gerer_presences"},
    "staff": {"voir_sessions", "creer_session", "gerer_salles", "gerer_inscriptions"},
    "admin_standard": {"voir_sessions", "creer_session", "gerer_salles", "gerer_users"},
    "admin_reseau": {"voir_sessions", "gerer_salles", "gerer_users"},
    "superadmin": {"ALL"},
}


def check_permission(user: UserBase, action: str) -> bool:
    if not user or not user.is_active:
        return False

    if user.role == "superadmin":
        return True

    droits = PERMISSIONS_PAR_ROLE.get(user.role, set())
    return action in droits