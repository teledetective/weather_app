import requests
from config import WEATHER_API_BASE_URL, DEFAULT_LIMIT, DEFAULT_OFFSET
from datetime import datetime, timedelta

WEATHER_API_PARAMS = {
    "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",
    "f": "json",
    "limit": DEFAULT_LIMIT,
    "offset": DEFAULT_OFFSET
}

def fetch_weather_data(station_id, month, day):
    """Effectue une requête HTTP vers api.weather.gc.ca pour les données météo."""
    params = WEATHER_API_PARAMS.copy()
    params.update({
        "LOCAL_MONTH": month,
        "LOCAL_DAY": day,
        "VIRTUAL_CLIMATE_ID": station_id
    })
    url = f"{WEATHER_API_BASE_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_recent_snow_data(station_id):
    """Récupère les données de neige des 5 derniers jours pour une station."""
    base_url = "https://api.weather.gc.ca/collections/climate-daily/items"
    today = datetime.now()
    snow_data = []

    for i in range(5):
        date = today - timedelta(days=i)
        params = {
            "LOCAL_YEAR": date.year,
            "LOCAL_MONTH": date.month,
            "LOCAL_DAY": date.day,
            "VIRTUAL_CLIMATE_ID": station_id,
            "f": "json",
            "limit": 1
        }
        url = f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                snow_value = data['features'][0]['properties'].get('SNOW_ON_GROUND_CM', 'N/A')
                snow_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'snow_cm': snow_value
                })
    return snow_data if snow_data else None

def fetch_recent_temperatures(station_id):
    """Récupère les températures max/min les plus récentes pour une station."""
    base_url = "https://api.weather.gc.ca/collections/climate-daily/items"
    today = datetime.now()
    
    # Essayer les 5 derniers jours pour trouver la donnée la plus récente
    for i in range(5):
        date = today - timedelta(days=i)
        params = {
            "LOCAL_YEAR": date.year,
            "LOCAL_MONTH": date.month,
            "LOCAL_DAY": date.day,
            "VIRTUAL_CLIMATE_ID": station_id,
            "f": "json",
            "limit": 1
        }
        url = f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                properties = data['features'][0]['properties']
                temp_max = properties.get('MAX_TEMPERATURE', 'N/A')
                temp_min = properties.get('MIN_TEMPERATURE', 'N/A')
                return {
                    'date': date.strftime('%Y-%m-%d'),
                    'temp_max': temp_max,
                    'temp_min': temp_min
                }
    return None