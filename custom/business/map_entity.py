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
    """
        Classe MapEntity:
        Classe représentant une entité dans une carte géographique avec des attributs spécifiques, tels que son emplacement, son icône, sa taille, et d'autres propriétés. La classe fournit des fonctionnalités permettant d'interagir avec l'entité, comme la modification de sa position, la réinitialisation de ses attributs, ou l'ajout de texte associé.
    """

    def __init__(self, id: str, name: str, url_icon: str, latitude: float, longitude: float, altitude: float = 0, size: float = 5):
        """
        Initialise une instance de la classe.

        Paramètres:
        id (str): Identifiant unique de l'objet.
        name (str): Nom de l'objet.
        url_icon (str): Chemin vers l'icône de l'objet.
        latitude (float): Latitude géographique de l'objet.
        longitude (float): Longitude géographique de l'objet.
        altitude (float, optionnel): Altitude géographique de l'objet. Par défaut, 0.
        size (float, optionnel): Taille de l'objet. Par défaut, 5.

        Attributs:
        id (str): Identifiant unique de l'objet.
        name (str): Nom de l'objet.
        url_icon (str): Chemin de l'icône actuelle de l'objet.
        url_icon_default (str): Chemin de l'icône par défaut de l'objet.
        size (float): Taille actuelle de l'objet.
        size_default (float): Taille par défaut de l'objet.
        angle (float): Angle de l'objet. Par défaut, 0.
        opacity (float): Opacité de l'objet. Par défaut, 1.
        highlight: Contenu non défini pour la surbrillance.
        latitude_default (float): Latitude par défaut de l'objet.
        longitude_default (float): Longitude par défaut de l'objet.
        altitude (float): Altitude actuelle de l'objet.
        altitude_default (float): Altitude par défaut de l'objet.
        texts (list): Liste des textes associés à l'objet.
        feature (QgsFeature): Objet géospatial QGIS.
        label (QLabel): Widget d'étiquette affichant des informations sur l'objet.

        Actions effectuées:
        - Initialise les valeurs des attributs basées sur les paramètres.
        - Initialise la géométrie spatiale et les attributs de l'objet QgsFeature.
        - Configure et crée un QLabel pour afficher des informations spécifiques sur l'objet.
        - Met à jour la position de l'étiquette à sa position initiale.
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
        Retourne la latitude actuelle de l'entité,
        extraite de la géométrie QgsFeature.
        """
        point = self.feature.geometry().asPoint()
        return point.y()  # y correspond à la latitude

    def get_longitude(self) -> float:
        """
        Retourne la longitude actuelle de l'entité,
        extraite de la géométrie QgsFeature.
        """
        point = self.feature.geometry().asPoint()
        return point.x()

    # Getter et Setter pour altitude
    def get_altitude(self) -> float:
        return self.altitude

    def set_altitude(self, value: float):
        self.altitude = value

    # Getter et Setter pour url_icon
    def get_url_icon(self) -> str:
        return self.url_icon

    def set_url_icon(self, value: str, need_refresh_category: bool = True):
        self.url_icon = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_url_icon(self):
        """
        Réinitialise l'icône à sa valeur par défaut.
        """
        self.set_url_icon(self.url_icon_default)

    # Getter et Setter pour background_image
    def get_background_image(self) -> str:
        return self.background_image

    def set_background_image(self, value: str|None, need_refresh_category: bool = True):
        self.background_image = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_background_image(self):
        """
        Réinitialise l'opacité de l'objet à sa valeur par défaut, qui est 1.
        Cela garantit que l'objet est complètement opaque après l'appel de cette méthode.
        """
        self.set_background_image(None)

    # Getter et Setter pour highlight
    def get_highlight(self) -> bool:
        return self.highlight

    def set_highlight(self, value: str|None, need_refresh_category: bool = True):
        self.highlight = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_highlight(self):
        """
        Réinitialise la mise en surbrillance.
        """
        self.set_highlight(None)

    # Getter et Setter pour size
    def get_size(self) -> float:
        return self.size

    def set_size(self, value: float, need_refresh_category: bool = True):
        self.size = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_size(self):
        """
        Réinitialise la taille de l'objet à sa valeur par défaut.
        """
        self.set_size(self.size_default)

    # Getter et Setter pour texts
    def get_texts(self) -> list[str]:
        return self.texts

    def set_texts(self, value: list[str]):
        self.texts = value
        self.set_need_update_label(True)

    def append_text(self, text: str):
        """
        Ajoute une chaîne de texte à la liste existante.

        Paramètres:
        text (str): La chaîne de texte à ajouter.
        """
        self.texts.append(text)
        self.set_need_update_label(True)

    def reset_text(self):
        """
        Réinitialise le texte stocké dans l'objet.
        """
        if self.texts:
            self.set_texts([])

    # Getter
    def get_feature(self) -> str:
        return self.feature

    # Getter et Setter pour need_refresh_category
    def get_need_refresh_category(self) -> bool:
        return self.need_refresh_category

    def set_need_refresh_category(self, value: bool):
        if self.need_refresh_category is False:
            self.need_refresh_category = value

    # Getter et Setter pour need_refresh_category
    def get_need_update_label(self) -> bool:
        return self.need_update_label

    def set_need_update_label(self, value: bool):
        if self.need_update_label is False:
            self.need_update_label = value

    # Getter et Setter pour name
    def get_name(self) -> str:
        return self.name

    def set_name(self, value: str):
        self.name = value

    # Getter et Setter pour angle
    def get_angle(self) -> float:
        return self.angle

    def set_angle(self, value: float, need_refresh_category: bool = True):
        self.angle = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_angle(self):
        """
        Réinitialise l'angle de l'objet à zéro.
        """
        self.set_angle(0)

    # Getter et Setter pour id
    def get_id(self) -> str:
        return self.id

    # Getter et Setter pour opacity
    def get_opacity(self) -> float:
        return self.opacity

    def set_opacity(self, value: float, need_refresh_category: bool = True):
        self.opacity = value
        self.set_need_refresh_category(need_refresh_category)

    def reset_opacity(self):
        """
        Réinitialise l'opacité de l'objet à sa valeur par défaut, qui est 1.
        Cela garantit que l'objet est complètement opaque après l'appel de cette méthode.
        """
        self.set_opacity(1)

    # Getter
    def get_category(self):
        if self.need_refresh_category:
            self.category = self.generate_category()
            self.need_refresh_category = False

        return self.category


    def generate_category(self) -> QgsRendererCategory:
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
        Déplace l'objet vers les coordonnées spécifiées et met à jour son altitude.

        Paramètres:
        lat (float): Latitude de la nouvelle position.
        lon (float): Longitude de la nouvelle position.
        alti (float): Altitude de la nouvelle position.
        """
        self.feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        LayerTraceQGIS.get_instance().layer.dataProvider().changeGeometryValues({self.feature.id(): self.feature.geometry()})
        self.altitude = alti
        self.set_need_update_label(True)

    def move_to_entity(self, map_entity):
        self.move_to(map_entity.get_latitude(), map_entity.get_longitude(), map_entity.altitude)

    def reset(self):
        """
        Réinitialise les paramètres d'un objet à leurs valeurs par défaut.

        Les actions effectuées par cette méthode comprennent :
        - Réinitialisation de l'icône associée
        - Réinitialisation de la position
        - Réinitialisation de la taille
        - Réinitialisation du texte
        - Réinitialisation de l'angle
        - Réinitialisation de l'opacité
        - Réinitialisation de la mise en surbrillance
        - Mise à jour de la position de l'étiquette
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
        Réinitialise la position de l'objet à ses coordonnées par défaut.
        """
        self.move_to(self.latitude_default, self.longitude_default, self.altitude_default)

    def create_label(self) -> QLabel:
        label = QLabel(iface.mainWindow())
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("background-color: rgba(255, 255, 255, 200); border: 1px solid black;")
        label.setAttribute(Qt.WA_TransparentForMouseEvents)

        return label

    def reset_label(self):
        self.hide_label()
        self.label.setParent(None)
        self.label.deleteLater()
        self.label = self.create_label()
        self.set_need_update_label(True)

    def update_label_position(self, show_name: bool, show_position: bool):
        """
        Met à jour la position d'un label sur le canvas en fonction de la position d'une entité géographique.

        Cette méthode calcule la position écran d'une entité géographique à partir de sa géométrie et applique un décalage
        pour positionner un label de manière à ce qu'il n'obstrue pas l'entité. Elle vérifie également si le label se trouve
        dans les limites visibles du canvas et ajuste sa visibilité en conséquence.

        Pour le contenu du label, elle intègre l'ID de l'entité, ses coordonnées (X, Y et Z) avec une précision à quatre chiffres
        après la virgule, ainsi qu'un texte supplémentaire s'il existe.
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
        Cache l'étiquette (label) en la rendant invisible.
        """
        self.label.setVisible(False)

    def show_label(self):
        """
        Affiche l'étiquette en la rendant visible.
        """
        self.label.setVisible(True)

    def unload(self):
        if self.label:
            self.hide_label()
            self.label.setParent(None)
            self.label.deleteLater()
            self.label = None
