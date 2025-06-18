import os

from PyQt5.QtWidgets import QGridLayout
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDockWidget, QVBoxLayout, QHBoxLayout, QWidget, QRadioButton, QButtonGroup, QDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

# Chargement du .ui existant
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'trace_qgis_dock_widget_setting.ui'))


class TraceQGISDockWidget(QDockWidget, FORM_CLASS):
    """
    TraceQGISDockWidget est une classe qui hérite de QDockWidget et FORM_CLASS.
    Elle configure et gère un widget de panneau dédié aux paramètres de visualisation de TraceQGIS.

    Attributes:
        speed_group : Un groupe de boutons radio représentant différentes vitesses de lecture.
        radio_layout : Un agencement horizontal pour les boutons radio de focus.
        radio_group : Un groupe de boutons radio pour gérer les options de focus.
        pauseButton : Bouton permettant de mettre en pause ou de reprendre le timer.
        tickSlider : Slider servant à ajuster la position actuelle dans le traçage temporel.

    Méthodes:
        __init__(parent) : Initialise et configure l'interface utilisateur du widget.
        refresh_radio_buttons() : Actualise les options des boutons radio pour les entités affichées dans le widget.
        on_radio_changed(id_) : Déclenchement lors du changement de bouton radio de focus, met à jour l'entité en focus.
        get_vitesse() -> int : Retourne l'identifiant de la vitesse actuellement sélectionnée parmi les boutons radio.
        on_vitesse_changed() : Modifie l'intervalle du timer basé sur la vitesse choisie.
        get_focus() : Retourne l'identifiant de l'entité actuellement sélectionnée dans le groupe de boutons radio de focus.
        toggle_timer() : Active ou désactive le timer, met à jour le texte du bouton pause/lecture.
        on_tickSlider_changed() -> bool : Détecte le changement de position du slider et actualise l'état du traçage temporel.
        change_current_tick(tick) : Modifie et affiche la valeur actuelle du tick dans l'affichage numérique.
        change_tick_equivalent(tick, multiplier, unit) : Calcule et affiche la valeur équivalente du tick en fonction d'un multiplicateur et d'une unité donnée.
        get_tickSlider() -> int : Retourne la valeur actuelle du slider.
        set_max_tickSlider(max) : Définit la valeur maximale admissible pour le slider.
        set_value_tickSlider(value) : Ajuste la valeur du slider et met à jour les affichages du tick courant et équivalent.
    """
    signal_focus_changed = pyqtSignal(str)
    signal_tick_changed = pyqtSignal(int)
    signal_speed_changed = pyqtSignal(int)
    signal_toggle_timer = pyqtSignal(int)
    signal_toggle_show_info_name = pyqtSignal(bool)
    signal_toggle_show_info_position = pyqtSignal(bool)
    ENTITY_ID_PROPERTY_NAME = "entity_id"

    def __init__(self, parent=None, multiplier: float= 10, unit: str = "sec"):
        """
        Constructeur de la classe.

        Initialise le widget principal et configure l'interface utilisateur, y compris les groupes de boutons radio pour la définition des vitesses d'exécution.

        Configuration spécifique :
        - Attribue un titre à la fenêtre principale.
        - Crée un groupe de boutons radio pour gérer différentes options de vitesses (x1, x2, x5, x10).
        - Configure un layout horizontal pour contenir les boutons radio associés à la mise au point.

        Connecte les signaux des éléments interactifs de l'interface utilisateur à leurs slots correspondants :
        - Liaison du bouton de pause pour activer ou désactiver le minuteur.
        - Récupération de la sélection de vitesse choisie parmi les boutons radio.
        - Gestion de la libération du slider pour effectuer des actions lors de modifications sur celui-ci.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Setup UI dans le widget
        self.setWindowTitle("Trace QGIS - Paramétrage")

        # Groupe des radios de vitesse
        self.speed_group = QButtonGroup(self)
        self.speed_group.addButton(self.radioButton_vitesse1, 1)  # x1
        self.speed_group.addButton(self.radioButton_vitesse2, 2)  # x2
        self.speed_group.addButton(self.radioButton_vitesse3, 5)  # x5
        self.speed_group.addButton(self.radioButton_vitesse4, 10)  # x10

        # Layout pour les radios
        self.radio_layout = QGridLayout(self.focusRadioContainer)
        self.radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_group = QButtonGroup(self.focusRadioContainer)


        self.pauseButton.clicked.connect(self.toggle_timer)
        self.speed_group.buttonClicked.connect(self.on_vitesse_changed)
        self.tickSlider.sliderReleased.connect(self.on_tickSlider_changed)
        self.checkbox_show_name.stateChanged.connect(self.toggle_show_information_name)
        self.checkbox_show_position.stateChanged.connect(self.toggle_show_information_position)
        self.radio_group.buttonClicked[int].connect(self.on_radio_changed)

        self.timer_on = True
        self.multiplier = multiplier
        self.unit = unit

    def refresh_radio_buttons(self, entities_list: list = []):
        """
        Actualise les boutons radio en supprimant les anciens et en ajoutant de nouveaux.

        Ajoute un bouton radio par défaut :
        - Créé un bouton radio "Aucun" associé à un identifiant 0.
        - Ajoute ce bouton au groupe de boutons et à la mise en page.

        Ajoute un bouton radio pour chaque entité :
        - Parcours toutes les entités de la carte.
        - Pour chaque entité, crée un bouton radio portant son nom, associé à son identifiant.
        - Ajoute le bouton radio au groupe et à la mise en page.

        Connecte les clics sur les boutons radio à la méthode de gestion des changements "on_radio_changed".
        """
        # Nettoyer anciens boutons
        while self.radio_layout.count():
            child = self.radio_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Bouton "Aucun"
        btn = QRadioButton('Aucun')
        self.radio_group.addButton(btn, 0)
        self.radio_layout.addWidget(btn, 0, 0)

        # Boutons par entité
        i = 1
        for id_, name in entities_list:
            btn = QRadioButton(name)
            btn.setProperty(self.ENTITY_ID_PROPERTY_NAME, id_)
            self.radio_group.addButton(btn, i)
            row = i // 2  # ligne actuelle
            col = i % 2  # 0 ou 1 : colonne
            self.radio_layout.addWidget(btn, row, col)
            i += 1

    def on_radio_changed(self, id_):
        """
        Met à jour le focus de LayerTraceQGIS lors du changement de sélection radio.

        Paramètres:
        id_ : Identifiant de l'élément sélectionné.
        """
        self.signal_focus_changed.emit(self.get_focus())

    def get_vitesse(self) -> int:
        """
        Renvoie l'identifiant de l'option de vitesse sélectionnée.

        Retourne:
            int: Identifiant de l'option actuellement sélectionnée dans le groupe de boutons de vitesse.
        """
        return self.speed_group.checkedId()

    def on_vitesse_changed(self):
        """
        Méthode qui est appelée lorsque la vitesse change.

        Elle met à jour l'intervalle du minuteur de l'objet LayerTraceQGIS avec la nouvelle vitesse obtenue à partir de l'instance actuelle.
        """
        self.signal_speed_changed.emit(self.get_vitesse())

    def get_focus(self):
        """
        Renvoie l'identifiant du bouton radio actuellement sélectionné dans le groupe de boutons radio.

        Si un bouton est sélectionné dans le groupe de boutons radio, retourne son identifiant.
        Sinon, retourne None.

        Retour :
        - Identifiant du bouton radio sélectionné ou None si aucun bouton n'est sélectionné.
        """
        checked_button = self.radio_group.checkedButton()
        if checked_button:
            return checked_button.property(self.ENTITY_ID_PROPERTY_NAME)
        return None

    def toggle_timer(self):
        """
        Permet de basculer l'état du minuteur.

        Cette méthode utilise l'instance unique de LayerTraceQGIS pour changer l'état du minuteur.
        Si le minuteur est actif, le texte du bouton est défini sur "Pause".
        Sinon, il est défini sur "Lecture".
        """
        timer_change = not self.timer_on
        self.set_timer_on(timer_change)
        self.signal_toggle_timer.emit(timer_change)

    def set_timer_on(self, is_active: bool):
        """
        Permet de basculer l'état du minuteur.

        Cette méthode utilise l'instance unique de LayerTraceQGIS pour changer l'état du minuteur.
        Si le minuteur est actif, le texte du bouton est défini sur "Pause".
        Sinon, il est défini sur "Lecture".
        """
        self.timer_on = is_active
        if self.timer_on:
            self.pauseButton.setText("Lecture")
        else:
            self.pauseButton.setText("Pause")

    def on_tickSlider_changed(self):
        """
        Méthode appelée lorsque le curseur 'tickSlider' change de position.
        Cette méthode met à jour l'état en appelant 'go_to_tick' sur l'instance singleton LayerTraceQGIS,
        en passant la valeur actuelle du curseur 'tickSlider' comme argument.

        Retourne :
            bool : Toujours True
        """

        self.signal_tick_changed.emit(self.get_tickSlider())

    def change_current_tick(self, tick: int):
        """
        Modifie la valeur actuelle du tick et l'affiche.

        Paramètres:
        tick (int): La nouvelle valeur du tick à afficher.
        """
        self.tickCourant.display(tick)

    def change_tick_equivalent(self, tick: int):
        """
        Modifie l'équivalent d'un tick en fonction d'un multiplicateur et d'une unité.

        Paramètres:
        tick (int): La valeur du tick à modifier.
        multiplier (float): Le multiplicateur appliqué à la valeur du tick.
        unit (str): L'unité de mesure qui sera ajoutée au tick calculé.

        Comportement:
        - Multiplie la valeur du tick par le multiplicateur donné.
        - Met à jour l'affichage du texte avec la nouvelle valeur du tick formatée en flottant (2 décimales) suivie de l'unité.
        """
        tick *= self.multiplier
        self.tickEquivalentLabel.setText(f"{tick:.2f} {self.unit}")

    def get_tickSlider(self) -> int:
        """
        Renvoie la valeur actuelle du tickSlider.

        Retour:
            int: La valeur actuelle du tickSlider.
        """
        return self.tickSlider.value()

    def set_max_tickSlider(self, max: int):
        """
        Définit la valeur maximale du tickSlider.

        Paramètres:
        max (int): Valeur maximale à définir pour le tickSlider.
        """
        self.tickSlider.setMaximum(max)

    def set_value_tickSlider(self, value: int):
        """
        Définit la valeur de tickSlider ainsi que les valeurs associées.

        Paramètres:
        value (int): La valeur à définir pour le tickSlider.

        Actions:
        - Met à jour la valeur du composant graphique tickSlider.
        - Change la valeur actuelle du tick (tick courant) en fonction de la nouvelle valeur.
        - Met à jour le tick équivalent, basé sur le multiplicateur et l'unité obtenus depuis l'instance de LayerTraceQGIS.
        """
        self.tickSlider.setValue(value)
        self.change_current_tick(value)
        self.change_tick_equivalent(value)

    def toggle_show_information_name(self, state):
        """Affiche ou cache les labels selon l'état du checkbox"""
        visible = state == Qt.Checked
        self.signal_toggle_show_info_name.emit(visible)

    def toggle_show_information_position(self, state):
        """Affiche ou cache les labels selon l'état du checkbox"""
        visible = state == Qt.Checked
        self.signal_toggle_show_info_position.emit(visible)

    def unload(self):
        self.radio_group.buttonClicked[int].disconnect(self.on_radio_changed)
        self.pauseButton.clicked.disconnect(self.toggle_timer)
        self.speed_group.buttonClicked.disconnect(self.on_vitesse_changed)
        self.tickSlider.sliderReleased.disconnect(self.on_tickSlider_changed)
        self.checkbox_show_name.stateChanged.disconnect(self.toggle_show_information_name)
        self.checkbox_show_position.stateChanged.disconnect(self.toggle_show_information_position)