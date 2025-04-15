WEATHER STATIONS API
---------------------

DESCRIPTION
-----------
Une API REST Flask pour explorer les données météorologiques des stations canadiennes.

Elle utilise l’API d’Environnement Canada (https://api.weather.gc.ca),
stocke les stations dans un fichier GeoJSON, met en cache les données dans SQLite,
et les affiche sur une carte interactive avec Leaflet.

FONCTIONNALITÉS
----------------
Chargement des stations :
- Lecture depuis data/stations.geojson (coordonnées, ID des stations)
- Traitement avec GeoPandas pour la manipulation géospatiale

API REST :
- GET / : Affiche la carte interactive
- GET /stations?limit=X&offset=Y : Liste paginée des stations
- GET /station/indicator/<station_id>/<month>/<day> : Données météo spécifiques
- GET /station/snow/<station_id> : Neige record (historique de 10 ans)
- GET /station/temperatures/<station_id> : Températures max/min historiques

Carte interactive :
- Clic sur une station → neige record, températures, nom de la ville

Cache :
- Données météo stockées dans une base SQLite (data/weather_data.db)
- Clés de cache : station + type + date
- Utilisation de ?refresh=true pour forcer la mise à jour

BASE DE DONNÉES SQLITE
-----------------------
- Table : weather_data
- Colonnes : station_id, month, day, data (JSON), cache_key (unique)
- json.dumps() pour stocker, json.loads() pour lire

PRÉREQUIS
---------
- Python ≥ 3.9
- Bibliothèques nécessaires :
  - flask
  - geopandas
  - requests
  - shapely
  - pandas

INSTALLATION
------------
1. Cloner le dépôt :
   git clone https://github.com/teledetective/weather_app.git
   cd weather_app

2. Créer un environnement virtuel :
   python -m venv venv
   source venv/bin/activate  (ou .\venv\Scripts\activate sous Windows)

3. Installer les dépendances :
   pip install -r requirements.txt

4. Lancer l’app :
   python app.py

UTILISATION
-----------
Accès via navigateur :
- http://localhost:5000

Appels API :
- /stations?limit=10
- /station/snow/VSQC136
- /station/temperatures/VSQC136

NOTES
-----
- Les données sont extraites depuis l’API d’Environnement Canada
- Le cache SQLite évite les appels répétitifs
- Le fichier stations.geojson doit être structuré correctement
