from qgis.utils import iface
from qgis.core import (
    Qgis,
    QgsProject,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsField,
    QgsCategorizedSymbolRenderer,
    QgsMessageLog,
    QgsLineSymbol,
    QgsSingleSymbolRenderer,
    QgsArrowSymbolLayer,
    QgsRendererCategory
)

from qgis.PyQt.QtCore import Qt, QTimer, QVariant, pyqtSignal, QObject
from typing import TYPE_CHECKING
from PyQt5.QtGui import QColor

from PyQt5.QtCore import QMetaType
from qgis.core import QgsField

from ..actions.action_factory import ActionFactory
from ..utils.utils import Utils

if TYPE_CHECKING:
    from .map_entity import MapEntity
    from ..actions.action import Action

class LayerTraceQGIS(QObject):
    """
    Classe LayerTraceQGIS

    Cette classe gère les couches vectorielles et les entités utilisées pour suivre les entités et leurs actions dans QGIS.

    Attributs :
        signal_tick_changed      Signal émis à chaque progression de tick.
        signal_tick_reset        Signal émis lors de la réinitialisation des ticks.
        signal_timer_changed     Signal indiquant un changement d'état du timer.
        signal_entities_updated  Signal émis lorsqu'il y a une mise à jour des entités.
        _instance                Instance unique de la classe LayerTraceQGIS, utilisée pour un modèle singleton.
    """
    signal_tick_changed = pyqtSignal(int)
    signal_tick_reset = pyqtSignal(int)
    signal_timer_changed = pyqtSignal(bool)
    signal_entities_updated = pyqtSignal(list)
    _instance = None

    @classmethod
    def get_instance(cls, map_entities: ['MapEntity'] = [], actions = []):
        """
            Méthode de classe pour obtenir une instance unique de la classe LayerTraceQGIS.

            Paramètres:
                map_entities (list[MapEntity]): Liste des entités de la carte. Valeur par défaut est une liste vide.
                actions (list): Liste des actions associées. Valeur par défaut est une liste vide.

            Retourne:
                LayerTraceQGIS: Instance unique de la classe LayerTraceQGIS.
        """
        if cls._instance is None:
            cls._instance = LayerTraceQGIS(map_entities, actions)
        return cls._instance

    def __init__(self, map_entities: ['MapEntity'] = [], actions = []):
        """
        Initialise une instance de la classe.

        Paramètres:
        map_entities : liste d'objets de type 'MapEntity', optionnel
            Une liste initiale d'entités de la carte à utiliser pour l'initialisation.
        actions : liste, optionnel
            Une liste initiale d'actions à associer.

        Attributs :
        layer : objet
            La couche principale utilisée pour représenter les entités sur la carte.
        layer_lines : objet
            La couche utilisée pour représenter les lignes entre les entités sur la carte.
        layer_trace : objet
            La couche utilisée pour représenter les mouvements des entités sur la carte.
        show_name : bool
            Indicateur pour afficher ou non les noms des entités.
        show_position : bool
            Indicateur pour afficher ou non les positions des entités.
        map_entities : liste
            La liste des entités.
        tick_end : int
            La valeur de fin des tick des actions.
        actions : dict
            Un dictionnaire contenant des actions associées.
        timer : QTimer
            Un minuteur pour gérer des rafraîchissements périodiques.
        entities_loaded : dict
            Un dictionnaire contenant les entités contenue dans d'autre entitées.
        speed : int
            La vitesse du timer 1000 / speed.
        interval : int
            L'intervalle par défaut entre les rafraîchissements.
        focus : int
            L'identifiant de l'entitées focalisé.
        tick : int
            Le compteur actuel des ticks.
        lines : liste
            Une liste des lignes représentées.

        Initialise toutes les valeurs et les couche de fonctionnement en fonction des entitées et des actions
        """
        super().__init__()

        self.layer = None
        self.layer_lines = None
        self.layer_trace = None
        self.init_layer()

        self.show_name = False
        self.show_position = False

        self.map_entities = []
        self.set_map_entities(map_entities)

        self.tick_end = 0
        self.actions = {}
        self.set_actions(actions)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)

        self.entities_loaded = {}

        self.speed = 1
        self.interval = 1000
        self.focus = 0
        self.tick = 0
        self.lines = []

        iface.mapCanvas().extentsChanged.connect(self.update_all_labels)

    def init_layer(self):
        """
        Initialise et configure les couches nécessaires dans un projet QGIS, en les regroupant sous une même catégorie pour une meilleure organisation.

        Attribut initialisé:
        layer : objet
            La couche principale utilisée pour représenter les entités sur la carte.
        layer_lines : objet
            La couche utilisée pour représenter les lignes entre les entités sur la carte.
        layer_trace : objet
            La couche utilisée pour représenter les mouvements des entités sur la carte.

        Méthodes et fonctionnalités :
        - Vérifie l'existence d'un groupe "Trace QGIS" dans l'arborescence des couches du projet. Si le groupe n'existe pas, il est créé.
        - Initialise une couche vectorielle en mémoire de type "Point", nommée "Entity", avec deux attributs : un entier ("id") et une chaîne ("nom"). Cette couche est ajoutée au groupe "Trace QGIS".
        - Initialise une couche vectorielle en mémoire de type "LineString", nommée "Communication", avec un rendu spécifique basé sur un symbole de flèche noire finement ajusté.
        - Applique un rendu personnalisé à la couche "Communication" avec une flèche noire pointillée pour mieux représenter les connexions ou les directions.
        - Crée une seconde couche vectorielle en mémoire de type "LineString", nommée "Traces Mouvements", destinée à représenter les mouvements. Elle possède deux attributs : un entier ("id") et une chaîne ("nom"), et utilise un simple rendu de ligne.
        - Ajoute chaque couche nouvellement créée au projet et les regroupe dans le dossier "Trace QGIS" pour faciliter leur gestion.

        Cette fonction permet d'automatiser l'ajout et la configuration des couches géographiques en mémoire pour des projets QGIS spécifiques comportant des entités, des communications et des traces de mouvement.
        """
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Trace QGIS")
        if not group:
            group = root.addGroup("Trace QGIS")

        self.layer = QgsVectorLayer("Point?crs=EPSG:4326", "Entity", "memory")

        self.layer.dataProvider().addAttributes([
            QgsField("id", QMetaType.Int),  # entier
            QgsField("nom", QMetaType.QString)  # chaîne
        ])

        self.layer.updateFields()
        QgsProject.instance().addMapLayer(self.layer, False)
        group.addLayer(self.layer)

        # Création de la couche mémoire en LineString
        self.layer_lines = QgsVectorLayer("LineString?crs=EPSG:4326", "Communication", "memory")

        # Création du symbole de ligne principal (pointillé)
        line_symbol = QgsLineSymbol()
        line_symbol.deleteSymbolLayer(0)  # Supprimer la couche par défaut

        # Flèche noire alignée avec la ligne
        arrow_layer = QgsArrowSymbolLayer()
        arrow_layer.setColor(QColor('black'))
        arrow_layer.setWidth(0.3)  # largeur plus fine (par défaut 0.5)
        arrow_layer.setHeadThickness(1)  # épaisseur plus fine de la tête (par défaut 1)
        arrow_layer.setHeadLength(2.5)
        arrow_layer.setArrowWidth(0.4)
        arrow_layer.setArrowStartWidth(0.4)

        line_symbol.appendSymbolLayer(arrow_layer)

        # Appliquer le rendu
        line_renderer = QgsSingleSymbolRenderer(line_symbol)
        self.layer_lines.setRenderer(line_renderer)

        # Ajouter la couche au projet et au groupe
        QgsProject.instance().addMapLayer(self.layer_lines, False)
        group.addLayer(self.layer_lines)

        self.layer_trace = QgsVectorLayer("LineString?crs=EPSG:4326", "Traces Mouvements", "memory")
        self.layer_trace.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol()))

        self.layer_trace.dataProvider().addAttributes([
            QgsField("id", QMetaType.Int),  # entier
            QgsField("nom", QMetaType.QString)  # chaîne
        ])
        self.layer_trace.updateFields()

        QgsProject.instance().addMapLayer(self.layer_trace, False)
        group.addLayer(self.layer_trace)


    def reset(self, map_entities: ['MapEntity'] = [], actions = []):
        """
        Réinitialise les entités de la carte, les actions et redémarre le minuteur.

        Paramètres:
        map_entities (List[MapEntity]): Liste des entités de la carte à initialiser. Par défaut, une liste vide.
        actions (List): Liste des actions à définir. Par défaut, une liste vide.

        Modifie:
        interval (int): Définit l'intervalle à 1000.
        focus (int): Réinitialise le focus à 0.
        tick (int): Réinitialise le compteur de ticks à 0.
        lines (List): Réinitialise la liste des lignes à une liste vide.
        entities_loaded (dict): Réinitialise les entités chargées.

        Actions:
        Décharge les entités de la carte actuellement chargées.
        Met à jour les entités de la carte avec les nouvelles passées en paramètre.
        Met à jour les actions avec celles passées en paramètre.
        Redémarre le minuteur.
        """
        self.interval = 1000
        self.focus = 0
        self.tick = 0
        self.lines = []
        self.entities_loaded = {}

        for map_entity in self.map_entities.values():
            map_entity.unload()

        self.set_map_entities(map_entities)
        self.set_actions(actions)

        self.start_timer()

    def set_map_entities(self, map_entities: ['MapEntity'] = []):
        """
        Définit les entités de la carte et met à jour les couches associées.

        Cette méthode remplace les données actuelles des couches `layer` et `layer_trace` par les nouvelles entités fournies.
        Chaque entité de la carte est ajoutée à la couche principale et positionnée.
        Ensuite, les styles des couches `layer` et `layer_trace` sont appliqués de nouveau.
        La méthode émet un signal contenant une liste des ids et des noms des entités pour l'interface.

        Paramètres:
        map_entities (liste de 'MapEntity', optionnel): Liste des entités de la carte à ajouter. Par défaut, une liste vide est utilisée.
        """
        self.layer.dataProvider().truncate()
        self.layer_trace.dataProvider().truncate()

        self.map_entities = {mapEntity.get_id(): mapEntity for mapEntity in map_entities}

        for map_entity in self.map_entities.values():
            self.layer.dataProvider().addFeature(map_entity.feature)
            map_entity.update_label_position(self.show_name, self.show_position)

        self.apply_renderer()
        self.apply_trace_renderer()

        # Prépare la liste (id, name)
        info_list = [(e.get_id(), e.get_name()) for e in self.map_entities.values()]

        # Émet le signal avec la liste
        self.signal_entities_updated.emit(info_list)

    def set_actions(self, actions: []):
        """
        Définit et initialise les actions à partir d'une liste décrivant chaque action.

        Paramètres:
        actions (list): Une liste de dictionnaires représentant les actions.

        Traitement:
        - Initialise la liste `self.actions` en tant que liste d'objets 'Action'.
        - Pour chaque dictionnaire dans `actions`, tente de créer une instance d'Action via `ActionFactory.action_from_dict`.
        - Ajoute l'action créée à la liste `self.actions`.
        - Si une erreur de type `ValueError` est levée lors de la création d'une action,
          un message est enregistré dans les journaux de QGIS avec un niveau d'avertissement (Qgis.Warning).
        - Met à jour `self.tick_end` avec la valeur la plus élevée de la propriété `end_at` parmi toutes les actions,
          avec une valeur par défaut de 0.
        - La méthode émet un signal contenant le tick le plus elever pour l'interface.

        Exceptions:
        - Enregistre une erreur dans le journal si une action ne peut pas être créée à partir du dictionnaire fourni.
        """
        self.actions: list['Action'] = []
        for action_dict in actions:
            try:
                action = ActionFactory.action_from_dict(action_dict)
                self.actions.append(action)
            except ValueError as e:
                QgsMessageLog.logMessage(f"Erreur lors de la création d'une action : {e}", "Trace QGIS", level=Qgis.Warning)

        self.tick_end = max((action.end_at for action in self.actions), default=0)
        self.signal_tick_reset.emit(self.tick_end)

    def get_active_actions(self) -> list['Action']:
        """
        Retourne toutes les actions actives par rapport au tick actuel

        Retour :
            list['Action']: Liste des actions actives.
        """
        return [action for action in self.actions if action.is_active_at(self.tick)]

    def need_refresh_categories(self) -> bool:
        """
        Vérifie si une mise à jour des catégories est nécessaire.

        Retourne True si au moins une des entités nécessite une mise à jour de catégorie.
        """
        return any(map_entity.get_need_refresh_category() for map_entity in self.map_entities.values())

    def map_entities_need_refresh_labels(self) -> list:
        """
        Retourne une liste de map_entities qui nécessitent une mise à jour de leur étiquette.
        """
        return [
            map_entity
            for map_entity in self.map_entities.values()
            if map_entity.get_need_update_label()
        ]

    def apply_renderer(self):
        """
        Génère la liste des catégories pour le layer des entitées
        """
        categories = []

        for mapEntity in self.map_entities.values():
            categories.append(mapEntity.get_category())

        # Applique un rendu catégorisé basé sur l'attribut "icon"
        renderer = QgsCategorizedSymbolRenderer("id", categories)
        self.layer.setRenderer(renderer)

    def apply_trace_renderer(self):
        """
        Génère la liste des catégories pour le layer des mouvements des entitées, elle génères une couleur unique
        en fonction des ID des entitées
        """
        if not self.layer_trace:
            return

        categories = []

        # Extraire les entités actuelles pour connaître les IDs présents
        for mapEntity in self.map_entities.values():
            symbol = QgsLineSymbol.createSimple({
                'color': Utils.generate_random_color(mapEntity.get_id()),
                'width': '0.8'
            })
            category = QgsRendererCategory(mapEntity.get_id(), symbol, f"Trace {mapEntity.get_name()}")
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("id", categories)
        self.layer_trace.setRenderer(renderer)

    def refresh(self) -> bool:
        """
        Permet d'executer les actions en fonction du tick actuel et de passer au suivant.

        La méthode émet un signal contenant le tick actuel pour l'interface.

        Retourne:
            bool: True si la méthode a réussi à poursuivre la mise à jour, sinon False.
        """
        if self.tick > self.tick_end:
            self.stop_timer()
            return False

        self.reset_before_refresh()

        self.refresh_action()
        self.refresh_line()
        self.refresh_focus()

        self.signal_tick_changed.emit(self.tick)

        self.tick += 1
        return True

    def go_to_tick(self, to: int):
        """
        Rejous toutes les actions de 0 pour aller jusque l'étape tick "to"

        Paramètres:
        to (int): L'étape cible jusqu'à laquelle le processus doit avancer.

        Comportement:
        - Réinitialise les entités cartographiques en appelant leur fonction reset.
        - Débute une édition de la couche trace, vide ses données, et valide les changements.
        - Réinitialise et recharge les entités.
        - Met à jour le style ou le rendu à utiliser.
        - Avance jusqu'à l'étape cible en réinitialisant et en actualisant l'état à chaque tick.
        - Effectue une actualisation finale pour synchroniser avec l'état atteint.

        Renvoie:
        bool: Retourne True après avoir procédé avec succès au déplacement jusqu'à l'étape spécifiée.
        """
        for map_entity in self.map_entities.values():
            map_entity.reset()

        self.layer_trace.startEditing()
        self.layer_trace.dataProvider().truncate()
        self.layer_trace.commitChanges()

        self.entities_loaded = {}
        self.apply_renderer()

        self.tick = 0
        while self.tick < to:
            self.reset_before_refresh()
            self.refresh_action(True)
            self.tick += 1

        self.refresh()

        return True

    def reset_before_refresh(self):
        """
        Réinitialise les entités et leurs attributs visuels avant un rafraîchissement.

        Efface toutes les lignes actuelles. Parcourt les entités mappées et réinitialise leurs propriétés visuelles comme suit :
        - Réinitialise le texte des entités.
        - En cas de nécessité, réinitialise l'icône des entités après une action de changement d'icône.
        - En cas de nécessité, réinitialise la mise en surbrillance des entités après une action de surbrillance.
        - En cas de nécessité, réinitialise l'image de fond des entités après une action sur l'arrière-plan.
        """
        self.lines = []
        for mapEntity in self.map_entities.values():
            mapEntity.reset_text()
            if self.in_last_action('ActionChangeIcon'):
                mapEntity.reset_icon()
            if self.in_last_action('ActionHighlight'):
                mapEntity.reset_highlight()
            if self.in_last_action('ActionBackground'):
                mapEntity.reset_background_image()

    def in_last_action(self, action_name: str) -> bool:
        """
        Détermine si une action spécifique a eu lieu au dernier tick.

        Paramètres:
        action_name (str): Le nom de la classe de l'action pour laquelle vérifier l'occurrence.

        Retourne:
        bool: Retourne True si l'action spécifiée a eu lieu à la fin du dernier tick. Sinon, retourne False.

        Exceptions:
        ValueError: Exception lancée si le nom de l'action donné ne correspond pas à une classe d'action reconnue.
        """
        # Dictionnaire des classes possibles
        from ..actions.action_change_icon import ActionChangeIcon
        from ..actions.action_highlight import ActionHighlight
        from ..actions.action_background import ActionBackground

        action_classes = {
            "ActionChangeIcon": ActionChangeIcon,
            "ActionHighlight": ActionHighlight,
            "ActionBackground": ActionBackground,
        }

        action_type = action_classes.get(action_name)
        if action_type is None:
            raise ValueError(f"Action '{action_name}' non reconnue.")

        return any(
            isinstance(act, action_type) and (act.end_at + 1) == self.tick
            for act in self.actions
        )


    def refresh_action(self, fast: bool = False):
        """
        Partie du refresh qui traite les actions.

        Paramètres :
        fast (bool) : Indique si l'actualisation doit être rapide ou complète.
                      Si True, les actions liées a l'interface ne sont pas executée.

        Procédé :
        1. Récupère et trie les actions en fonction des prioritées.
        2. Exécute chaque action active si son entité associée n'est pas encore chargée,
           sinon enregistre un message dans les journaux QGIS.
        3. Rafraîchit le chargement des ressources.
        4. Si l'actualisation n'est pas rapide (fast=False) :
            - Vérifie si les catégories doivent être rafraîchies et applique le moteur de rendu si nécessaire.
            - Met à jour la position des étiquettes pour les entités de la carte nécessitant une actualisation en fonction des configurations.
            - Déclenche le repaint des couches (principale et de trace).
        """
        actions_active = self.get_active_actions()
        actions_active = Utils.sort_actions(actions_active)

        for action in actions_active:
            if not self.is_loaded_by_id(action.entity_id):
                action.execute()
            else:
                QgsMessageLog.logMessage("Action non traité car entity load\n" + str(action), "Trace QGIS", level=Qgis.Info)

        self.refresh_load()

        if not fast:
            if self.need_refresh_categories():
                self.apply_renderer()

            for map_entity in self.map_entities_need_refresh_labels():
                if not self.is_loaded(map_entity):
                    map_entity.update_label_position(self.show_name, self.show_position)
                else:
                    map_entity.update_label_position(False, False)

            self.layer.triggerRepaint()
            self.layer_trace.triggerRepaint()


    def refresh_line(self):
        """
        Partie du refresh qui traite les lignes entre entitées.
        """
        self.layer_lines.startEditing()

        self.layer_lines.dataProvider().truncate()
        if self.lines:
            for line in self.lines:
                self.draw_line_between(line[0], line[1])

        self.layer_lines.commitChanges()

        self.layer_lines.triggerRepaint()

    # TIMER SECTION
    def start_timer(self):
        """
        Démarre le minuteur à une vitesse déterminée par l'intervalle et la vitesse actuelle.

        La méthode émet un signal indiquant le départ du minuteur.
        """
        self.timer.start(self.interval // self.speed)
        self.signal_timer_changed.emit(True)

    def change_interval_timer(self, speed: int):
        """
        Modifie l'intervalle du minuteur en fonction de la vitesse donnée.

        Arguments:
        speed (int): La vitesse souhaitée
        """
        self.speed = speed
        if self.speed <= 0:
            self.speed = 1  # éviter division par 0
        self.timer.setInterval(1000 // self.speed)

    def stop_timer(self):
        """
        Arrête le minuteur en cours d'exécution.

        La méthode émet un signal indiquant l'arret du minuteur.
        """
        self.timer.stop()
        self.signal_timer_changed.emit(False)

    def toggle_timer(self, is_active: bool = True):
        """
        Cette méthode permet de basculer l'état du minuteur.
        Si le minuteur est actif, il est arrêté.
        Sinon, il le démarre
        """
        if is_active:
            self.start_timer()
        else:
            self.stop_timer()

    # INTERFACE SECTION
    def draw_line_between(self, idFeature1: int, idFeature2: int):
        """
        Dessine une ligne directe entre deux entités sur layer_lines.
        """
        feature1 = self.map_entities.get(idFeature1)
        feature2 = self.map_entities.get(idFeature2)
        if not feature1 or not feature2:
            QgsMessageLog.logMessage(f"Feature {idFeature1} ou {idFeature2} est introuvable.", level=Qgis.Warning)
            return

        geom1 = feature1.feature.geometry()
        geom2 = feature2.feature.geometry()

        if not geom1.isGeosValid() or not geom2.isGeosValid() or geom1.isEmpty() or geom2.isEmpty():
            QgsMessageLog.logMessage(
                f"Une ou les deux géométries de {idFeature1} et {idFeature2} sont invalides ou vides.",
                level=Qgis.Warning)
            return

        point1 = geom1.asPoint()
        point2 = geom2.asPoint()

        if point1 == point2:
            QgsMessageLog.logMessage(
                f"Les deux points sont identiques, aucune ligne tracée.",
                level=Qgis.Warning)
            return

        line_geom = QgsGeometry.fromPolylineXY([point1, point2])

        line_feature = QgsFeature()
        line_feature.setGeometry(line_geom)
        self.layer_lines.addFeature(line_feature)

    def exist_line(self, id1, id2):
        """
        Vérifie si une ligne existante connecte deux identifiants donnés.

        Paramètres:
        id1: Premier identifiant à vérifier.
        id2: Deuxième identifiant à vérifier.

        Retourne:
        bool: True si une ligne existante connecte id1 et id2, sinon False.
        """
        return any(line == [id1, id2] for line in self.lines)

    def add_line(self, idFeature1: int, idFeature2: int):
        """
        Ajoute une ligne entre deux entités si elle n'existe pas déjà.

        Paramètres:
        idFeature1 (int): Identifiant de la première entité.
        idFeature2 (int): Identifiant de la seconde entité.

        Description:
        Vérifie si une ligne reliant les deux entités identifiées par `idFeature1` et `idFeature2` existe déjà.
        Si elle n'existe pas, ajoute une nouvelle ligne à la liste `lines` reliant ces deux entités"""
        if not self.exist_line(idFeature1, idFeature2):
            self.lines.append([idFeature1, idFeature2])

    def remove_line(self, id1, id2):
        """
        Supprime une ligne spécifique entre deux identifiants donnés.

        Paramètres:
        id1 : Identifiant du premier point de la ligne.
        id2 : Identifiant du second point de la ligne.

        Comportement:
        Parcourt la liste des lignes pour identifier une ligne composée des deux identifiants spécifiés.
        Si une correspondance exacte est trouvée, la ligne est supprimée de la liste.
        """
        for line in self.lines:
            if set(line) == {id1, id2}:
                self.lines.remove(line)

    def set_focus(self, id_entity: int):
        """
        Définit la mise au point de l'entité spécifiée.

        Paramètres:
        id_entity (int): Identifiant de l'entité.
        """
        self.focus = id_entity

    def refresh_focus(self):
        """
        Actualise le focus sur l'entité courante si elle est définie.

        Si l'entité existe, calcule le centre de sa géométrie, repositionne le centre de la carte sur ce point
        et rafraîchit l'affichage du canevas cartographique.
        """
        if not self.focus:
            return

        focusEntity = self.map_entities[self.focus]
        if not focusEntity:
            self.focus = False
            return

        center = focusEntity.feature.geometry().centroid().asPoint()
        iface.mapCanvas().setCenter(center)
        iface.mapCanvas().refresh()

    def update_all_labels(self):
        """
        Mise à jour de toutes les étiquettes des entités de la carte.

        Parcourt toutes les entités présentes dans map_entities et
        met à jour la position de leur étiquette associée en appelant
        la méthode update_label_position() pour chaque entité.
        """
        for map_entity in self.map_entities.values():
            if not self.is_loaded(map_entity):
                map_entity.update_label_position(self.show_name, self.show_position)
            else:
                map_entity.update_label_position(False, False)

    def toggle_show_information_name(self, state: bool):
        """
        Permet d'afficher ou non le nom de l'entitée sur la carte

        Paramètres:
        state (bool): Détermine si le nom sera affiché ou masqué.
        """
        self.show_name = state
        self.update_all_labels()

    def toggle_show_information_position(self, state):
        """
        Permet d'afficher ou non la position de l'entitée sur la carte

        Paramètres:
        state (bool): Détermine si le position sera affiché ou masqué.
        """
        self.show_position = state
        self.update_all_labels()


    def load_entity(self, entity: 'MapEntity', entity_load: 'MapEntity'):
        """
        Permet de charger une entité dans une autre.

        Paramètres:
        entity (MapEntity): L'entité à charger.
        entity_load (MapEntity): L'entité dans lequel elle est charger.

        Comportement:
        - Vérifie si l'identifiant de l'entité principale est déjà dans le dictionnaire des entités chargées.
        - Si ce n'est pas le cas, initialise une nouvelle liste pour cet identifiant.
        - Ajoute l'entité associée dans la liste des entités chargées pour l'entité principale, si elle n'est pas déjà incluse.
        """
        entity_id = entity.get_id()
        if entity_id not in self.entities_loaded:
            self.entities_loaded[entity_id] = []

        if entity_load not in self.entities_loaded[entity_id]:
            self.entities_loaded[entity_id].append(entity_load)

    def unload_entity(self, entity: 'MapEntity', entity_load: 'MapEntity'):
        """
        Permet de décharger une entité

        Paramètres:
        entity : MapEntity
            L'entité à décharger.
        entity_load : MapEntity
            L'entité cible qui doit être retirée du groupe d'entités chargées.

        Description:
        Vérifie si l'entité source est présente dans les entités chargées. Si elle l'est, retire l'entité cible du groupe associé. Si le groupe devient vide après le retrait, il est complètement supprimé.
        """
        group_id = entity.get_id()
        target_id = entity_load.get_id()

        if group_id in self.entities_loaded:
            self.entities_loaded[group_id] = [
                e for e in self.entities_loaded[group_id] if e.get_id() != target_id
            ]
            if not self.entities_loaded[group_id]:
                del self.entities_loaded[group_id]

    def is_loaded(self, entity_load: 'MapEntity', in_entity: 'MapEntity' = None) -> bool:
        """
        Vérifie si une entité est chargée dans une entité ou simplement chargé

        Paramètres:
        - entity_load : 'MapEntity'
          L'entité dont il faut vérifier le chargement.
        - in_entity : 'MapEntity', optionnel (par défaut None)
          Le groupe dans lequel vérifier si l'entité est chargée. Si None, vérifie dans tous les groupes.

        Retourne:
        - bool : True si l'entité est chargée, False sinon.
        """
        if in_entity is None:
            # Vérifie si l'entité est chargée dans n'importe quel groupe
            return any(entity_load in loaded_list for loaded_list in self.entities_loaded.values())
        else:
            group_id = in_entity.get_id()
            return entity_load in self.entities_loaded.get(group_id, [])

    def is_loaded_by_id(self, entity_id: str, in_entity_id: str = None) -> bool:
        """
        Vérifie si une entité avec un identifiant donné est chargée.

        Paramètres:
        entity_id: str
            L'identifiant de l'entité à vérifier.
        in_entity_id: str, optionnel
            L'identifiant d'une entité spécifique où effectuer la recherche.

        Retourne:
        bool
            True si l'entité est chargée, False autrement.
        """
        if in_entity_id is None:
            return any(
                any(e.get_id() == entity_id for e in loaded_list)
                for loaded_list in self.entities_loaded.values()
            )
        else:
            return any(
                e.get_id() == entity_id for e in self.entities_loaded.get(in_entity_id, [])
            )

    def refresh_load(self):
        """
       Partie du refresh qui traite les entitées chargée
       """
        ids = [entity.get_id() for entity in self.map_entities.values() if self.is_loaded(entity)]

        if ids:
            self.layer.setSubsetString("id NOT IN (" + ", ".join(str(id_) for id_ in ids) + ")")
            for entity_id, entity_list in self.entities_loaded.items():
                entity = self.map_entities.get(entity_id)
                if entity:
                    names = [entity_loaded.get_name() for entity_loaded in entity_list]
                    text = "Stock: "
                    text += ", ".join(names)
                    entity.append_text(text)
        else:
            self.layer.setSubsetString("")


    def log_trace(self, entity: 'MapEntity', old_point: QgsPointXY):
        """
        Enregistre une trace d'un déplacement d'entité dans la couche de trace.

        Paramètres:
        entity (MapEntity): L'entité cartographique concernée.
        old_point (QgsPointXY): Le point précédent de l'entité.

        Cette méthode crée une nouvelle entité dans la couche de trace représentant
        le déplacement de l'entité cartographique. La géométrie de la nouvelle entité
        est une ligne reliant l'ancien point à la position actuelle de l'entité. Les
        attributs "id" et "nom" de l'entité sont également définis.
        """
        feature = QgsFeature(self.layer_trace.fields())
        feature.setGeometry(QgsGeometry.fromPolylineXY([old_point, entity.feature.geometry().asPoint()]))
        feature.setAttribute("id", entity.get_id())
        feature.setAttribute("nom", entity.get_name())
        self.layer_trace.dataProvider().addFeature(feature)

    def unload(self):
        """
        Décharge les ressources, déconnecte les signaux et libère les couches et entités cartographiques associées.

        Cette méthode effectue les actions suivantes :
        - Arrête le minuteur utilisé par l'application.
        - Déconnecte les signaux liés au changement d'extension de la carte et au rafraîchissement.
        - Vide toutes les entités cartographiques et libère les ressources associées.
        - Supprime les couches de points, de lignes et de traces si elles existent.
        - Supprime le groupe "Trace QGIS" du projet QGIS.
        - Réinitialise l'instance singleton de LayerTraceQGIS à None.
        """
        self.stop_timer()
        iface.mapCanvas().extentsChanged.disconnect(self.update_all_labels)
        self.timer.timeout.disconnect(self.refresh)

        self.map_entities.clear()
        self.entities_loaded.clear()

        for map_entity in self.map_entities.values():
            map_entity.unload()

        # Supprimer proprement la couche des points
        if self.layer is not None:
            QgsProject.instance().removeMapLayer(self.layer.id())
            self.layer = None

        # Supprimer proprement la couche des lignes
        if self.layer_lines is not None:
            QgsProject.instance().removeMapLayer(self.layer_lines.id())
            self.layer_lines = None

        if self.layer_trace:
            QgsProject.instance().removeMapLayer(self.layer_trace.id())
            self.layer_trace = None

        # Supprimer le groupe
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Trace QGIS")
        if group:
            parent = group.parent()
            if parent:
                parent.removeChildNode(group)

        LayerTraceQGIS._instance = None

    @staticmethod
    def get_map_entity(entity_id: int):
        return LayerTraceQGIS.get_instance().map_entities.get(entity_id)

    @staticmethod
    def get_current_tick() -> int:
        return int(LayerTraceQGIS.get_instance().tick)

    @staticmethod
    def static_load_entity(entity: 'MapEntity', entity_load: 'MapEntity'):
        LayerTraceQGIS.get_instance().load_entity(entity, entity_load)

    @staticmethod
    def static_unload_entity(entity: 'MapEntity', entity_load: 'MapEntity'):
        LayerTraceQGIS.get_instance().unload_entity(entity, entity_load)

    @staticmethod
    def static_is_loaded(entity_load: 'MapEntity', in_entity: 'MapEntity' = None):
        LayerTraceQGIS.get_instance().is_loaded(entity_load, in_entity)