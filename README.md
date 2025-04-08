# Weather Stations API

Ce projet est une API REST développée avec Flask pour gérer des données de stations météorologiques au Canada. Elle récupère des données géospatiales depuis l'API `https://api.weather.gc.ca`, les stocke dans un fichier GeoJSON, et les charge dans un GeoDataFrame avec `geopandas`. L’application permet de lister les stations, d’afficher leurs positions sur une carte interactive avec Leaflet, et de récupérer des données météorologiques spécifiques, telles que les températures extrêmes pour une station donnée. Les données sont mises en cache dans une base de données SQLite pour optimiser les performances.

## Fonctionnalités

- **Chargement des données géospatiales** :
  - Les stations sont définies dans un fichier statique `data/stations.geojson`, qui contient leurs identifiants, noms, coordonnées et autres métadonnées.
  - Les données sont chargées dans un GeoDataFrame avec `geopandas` pour un traitement géospatial efficace.

- **API REST avec Flask** :
  - `GET /stations` : Retourne une liste paginée de toutes les stations météorologiques définies dans `stations.geojson`.
  - `GET /station/indicator/<id_station>/<month>/<day>` : Récupère les données météorologiques pour une station, un mois et un jour spécifiques via l’API `https://api.weather.gc.ca/collections/ltce-temperature/items`.
  - `GET /station/snow/<id_station>` : Récupère les données de neige des 5 derniers jours pour une station donnée via l’API `https://api.weather.gc.ca/collections/climate-daily/items`.
  - `GET /station/temperatures/<id_station>` : Récupère les températures extrêmes (minimale et maximale) pour une station spécifique pour le 10 janvier, en utilisant la requête suivante :  
    `https://api.weather.gc.ca/collections/ltce-temperature/items?LOCAL_MONTH=01&LOCAL_DAY=10&VIRTUAL_CLIMATE_ID=<station_id>&sortby=VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY&f=json&limit=10000&offset=0`.  
    Les champs extraits sont `FIRST_LOW_MIN_TEMP` (température minimale) et `FIRST_HIGH_MIN_TEMP` (température maximale).
  - `GET /` : Affiche une carte interactive avec Leaflet où les stations sont représentées sous forme de marqueurs. En cliquant sur une station, les données de neige et de température sont affichées dans un panneau d’information en bas de la page.

- **Mise en cache des données** :
  - Les résultats des requêtes aux endpoints `/station/snow/<id_station>` et `/station/temperatures/<id_station>` sont stockés dans une base de données SQLite (`data/weather_data.db`) pour éviter de refaire des appels API inutiles.
  - À chaque clic sur une station dans la carte, l’application vérifie d’abord si les données sont disponibles dans le cache. Si elles ne le sont pas ou si un rafraîchissement est forcé (via le paramètre `?refresh=true`), une nouvelle requête est effectuée et le résultat est mis à jour dans la base de données.

- **Carte interactive** :
  - Une carte Leaflet est utilisée pour afficher les stations sous forme de points. Lorsqu’un utilisateur clique sur un marqueur, les données de neige et de température sont récupérées et affichées dynamiquement dans un panneau d’information.

## Concepts clés

### Mise en cache
La mise en cache est utilisée pour améliorer les performances de l’application en réduisant le nombre de requêtes envoyées à l’API externe `https://api.weather.gc.ca`. Voici comment elle fonctionne :
- **Stockage dans SQLite** : Les réponses des requêtes API sont stockées dans une base de données SQLite (`weather_data.db`) sous forme de texte JSON. Chaque entrée est associée à une clé unique (par exemple, `VSQC136_temp_recent` pour les températures d’une station).
- **Vérification du cache** : Avant d’effectuer une requête API, l’application vérifie si les données sont déjà présentes dans la base de données pour la station demandée.
- **Rafraîchissement forcé** : Lorsqu’un utilisateur clique sur une station dans la carte, la requête pour les températures inclut le paramètre `?refresh=true`, ce qui force une nouvelle requête API et met à jour le cache, même si des données existent déjà. Cela garantit que les informations affichées sont toujours les plus récentes disponibles.

### Base de données SQLite
La base de données SQLite (`weather_data.db`) est utilisée pour persister les données météorologiques :
- **Structure** : La table `weather_data` contient les colonnes suivantes :
  - `station_id` : Identifiant de la station (par exemple, `VSQC136`).
  - `month` et `day` : Mois et jour associés à la requête (utilisés pour `/station/indicator`, définis à `0` pour les endpoints `/snow` et `/temperatures`).
  - `data` : Données météorologiques sous forme de texte JSON.
  - `cache_key` : Clé unique pour identifier chaque entrée (par exemple, `VSQC136_temp_recent`).
- **Insertion et récupération** : Les données sont insérées avec `json.dumps()` pour garantir un format JSON valide et récupérées avec `json.loads()` pour être utilisées dans l’application.

## Prérequis

- Python 3.9 ou supérieur
- Docker (pour exécuter l’application dans un conteneur)
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