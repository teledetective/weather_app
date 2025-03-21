# Weather Stations API

Ce projet est une API REST développée avec Flask pour gérer des données de stations météorologiques au Canada. Elle utilise des données géospatiales provenant de l'API `https://api.weather.gc.ca` et les stocke dans un format GeoJSON, puis les charge dans un GeoDataFrame avec `geopandas`. L'API permet de lister les stations, de trouver les stations les plus proches d'une position donnée, de récupérer les extrêmes météorologiques pour une station et une date spécifiques, et d'afficher les stations sous forme de points sur une carte interactive avec Leaflet.

## Fonctionnalités

- **Chargement des données géospatiales** : Les données des stations sont récupérées depuis l'API `https://api.weather.gc.ca/collections/ltce-stations/items` et stockées dans un fichier `stations.geojson`.
- **API REST avec Flask** :
  - `GET /stations` : Liste toutes les stations météorologiques.
  - `GET /stations/near?lat=<latitude>&lon=<longitude>` : Trouve les stations autour d’une position donnée et calcule la distance pour chaque station.
  - `GET /station/indicator/<id_station>/<month>/<day>` : Récupère les extrêmes pour une journée et une station données, avec une analyse de la progression/régression des extrêmes.
  - `GET /map` : Affiche une carte interactive avec Leaflet où les stations sont représentées sous forme de points (marqueurs), avec des popups contenant des informations sur chaque station.
- **Stockage des requêtes** : Les requêtes à l'endpoint `/station/indicator` sont stockées dans une base de données SQLite (`weather_requests.db`).

## Prérequis

- Python 3.9 ou supérieur
- Les bibliothèques Python suivantes (listées dans `requirements.txt`) :
  - `flask`
  - `geopandas`
  - `requests`
  - `shapely`
  - `pandas`

## Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/teledetective/weather_app.git
   cd weather_app