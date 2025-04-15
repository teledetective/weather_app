Weather Stations API
Une API REST Flask pour explorer les données météorologiques des stations canadiennes, avec une carte interactive. Elle utilise l’API d’Environnement Canada (https://api.weather.gc.ca), stocke les stations dans un fichier GeoJSON, met en cache les données dans SQLite, et affiche les stations via Leaflet.
Fonctionnalités

Chargement des stations :

Les stations sont lues depuis data/stations.geojson (identifiants, coordonnées).
Traitement via geopandas pour une gestion géospatiale efficace.


API REST :

GET / : Carte Leaflet avec marqueurs cliquables pour afficher neige et températures.
GET /stations?limit=X&offset=Y : Liste paginée des stations.
GET /station/indicator/<station_id>/<month>/<day> : Données météo pour une date donnée.
GET /station/snow/<station_id> : Neige record pour la date actuelle (jusqu’à 10 ans en arrière).
GET /station/temperatures/<station_id> : Températures max/min et nom de la ville pour la date actuelle (jusqu’à 10 ans).


Carte interactive :

Marqueurs Leaflet pour chaque station.
Clic : affiche les données météo dans un panneau (neige, températures, ville).


Cache :

Données de /snow et /temperatures stockées dans data/weather_data.db.
Vérification du cache avant chaque requête API.
Rafraîchissement forcé avec ?refresh=true sur la carte.



Concepts clés
Cache

Stockage : Réponses API en JSON dans SQLite, avec clés uniques (ex. VSQC136_snow_2025-04-15).
Logique : Vérifie le cache avant l’API ; ?refresh=true force une mise à jour.
But : Réduire les appels API pour plus de rapidité.

Base SQLite

Table weather_data :
station_id : ID station (ex. VSQC136).
month, day : Mois/jour (0 pour /snow, /temperatures).
data : Données JSON.
cache_key : Clé unique.


Gestion : Insertion via json.dumps(), lecture via json.loads().

Prérequis

Python 3.9+
Bibliothèques (requirements.txt) :
flask
geopandas
requests
shapely
pandas


Fichier data/stations.geojson
(Optionnel) Docker

Installation

Cloner le dépôt :
git clone https://github.com/teledetective/weather_app.git
cd weather_app


Créer un environnement virtuel :
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows


Installer les dépendances :
pip install -r requirements.txt


Vérifier stations.geojson :

Placez un fichier valide dans data/ avec station_id, latitude, longitude.


Lancer l’application :
python app.py


Accédez à http://localhost:5000.



Utilisation

Carte : Cliquez sur un marqueur pour voir les données (neige, températures, ville).
API :
Stations : curl http://localhost:5000/stations?limit=10&offset=0
Neige : curl http://localhost:5000/station/snow/VSQC136
Températures : curl http://localhost:5000/station/temperatures/VSQC136



Notes

Les endpoints /snow et /temperatures explorent 10 ans pour trouver des données.
Assurez-vous que stations.geojson est à jour.
SQLite se crée automatiquement.
Le cache améliore les performances, mais ?refresh=true garantit des données récentes.

