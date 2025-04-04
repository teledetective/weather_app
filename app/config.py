# Base API URLs
WEATHER_API_BASE_URL = "https://api.weather.gc.ca/collections/ltce-temperature/items"
STATIONS_API_BASE_URL = "https://api.weather.gc.ca/collections/ltce-stations/items"

# Default query parameters for weather API
WEATHER_API_DEFAULT_PARAMS = {
    "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",
    "f": "json",
    "limit": "10000",
    "offset": "0"
}

# Default query parameters for stations API
STATIONS_API_DEFAULT_PARAMS = {
    "f": "json",
    "limit": "30000",
    "properties": "PROVINCE_CODE,VIRTUAL_STATION_NAME_E,VIRTUAL_CLIMATE_ID,ELEMENT_NAME_E",
    "ELEMENT_NAME_E": "TEMPERATURE"
}

# Default headers for API requests
DEFAULT_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# File paths
STATIONS_GEOJSON_PATH = "data/stations.geojson"

# Historical averages for trend analysis (simplified for demo purposes)
HISTORICAL_MAX_TEMP_AVG = 20.0
HISTORICAL_MIN_TEMP_AVG = 10.0

# Database path
WEATHER_REQUESTS_DB = "weather_requests.db"
# app/config.py
# Configuration globale pour le projet Weather App

# Chemin vers le fichier GeoJSON contenant les données des stations
STATIONS_GEOJSON = "data/stations.geojson"

# URL de base pour l'API météo de Environment Canada
WEATHER_API_BASE_URL = "https://api.weather.gc.ca/collections/ltce-temperature/items"

# Paramètres par défaut pour les requêtes à l'API météo
WEATHER_API_DEFAULT_PARAMS = {
    "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",  # Tri des résultats
    "f": "json",                                           # Format de réponse
    "limit": 10000,                                        # Limite par défaut pour l'API
    "offset": 0                                            # Offset par défaut pour l'API
}

# Paramètres par défaut pour les requêtes
DEFAULT_LIMIT = 10000
DEFAULT_OFFSET = 0
PAGINATION_LIMIT = 10

# Paramètres pour la pagination des stations
PAGINATION_DEFAULT_LIMIT = 10  # Nombre de stations par page par défaut
PAGINATION_DEFAULT_OFFSET = 0  # Décalage par défaut pour la pagination

# Chemin vers la base de données SQLite
DATABASE_PATH = "data/weather.db"