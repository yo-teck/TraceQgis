# Trace QGIS

Trace QGIS est un plugin pour QGIS qui permet de charger, visualiser et animer des entités géographiques en fonction d’actions définies dans des plans (ex : PDDL).
Il permet de représenter les mouvements d’entités sur une carte, de générer des traces et de gérer des scénarios dynamiques.
## Installation
### Prérequis

QGIS ≥ 3.x (compatible avec les versions LTR comme 3.28 ou 3.40)
Python 3.x (fourni avec QGIS)
Avoir un environnement QGIS configuré avec un profil utilisateur
Dépendance python: jsonschema, pyyaml, pddlpy

### Installation manuelle

#### 1. Téléchargement 

Télécharger le zip directement depuis le dépôt officiel : https://github.com/yo-teck/TraceQgis

#### 2. Installation des dépendances 

Ouvrir "OSGeo4W Shell" installer les dépendances suivante : jsonschema, pyyaml, pddlpy

```pip install jsonschema pyyaml pddlpy```

#### 3. Instalation du plugin via QGIS

Démarrez QGIS (ou redémarrez-le si déjà ouvert).

Menu Extensions → Installer/Gérer les extensions
Puis Installer depuis un ZIP

Cherchez votre fichier ZIP et installer le.

2 boutons vert devrait apparaitre appuyez sur le premier "TraceQGIS" et appuyez sur démo

## Lancer les tests unitaires

### 1. Localise l’interpréteur Python utilisé par QGIS.

Par défaut (sous Windows), c’est souvent quelque chose comme :
C:\Program Files\QGIS XXX\bin\python.exe

### 2. Ouvre un terminal (CMD ou PowerShell).

Utilise cet interpréteur pour installer les paquets :
```
"Chemin\python.exe" -m pip install jsonschema pyyaml pddlpy
Exemple :
"C:\Program Files\QGIS 3.28\bin\python.exe" -m pip install jsonschema pyyaml pddlpy
```
Remarque : Si l'installation de pip n'est pas disponible, vous devrez peut-être configurer pip pour fonctionner dans l'environnement Python de QGIS. Si nécessaire, consultez la documentation de QGIS pour savoir comment installer des paquets dans son environnement Python.

## 2. Ajouter le plugin à QGIS
Téléchargez le code source du plugin ou placez-le dans votre répertoire de plugins QGIS.

## 3. Test and Deploy

### Package to install
``pytest pytest-mock jsonschema pddlpy``

To launch test you need to do in **OSGeo4W Shell**:

```bash
set PYTHONPATH=pathofrepo;pathofqgisrepo

# EXAMPLE:
set PYTHONPATH=C:\Users\jean\carto;C:\OSGeo4W\apps\qgis\python

# THEN
pytest

```

You need to name function whom test like ``test_*.py``

***
