# config.py : Fichier de configuration pour l'application météo

# URL de base pour l'API météo
WEATHER_API_BASE_URL = "https://api.weather.gc.ca/collections/ltce-temperature/items"
# URL pour récupérer les stations
STATIONS_API_BASE_URL = "https://api.weather.gc.ca/collections/ltce-stations/items"

# Paramètres par défaut pour les requêtes météo
WEATHER_API_DEFAULT_PARAMS = {
    "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",
    "f": "json",
    "limit": "10000",
    "offset": "0"
}

# Paramètres pour les requêtes sur les stations
STATIONS_API_DEFAULT_PARAMS = {
    "f": "json",
    "limit": "30000",
    "properties": "PROVINCE_CODE,VIRTUAL_STATION_NAME_E,VIRTUAL_CLIMATE_ID,ELEMENT_NAME_E",
    "ELEMENT_NAME_E": "TEMPERATURE"
}

# En-têtes HTTP pour les requêtes API
DEFAULT_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Chemin vers le fichier GeoJSON des stations
STATIONS_GEOJSON_PATH = "data/stations.geojson"

# Chemin vers la base de données SQLite
DATABASE_PATH = "data/weather_data.db"

# Moyennes historiques pour analyse (simplifiées pour la démo)
HISTORICAL_MAX_TEMP_AVG = 20.0
HISTORICAL_MIN_TEMP_AVG = 10.0

# Chemin du fichier GeoJSON (redondant avec STATIONS_GEOJSON_PATH)
STATIONS_GEOJSON = "data/stations.geojson"

# Valeurs par défaut pour les requêtes
DEFAULT_LIMIT = 10000
DEFAULT_OFFSET = 0
PAGINATION_LIMIT = 10

# Paramètres pour paginer les stations
PAGINATION_DEFAULT_LIMIT = 10  # Stations par page
PAGINATION_DEFAULT_OFFSET = 0  # Décalage initial