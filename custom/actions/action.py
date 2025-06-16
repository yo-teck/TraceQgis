from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Action(ABC):
    """
    Classe abstraite représentant une action dans un système.

    Méthodes :
    - __init__(start_at, end_at, entity_id, text="") : Constructeur de la classe Action, initialisant les paramètres de l'action.
    - is_active_at(tick) : Retourne un booléen indiquant si l'action est active au tick donné.
    - add_text(map_entity) : Ajoute un texte à une entité donnée.
    - execute() : Méthode abstraite à implémenter pour définir l'exécution de l'action.
    - __str__() : Retourne une représentation sous forme de chaîne de caractères de l'objet Action.

    Exceptions :
    - Exception : Levée lorsque les paramètres d'initialisation sont invalides ou si start_at est supérieur à end_at.
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, text: str = ""):
        """
        Initialise une instance avec les paramètres fournis.

        Paramètres:
        start_at (int): Position de départ de l'entité. Ne doit pas être None.
        end_at (int): Position de fin de l'entité. Ne doit pas être None.
        entity_id (int): Identifiant de l'entité. Ne doit pas être None.
        text (str): Texte associé à l'entité. Valeur par défaut égale à une chaîne vide.

        Exceptions:
        Exception: Levée si les paramètres start_at, end_at ou entity_id sont None.
        Exception: Levée si start_at est supérieur à end_at.
        """
        if start_at is None or end_at is None or entity_id is None:
            raise Exception("Paramètre invalide")
        elif start_at > end_at:
            raise Exception("start_at > end_at")

        self.start_at = start_at
        self.end_at = end_at
        self.entity_id = entity_id

        self.text = text

    def is_active_at(self, tick: int) -> bool:
        """
        Détermine si un événement est actif à un instant donné.

        Paramètres:
        tick (int): Le moment ou l'instant à vérifier.

        Retourne:
        bool: True si l'événement est actif à l'instant spécifié, sinon False.
        """
        return self.start_at <= tick <= self.end_at

    def add_text(self, map_entity: "MapEntity"):
        """
        Ajoute le texte de l'objet actuel à l'entité de carte spécifiée si le texte existe.

        Paramètres:
        map_entity (MapEntity): L'entité de carte à laquelle le texte sera ajouté.

        Comportement:
        - Si l'objet courant possède un attribut `text` non vide, ce texte sera ajouté à l'entité de carte via la méthode `append_text`.
        """
        if self.text:
            map_entity.append_text(self.text)

    @abstractmethod
    def execute(self) -> bool:
        pass

    def __str__(self):
        """
        Renvoie une représentation textuelle de l'objet sous forme d'une chaîne.

        La méthode construit une chaîne de caractères comprenant le nom de la classe,
        l'état actuel du tick récupéré depuis `LayerTraceQGIS.get_current_tick`,
        ainsi que les noms et valeurs des attributs de l'objet.

        Retourne:
            str : Représentation textuelle de l'objet.
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        text = self.__class__.__name__ + ":"
        text += " current_tick=" + str(LayerTraceQGIS.get_current_tick())
        for nom_attr, valeur in self.__dict__.items():
            text += f", {nom_attr}={str(valeur)}"

        return text