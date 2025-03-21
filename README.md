# Weather Stations API

Ce projet est une API REST développée avec Flask pour gérer des données de stations météorologiques au Canada. Elle utilise des données géospatiales provenant de l'API `https://api.weather.gc.ca` et les stocke dans un format GeoJSON, puis les charge dans un GeoDataFrame avec `geopandas`. L'API permet de lister les stations, de trouver les stations les plus proches d'une position donnée, et de récupérer les extrêmes météorologiques (températures maximale et minimale) pour une station et une date spécifiques.

## Fonctionnalités

- **Chargement des données géospatiales** : Les données des stations sont récupérées depuis l'API `https://api.weather.gc.ca/collections/ltce-stations/items` et stockées dans un fichier `stations.geojson`.
- **API REST avec Flask** :
  - `GET /stations` : Liste toutes les stations météorologiques.
  - `GET /stations/near?lat=<latitude>&lon=<longitude>` : Trouve les stations les plus proches d'une position donnée.
  - `GET /station/indicator/<id_station>/<month>/<day>` : Récupère les extrêmes météorologiques pour une station et une date, avec une analyse de la progression/régression des températures.
- **Stockage des requêtes** : Les requêtes à l'endpoint `/station/indicator` sont stockées dans une base de données SQLite (`weather_requests.db`).