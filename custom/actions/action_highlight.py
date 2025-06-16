from .action import Action

class ActionHighlight(Action):
    """
        Classe ActionHighlight permet de mettre en évidence une entité cartographique sur une carte avec une couleur spécifique.
        Elle prend en charge différentes couleurs pour la mise en évidence et s'assure que seules certaines couleurs prédéfinies sont acceptées.
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, color: str = "yellow", text: str = ""):
        """
        Initialise une instance avec les paramètres fournis.

        Arguments:
        start_at (int): Position de début de l'entité.
        end_at (int): Position de fin de l'entité.
        entity_id (int): Identifiant de l'entité.
        color (str): Couleur de mise en évidence, par défaut "yellow". Doit être parmi "yellow", "green", "blue", "red".
        text (str): Texte associé, par défaut une chaîne vide.

        Comportement spécifique:
        Si la couleur fournie n'est pas valide, "yellow" sera utilisée par défaut.
        """
        super().__init__(start_at, end_at, entity_id, text)

        if color not in ["yellow", "green", "blue", "red"]:
            self.highlight = "yellow"
        else:
            self.highlight = color


    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s)
        - Définit la mise en surbrillance de l'entité
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        map_entity.set_highlight(self.highlight, (current_tick == self.start_at or current_tick == self.end_at))
        self.add_text(map_entity)
        return True