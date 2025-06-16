# Carto

## 1. Installation des bibliothèques Python

Avant d'utiliser ce plugin, vous devez installer les bibliothèques nécessaires (jsonschema et pyyaml) dans l'environnement Python de QGIS.

### 1. Localise l’interpréteur Python utilisé par QGIS.

Par défaut (sous Windows), c’est souvent quelque chose comme :
C:\Program Files\QGIS XXX\bin\python.exe

### 2. Ouvre un terminal (CMD ou PowerShell).

Utilise cet interpréteur pour installer les paquets :
```
"Chemin\python.exe" -m pip install jsonschema pyyaml
Exemple :
"C:\Program Files\QGIS 3.28\bin\python.exe" -m pip install jsonschema pyyaml
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
