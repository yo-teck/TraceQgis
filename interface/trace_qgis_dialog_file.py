import os

from ..custom.manager.domain_problem_manager import DomainProblemManager
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QPushButton
from ..custom.utils.yaml_helper import YamlHelper

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'trace_qgis_dialog_file.ui'))


class TraceQGISDialogFile(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe représentant une boîte de dialogue QGIS personnalisée pour effectuer des opérations sur des fichiers.

    Méthodes :
    - __init__(parent=None) : Constructeur de la classe. Initialise la boîte de dialogue et configure les signaux nécessaires.
    - get_file_path() : Retourne le chemin d'accès au fichier sélectionné dans le QgsFileWidget.
    - valider() : Valide le fichier sélectionné, vérifie son chemin et le charge avec un validateur YAML.

    Attributs :
    - data : Contient les données chargées à partir du fichier sélectionné.
    """

    def __init__(self, parent=None):
        """
        Initialise une nouvelle instance de la classe TraceQGISDialogFile.

        Paramètres:
        - parent : L'objet parent du dialogue, par défaut None.

        Attributs:
        - data : Chaîne de caractères initialisée comme vide.

        Comportement:
        - Déconnecte les signaux automatiques de la boîte de dialogue pour éviter des comportements inattendus.
        - Connecte le bouton d'acceptation à la méthode validate.
        """

        self.data = ""
        super(TraceQGISDialogFile, self).__init__(parent)

        self.setupUi(self)

        # Déconnecte les signaux automatiques
        try:
            self.buttonBox.accepted.disconnect()
        except Exception:
            pass  # Si rien n'était connecté, on ignore

        self.buttonBox.accepted.connect(self.validate)
        self.pushButton.clicked.connect(self.download_yaml)


    def get_configuration_file_path(self) -> str:
        """
        Retourne le chemin du fichier sélectionné dans le QgsFileWidget.

        Méthode pour accéder au chemin du fichier spécifié dans le widget de type QgsFileWidget.

        Retourne:
            str: Le chemin absolu du fichier sélectionné dans le widget.
        """
        return self.configuration_filepath.filePath()

    def get_problem_file_path(self) -> str:
        """
        Retourne le chemin du fichier sélectionné dans le QgsFileWidget.

        Méthode pour accéder au chemin du fichier spécifié dans le widget de type QgsFileWidget.

        Retourne:
            str: Le chemin absolu du fichier sélectionné dans le widget.
        """
        return self.problem_filepath.filePath()

    def get_domain_file_path(self) -> str:
        """
        Retourne le chemin du fichier sélectionné dans le QgsFileWidget.

        Méthode pour accéder au chemin du fichier spécifié dans le widget de type QgsFileWidget.

        Retourne:
            str: Le chemin absolu du fichier sélectionné dans le widget.
        """
        return self.domain_filepath.filePath()

    def get_template_register_file_path(self) -> str:
        """
        Retourne le chemin du fichier sélectionné dans le QgsFileWidget.

        Méthode pour accéder au chemin du fichier spécifié dans le widget de type QgsFileWidget.

        Retourne:
            str: Le chemin absolu du fichier sélectionné dans le widget.
        """
        return self.dir_template_path.filePath()

    def download_yaml(self) -> None:
        path_domain = self.get_domain_file_path()
        path_problem = self.get_problem_file_path()
        domain_manager = DomainProblemManager()
        if domain_manager.has_model():
            domain_manager.reset()

        try:
            domain_manager.initialize(path_domain, path_problem)
            YamlHelper.generate_template(domain_manager.get_current_model(), self.get_template_register_file_path())
        except Exception as e:
            QMessageBox.critical(
                None,
                "Erreur fichier",
                f"Impossible d’écrire le fichier : {str(e)}"
            )
            return

        QMessageBox.information(
            None,
            "Template généré",
            f"Le template a bien été généré. Veuillez le remplir et le retourner"
        )
    def validate(self):
        """
        Valide les données en suivant les étapes définies, avec la gestion des erreurs.

        - Vérifie si un chemin de fichier a été fourni. Si ce n'est pas le cas, affiche un message d'avertissement.
        - Si un chemin est présent, tente de lire le fichier YAML en utilisant un schéma de validation JSON.
        - En cas d'erreur lors de la lecture ou de la validation, affiche un message décrivant l'erreur.
        - Si tout est valide, accepte le contenu actuel de la fenêtre ou du dialogue.
        """
        dpm = DomainProblemManager()
        if not self.get_problem_file_path():
            QMessageBox.warning(self, "Erreur", "Le champ fichier problème est obligatoire.")
            return
        if not self.get_domain_file_path():
            QMessageBox.warning(self, "Erreur", "Le champ fichier domain est obligatoire.")
            return
        path = self.get_configuration_file_path()
        if not path:
            QMessageBox.warning(self, "Erreur", "Le champ fichier est obligatoire.")
            return
        if not self.domain_problem_output.toPlainText():
            QMessageBox.warning(self, "Erreur", "Le chemin de sortie est obligatoire.")
            return
        plugin_dir = os.path.dirname(__file__)
        try:
            if not dpm.has_model():
                dpm.initialize(self.get_domain_file_path(), self.get_problem_file_path())
            dpm.get_current_model().load_plan(self.domain_problem_output.toPlainText())
            self.data = YamlHelper.read_file(path, plugin_dir + "/../schema/base_yaml_validator.json")
            dpm.get_current_model().save_configuration(self.data)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
            return

        self.accept()

    def unload(self):
        self.buttonBox.accepted.disconnect(self.validate)