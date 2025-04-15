# Weather Stations API

# Description
# Une API REST Flask pour explorer les données météorologiques des stations canadiennes.
# Elle utilise l’API d’Environnement Canada (https://api.weather.gc.ca),
# stocke les stations dans un fichier GeoJSON, met en cache les données dans SQLite,
# et affiche les stations via une carte interactive (Leaflet).

# Fonctionnalités

# Chargement des stations
# - Lecture depuis data/stations.geojson (coordonnées, ID des stations)
# - Traitement via GeoPandas pour une gestion géospatiale simple

# API REST
# - GET / : Affiche la carte avec les stations
# - GET /stations?limit=X&offset=Y : Liste paginée des stations
# - GET /station/indicator/<station_id>/<month>/<day> : Données météo pour une date précise
# - GET /station/snow/<station_id> : Neige record pour la date actuelle (sur 10 ans)
# - GET /station/temperatures/<station_id> : Températures max/min et nom de la ville (10 ans max)

# Carte interactive
# - Affiche les stations météo avec Leaflet
# - Clic sur une station = affiche neige + températures + nom de la ville

# Cache
# - Données de /snow et /temperatures enregistrées dans data/weather_data.db
# - Utilise un cache SQLite pour éviter les appels répétitifs à l'API
# - ?refresh=true permet de forcer une mise à jour

# Concepts clés

# Cache
# - Données JSON stockées dans SQLite avec des clés uniques (ex : VSQC136_snow_2025-04-15)
# - Vérifie d'abord le cache, puis interroge l’API si besoin
# - Améliore les performances et réduit la charge réseau

# Base SQLite
# - Table weather_data avec les colonnes :
#   - station_id
#   - month
#   - day
#   - data (JSON)
#   - cache_key (clé unique)
# - Insertion via json.dumps(), lecture via json.loads()

# Prérequis

# - Python 3.9 ou supérieur
# - Bibliothèques à installer via requirements.txt :
#   flask
#   geopandas
#   requests
#   shapely
#   pandas

# - Fichier requis : data/stations.geojson avec les champs :
#   station_id, latitude, longitude

# Installation

# Cloner le dépôt
git clone https://github.com/teledetective/weather_app.git
cd weather_app

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux / Mac
.\venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Vérifier le fichier stations.geojson
# Il doit être placé dans le dossier data/ avec les bons attributs

# Lancer l’application Flask
python app.py

# Accès via le navigateur
# http://localhost:5000

# Utilisation

# Sur la carte :
# - Cliquez sur un marqueur pour voir :
#   - les données de neige record
#   - les températures max/min
#   - le nom de la ville

# Appels API directs :
# - curl http://localhost:5000/stations?limit=10&offset=0
# - curl http://localhost:5000/station/snow/VSQC136
# - curl http://localhost:5000/station/temperatures/VSQC136

# Notes

# - Les endpoints /snow et /temperatures explorent jusqu’à 10 ans en arrière
# - Assurez-vous que stations.geojson est bien structuré
# - La base SQLite est générée automatiquement
# - Le cache permet d’améliorer la rapidité d’affichage
# - Ajouter ?refresh=true dans l’URL permet de forcer une mise à jour
