from typing import Optional
from pathlib import Path

from ..business.domain_problem_model import DomainProblemModel


class DomainProblemManager:
    _instance: Optional["DomainProblemManager"] = None

    def __init__(self):
        self._current_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainProblemManager, cls).__new__(cls)
            cls._instance._current_model = None
        return cls._instance

    def initialize(self, domain_path: str, problem_path: str, plan_path: Optional[str] = None) -> None:
        """
        Initialise ou remplace le DomainProblemModel courant si les fichiers sont valides.
        """
        if not Path(domain_path).exists():
            raise FileNotFoundError(f"Fichier domaine non trouvé : {domain_path}")
        if not Path(problem_path).exists():
            raise FileNotFoundError(f"Fichier problème non trouvé : {problem_path}")
        if plan_path and not Path(plan_path).exists():
            raise FileNotFoundError(f"Fichier plan non trouvé : {plan_path}")

        self._current_model = DomainProblemModel(domain_path, problem_path, plan_path)

    def get_current_model(self) -> DomainProblemModel:
        if self._current_model is None:
            raise ValueError("Aucun DomainProblemModel n’a été initialisé. Utilisez 'initialize()' d’abord.")
        return self._current_model

    def has_model(self) -> bool:
        return self._current_model is not None

    def reset(self) -> None:
        """Réinitialise l'instance du modèle courant."""
        self._current_model = None
