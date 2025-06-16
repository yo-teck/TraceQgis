from qgis.utils import iface
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsMarkerSymbol,
    QgsRasterMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsOuterGlowEffect,
    QgsRendererCategory
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel
from qgis.PyQt.QtGui import QFont, QColor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .layer_trace_qgis import LayerTraceQGIS

class MapEntity:

    def __init__(self, id: str, name: str, url_icon: str, latitude: float, longitude: float, altitude: float = 0, size: float = 5):
        """
        Initialise une instance avec ses propriétés spécifiques.

        Paramètres:
        id (str): Identifiant unique de l'instance.
        name (str): Nom de l'instance.
        url_icon (str): URL de l'icône associée.
        latitude (float): Latitude pour l'instance.
        longitude (float): Longitude pour l'instance.
        altitude (float, optionnel): Altitude pour l'instance, par défaut à 0.
        size (float, optionnel): Taille de l'objet, par défaut à 5.

        Attributs:
        id: Stocke l'identifiant de l'instance.
        name: Stocke le nom de l'instance.
        url_icon: Stocke l'URL de l'icône.
        url_icon_default: Valeur par défaut pour l'URL de l'icône.
        size: Taille de l'instance en tant que nombre décimal.
        size_default: Taille par défaut de l'instance.
        angle: Angle de rotation de l'instance, initialisé à 0.
        opacity: Niveau d'opacité de l'instance, initialisé à 1.
        highlight: Met en évidence une sélection, initialisé à None.
        background_image: Image d'arrière-plan, initialisé à None.
        latitude_default: Latitude initiale par défaut.
        longitude_default: Longitude initiale par défaut.
        altitude: Altitude actuelle de l'instance.
        altitude_default: Altitude par défaut de l'instance.
        texts: Liste des textes associés à l'instance.

        need_refresh_category: Détermine si une catégorie nécessite une mise à jour, initialisé à False.
        need_update_label: Indique si une étiquette doit être mise à jour, initialisé à False.

        feature: Contient un objet QgsFeature avec un identifiant et un nom comme attributs, et une géométrie représentant le point XY.
        label: Étiquette configurée pour le point.
        category: Catégorie calculée automatiquement pour organiser cette instance.

        Méthodes:
        create_label(): Crée une étiquette liée à cet objet.
        update_label_position(refresh_category, refresh_feature): Met à jour la position de l'étiquette selon les paramètres fournis.
        generate_category(): Génère une catégorie spécifique associée à cet objet.
        """
        self.id = id
        self.name = name
        self.url_icon = url_icon
        self.url_icon_default = url_icon
        self.size = float(size)
        self.size_default = float(size)
        self.angle = 0
        self.opacity = 1
        self.highlight = None
        self.background_image = None
        self.latitude_default = latitude
        self.longitude_default = longitude
        self.altitude = altitude
        self.altitude_default = altitude
        self.texts = []

        self.need_refresh_category = False
        self.need_update_label = False

        self.feature = QgsFeature()
        self.feature.setAttributes([id, name])
        self.feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude)))

        self.label = self.create_label()
        self.update_label_position(False, False)

        self.category = self.generate_category()

    def get_latitude(self) -> float:
        """
        Renvoie la latitude du point géométrique.

        Retourne:
            float: La latitude du point.
        """
        point = self.feature.geometry().asPoint()
        return point.y()  # y correspond à la latitude

    def get_longitude(self) -> float:
        """
        Récupère la longitude d'une entité géographique.

        Retourne:
            float: La coordonnée x (longitude) du point géométrique associé à l'entité.
        """
        point = self.feature.geometry().asPoint()
        return point.x()

    def get_altitude(self) -> float:
        """
        Renvoie l'altitude actuelle.

        Retourne:
            float: La valeur de l'altitude.
        """
        return self.altitude

    def set_altitude(self, value: float):
        """
        Définit l'altitude à la valeur spécifiée.

        Paramètres:
        value (float): La nouvelle valeur de l'altitude.
        """
        self.altitude = value

    def get_url_icon(self) -> str:
        """
        Retourne l'icône d'URL.

        Renvoie:
        Une chaîne de caractères représentant l'icône d'URL.
        """
        return self.url_icon

    def set_url_icon(self, value: str, need_refresh_category: bool = True):
        """
        Définit l'icône d'URL et met à jour l'état de rafraîchissement de la catégorie si nécessaire.

        Paramètres:
        value (str): L'URL de l'icône à affecter.
        need_refresh_category (bool): Indique s'il est nécessaire de marquer la catégorie pour un rafraîchissement. Par défaut à True.
        """
        self.url_icon = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_url_icon(self):
        """
        Réinitialise l'icône de l'URL à sa valeur par défaut.

        Cette méthode remplace l'icône actuelle de l'URL par l'icône par défaut spécifiée dans l'attribut url_icon_default.
        """
        self.set_url_icon(self.url_icon_default)

    def get_background_image(self) -> str:
        """
        Renvoie l'image d'arrière-plan actuelle.

        Cette méthode retourne le chemin ou l'identifiant de l'image d'arrière-plan actuellement définie.

        Retourne:
            str: L'image d'arrière-plan.
        """
        return self.background_image

    def set_background_image(self, value: str|None, need_refresh_category: bool = True):
        """
        Définit l'image d'arrière-plan de l'objet.

        Parameters:
         value (str | None): Chemin ou identifiant de l'image à définir comme arrière-plan, ou None pour supprimer l'image existante.
         need_refresh_category (bool): Indique si une actualisation de la catégorie est nécessaire après la modification de l'image d'arrière-plan. La valeur par défaut est True.
        """
        self.background_image = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_background_image(self):
        """
        Réinitialise l'image d'arrière-plan à sa valeur par défaut.

        Cette méthode supprime l'image d'arrière-plan actuellement définie
        en assignant une valeur nulle, indiquant qu'aucune image n'est utilisée.
        """
        self.set_background_image(None)

    def get_highlight(self) -> bool:
        """
        Renvoie l'état de mise en évidence.

        Retourne:
        bool: La valeur de l'attribut highlight indiquant si un élément est mis en évidence.
        """
        return self.highlight

    def set_highlight(self, value: str|None, need_refresh_category: bool = True):
        """
        Définit la valeur de mise en surbrillance et met à jour l'état de rafraîchissement de la catégorie si nécessaire.

        Arguments:
        value: Une chaîne ou None représentant la valeur de mise en surbrillance à définir.
        need_refresh_category: Un booléen indiquant si la catégorie doit être rafraîchie. Par défaut, True.
        """
        self.highlight = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_highlight(self):
        """
        Réinitialise la mise en surbrillance de l'objet.

        Définit la mise en surbrillance sur "None" pour indiquer qu'aucune
        mise en surbrillance n'est actuellement active.
        """
        self.set_highlight(None)

    def get_size(self) -> float:
        """
        Retourne la taille de l'objet.

        Retour :
            float : La taille de l'objet.
        """
        return self.size

    def set_size(self, value: float, need_refresh_category: bool = True):
        """
        Définit la taille et met à jour l'état pour indiquer si une actualisation de catégorie est nécessaire.

        Paramètres:
        value (float): La nouvelle taille à définir.
        need_refresh_category (bool): Indique si une actualisation de catégorie est nécessaire. Par défaut, True.
        """
        self.size = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_size(self):
        """
        Réinitialise la taille d'un objet à la valeur par défaut.

        Cette méthode met à jour la taille actuelle de l'objet en utilisant
        la valeur par défaut définie dans l'attribut `size_default`.
        """
        self.set_size(self.size_default)

    def get_texts(self) -> list[str]:
        """
        Récupère une liste de textes.

        Renvoie :
            list[str] : Une liste de chaînes de caractères.
        """
        return self.texts

    def set_texts(self, value: list[str]):
        """
        Définit les textes avec une liste de chaînes spécifiées.

        Paramètres :
        value (list[str]) : Liste de chaînes à assigner à l'attribut texts.

        Comportement :
        - Met à jour l'attribut texts avec la liste fournie.
        - Indique que l'étiquette nécessite une mise à jour en définissant l'indicateur approprié à True.
        """
        self.texts = value
        self.set_need_update_label(True)

    def append_text(self, text: str):
        """
        Ajoute un texte à la liste des textes et met à jour l'état de l'étiquette.

        Paramètres:
        text (str): Le texte à ajouter.
        """
        self.texts.append(text)
        self.set_need_update_label(True)

    def reset_text(self):
        """
        Réinitialise les textes de l'objet.

        Vérifie si des textes existent. Si c'est le cas, remplace les textes existants
        par une liste vide.
        """
        if self.texts:
            self.set_texts([])

    def get_feature(self) -> str:
        """
        Renvoie la valeur de l'attribut 'feature'.

        Retour:
            str: La valeur de 'feature'.
        """
        return self.feature

    def get_need_refresh_category(self) -> bool:
        """
        Retourne la valeur de l'attribut need_refresh_category.

        Renvoie:
         bool: La valeur de l'attribut need_refresh_category.
        """
        return self.need_refresh_category

    def set_need_refresh_category(self, value: bool):
        """
        Définit la nécessité de rafraîchir la catégorie.

        Paramètres:
        value (bool): Indique si la catégorie doit être marquée comme nécessitant un rafraîchissement.

        Comportement:
        Si l'attribut 'need_refresh_category' est actuellement défini sur False, il sera mis à jour avec la valeur spécifiée.
        """
        if self.need_refresh_category is False:
            self.need_refresh_category = value

    def get_need_update_label(self) -> bool:
        """
        Renvoie l'état actuel de l'attribut need_update_label.

        Retourne:
            bool : La valeur de l'attribut need_update_label indiquant si une mise à jour de l'étiquette est nécessaire.
        """
        return self.need_update_label

    def set_need_update_label(self, value: bool):
        """
        Définit si l'attribut need_update_label doit être mis à jour.

        Paramètres:
        value (bool): Valeur indiquant si l'attribut need_update_label doit être mis à jour.
        """
        if self.need_update_label is False:
            self.need_update_label = value

    def get_name(self) -> str:
        """
        Renvoie le nom.

        Retour:
            str: Le nom.
        """
        return self.name

    def set_name(self, value: str):
        """
        Définit le nom de l'objet.

        Paramètres:
        value (str): Le nom à attribuer à l'objet.
        """
        self.name = value

    def get_angle(self) -> float:
        """
        Renvoie l'angle actuel.

        Retour:
        float : La valeur de l'angle.
        """
        return self.angle

    def set_angle(self, value: float, need_refresh_category: bool = True):
        """
        Définit l'angle à une valeur spécifiée et, si nécessaire, met à jour l'état de rafraîchissement de la catégorie.

        Paramètres:
        value (float): La valeur de l'angle à définir.
        need_refresh_category (bool): Indique si la catégorie doit être marquée pour un rafraîchissement. La valeur par défaut est True.
        """
        self.angle = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_angle(self):
        """
        Réinitialise l'angle de l'objet à zéro.

        Cette méthode modifie l'angle actuel de l'objet en le fixant à 0.
        Elle utilise la méthode interne set_angle pour effectuer cette opération.
        """
        self.set_angle(0)

    def get_id(self) -> str:
        """
        Cette méthode retourne l'identifiant unique associé à l'objet.

        Retour:
            str: L'identifiant unique de l'objet.
        """
        return self.id

    def get_opacity(self) -> float:
        """
        Renvoie l'opacité actuelle.

        Retourne:
            float: La valeur de l'opacité.
        """
        return self.opacity

    def set_opacity(self, value: float, need_refresh_category: bool = True):
        """
        Définit l'opacité de l'objet.

        Paramètres:
        value (float): La nouvelle valeur d'opacité.
        need_refresh_category (bool, optionnel): Indique si une actualisation de la catégorie est nécessaire. Valeur par défaut à True.
        """
        self.opacity = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_opacity(self):
        """
        Réinitialise l'opacité de l'objet.
        Fixe l'opacité à la valeur maximale (1).
        """
        self.set_opacity(1)

    def get_category(self):
        """
        Renvoie la catégorie après avoir vérifié si une mise à jour est nécessaire.

        Si la catégorie nécessite une mise à jour (indiquée par l'attribut need_refresh_category),
        elle est régénérée en appelant la méthode generate_category. Une fois mise à jour,
        la propriété need_refresh_category est définie sur False pour indiquer que la catégorie est actuelle.

        Retourne:
        La catégorie actualisée ou non actualisée selon l'état de need_refresh_category.
        """
        if self.need_refresh_category:
            self.category = self.generate_category()
            self.need_refresh_category = False

        return self.category


    def generate_category(self) -> QgsRendererCategory:
        """
        Génère une catégorie de rendu basée sur les propriétés de l'objet.

        Cette méthode crée un objet QgsRendererCategory utilisant un symbole configuré avec plusieurs couches symboliques en fonction des propriétés définies :
        - Une taille et une opacité générales pour le symbole.
        - Ajout d'une couche de surbrillance avec un effet Glow si la propriété `highlight` est définie.
        - Ajout d'une couche d'arrière-plan avec une image raster si `background_image` est spécifié.
        - Ajout de la couche principale du symbole basée sur l'image spécifique définie dans `url_icon`.

        Retourne:
        Un objet QgsRendererCategory contenant le symbole configuré et les propriétés associées.
        """
        symbol = QgsMarkerSymbol()
        symbol.deleteSymbolLayer(0)
        symbol.setSize(self.size)
        symbol.setOpacity(self.opacity)

        if self.highlight:
            # appliquer un effet blur sur glow_layer (si possible)
            glow_effect = QgsOuterGlowEffect()
            glow_effect.setColor(QColor(self.highlight))
            glow_effect.setSpread(5)
            glow_effect.setBlurLevel(1)
            glow_layer = QgsSimpleMarkerSymbolLayer()
            glow_layer.setPaintEffect(glow_effect)

            symbol.appendSymbolLayer(glow_layer)

        if self.background_image:
            background_layer = QgsRasterMarkerSymbolLayer(self.background_image)
            background_layer.setSize(self.size * 3)
            background_layer.setOpacity(0.5)
            symbol.appendSymbolLayer(background_layer)
            symbol.setSize(self.size * 3)  # Taille du symbole

        # Créer un QgsRasterMarkerSymbolLayer avec le fichier image
        raster_layer = QgsRasterMarkerSymbolLayer(self.url_icon)  # mapEntity.url_icon est le chemin vers l'image
        raster_layer.setSize(self.size)
        raster_layer.setAngle(self.angle)
        symbol.appendSymbolLayer(raster_layer)

        return QgsRendererCategory(self.id, symbol, self.name)

    def move_to(self, lat: float, lon: float, alti: float):
        """
        Déplace l'entité vers nouvelles coordonnées géographiques et met à jour l'altitude.

        Paramètres:
        lat (float): La latitude de la nouvelle position.
        lon (float): La longitude de la nouvelle position.
        alti (float): La nouvelle altitude.

        Actions:
        - Définit la nouvelle géométrie de l'entité avec les coordonnées données.
        - Met à jour les données de la couche pour refléter la nouvelle position.
        - Met à jour la propriété `altitude` de l'entité.
        - Indique qu'une mise à jour de l'étiquette est nécessaire.
        """
        self.feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        LayerTraceQGIS.get_instance().layer.dataProvider().changeGeometryValues({self.feature.id(): self.feature.geometry()})
        self.altitude = alti
        self.set_need_update_label(True)

    def move_to_entity(self, map_entity):
        """
        Déplace l'objet actuel vers l'entité spécifiée en utilisant ses coordonnées.

        Paramètres:
        map_entity : Une entité vers laquelle bougée
        """
        self.move_to(map_entity.get_latitude(), map_entity.get_longitude(), map_entity.altitude)

    def reset(self):
        """
        Réinitialise les attributs de l'objet à leurs valeurs par défaut.

        Les méthodes appelées effectuent les actions suivantes :
        - Réinitialise l'icône URL.
        - Réinitialise la position de l'objet.
        - Réinitialise la taille de l'objet.
        - Réinitialise le texte de l'objet.
        - Réinitialise l'angle de rotation de l'objet.
        - Réinitialise l'opacité de l'objet.
        - Réinitialise la mise en surbrillance de l'objet.
        - Réinitialise l'image d'arrière-plan de l'objet.
        - Réinitialise l'étiquette associée à l'objet.
        """
        self.reset_url_icon()
        self.reset_position()
        self.reset_size()
        self.reset_text()
        self.reset_angle()
        self.reset_opacity()
        self.reset_highlight()
        self.reset_background_image()
        self.reset_label()

    def reset_position(self):
        """
        Réinitialise la position de l'objet aux valeurs par défaut.
        """
        self.move_to(self.latitude_default, self.longitude_default, self.altitude_default)

    def create_label(self) -> QLabel:
        """
        Créer une étiquette QLabel avec des propriétés spécifiques, telles que la police, le style de bordure, la transparence du fond et des événements de souris. Cette méthode retourne l'objet QLabel configuré.

        Retourne:
            QLabel: L'instance QLabel configurée.
        """
        label = QLabel(iface.mainWindow())
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("background-color: rgba(255, 255, 255, 200); border: 1px solid black;")
        label.setAttribute(Qt.WA_TransparentForMouseEvents)

        return label

    def reset_label(self):
        """
        Réinitialise l'étiquette en cours en la supprimant et en en créant une nouvelle.

        Cette méthode cache d'abord l'étiquette existante, détache son parent et supprime l'étiquette de la mémoire.
        Une nouvelle étiquette est ensuite recréée et marquée comme nécessitant une mise à jour.
        """
        self.hide_label()
        self.label.setParent(None)
        self.label.deleteLater()
        self.label = self.create_label()
        self.set_need_update_label(True)

    def update_label_position(self, show_name: bool, show_position: bool):
        """
        Met à jour la position et la visibilité du label associé à une fonctionnalité sur un canevas, en fonction des paramètres d'affichage donnés.

        Paramètres:
        show_name (bool): Indique si le nom de l'entité doit être affiché.
        show_position (bool): Indique si la position de l'entité doit être affichée.

        Comportement:
        - Affiche ou masque le label selon les paramètres d'affichage ou si du texte est déjà présent.
        - Calcule la position finale du label avec un décalage pour éviter l'obstruction du point d'entité.
        - Transforme la position géographique en coordonnées de pixels sur l'écran.
        - Prend en compte la largeur du panneau latéral dans l'application pour ajuster la position du label.
        - Vérifie si le label reste dans les limites visibles du canevas avant de l'afficher et de le positionner.
        - Ajuste la taille du label selon le texte généré.

        Ce processus assure que le label est correctement positionné à l'écran tout en s'adaptant aux contraintes d'affichage et aux décalages nécessaires pour éviter des chevauchements visuels.
        """
        self.need_update_label = False

        if show_name or show_position or self.texts:
            self.show_label()
        else:
            self.hide_label()
            return

        canvas = iface.mapCanvas()
        point = self.feature.geometry().asPoint()

        # Transforme la coordonnée en pixel écran
        screen_pos = canvas.mapSettings().mapToPixel().transform(point)

        # Décalage pour que le label n'obstrue pas le point
        # Récupère la position du canvas dans la fenêtre principale pour détecter le panneau latéral
        main_window = iface.mainWindow()
        canvas_pos_in_main = main_window.mapFromGlobal(canvas.mapToGlobal(canvas.rect().topLeft()))
        left_panel_width = canvas_pos_in_main.x()

        # Décalage pour que le label n'obstrue pas le point, ajusté avec le panneau gauche
        offset_x = left_panel_width + 20
        offset_y = 110

        # Position finale avec décalage
        final_x = int(screen_pos.x() + offset_x)
        final_y = int(screen_pos.y() + offset_y)

        # Dimensions visibles du canvas
        canvas_rect = canvas.rect()

        description = self.generate_description_label(show_name, show_position)

        # Vérifie si le label serait dans les limites du canvas
        if canvas_rect.contains(int(screen_pos.x()), int(screen_pos.y())):
            self.show_label()
            self.label.move(final_x, final_y)
            self.label.setText(description)
            self.label.adjustSize()
        else:
            self.hide_label()

    def generate_description_label(self, show_name: bool, show_position: bool) -> str:
        """
        Génère l'étiquette descriptive basée sur les paramètres fournis.

        Paramètres:
        show_name (bool): Indique si le nom doit être inclus dans la description.
        show_position (bool): Indique si la position (latitude, longitude, altitude) doit être incluse dans la description.

        Retourne:
        str: Une chaîne de caractères contenant la description générée.
        """
        description = ""
        if show_name:
            description += f"{self.get_name()}"

        if show_position:
            if description:
                description += "\n"
            description += f"Position: {self.get_latitude():.4f}, {self.get_longitude():.4f}, {self.get_altitude():}"

        if self.get_texts():
            if description:
                description += "\n"
            description += "\n".join(self.get_texts())

        return description

    def hide_label(self):
        """
        Masque l'étiquette.
        """
        self.label.setVisible(False)

    def show_label(self):
        """
        Affiche  l'étiquette
        """
        self.label.setVisible(True)

    def unload(self):
        """
        Décharge les éléments associés à l'instance de l'objet.

        Si l'objet possède une étiquette (`label`), cette méthode effectue les opérations suivantes :
        - Appelle la méthode `hide_label()` pour masquer l'étiquette.
        - Détache l'étiquette en retirant le parent défini avec `setParent(None)`.
        - Supprime l'étiquette avec `deleteLater`.
        - Réinitialise l'attribut `label` à `None`.
        """
        if self.label:
            self.hide_label()
            self.label.setParent(None)
            self.label.deleteLater()
            self.label = None
