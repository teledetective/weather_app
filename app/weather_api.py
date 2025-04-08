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
    """Récupère la précipitation de neige record pour la date actuelle (année la plus récente disponible)."""
    base_url = "https://api.weather.gc.ca/collections/ltce-snowfall/items"
    today = datetime.now()
    current_month = today.month  # Par exemple, 4 pour avril
    current_day = today.day      # Par exemple, 8 pour le 8 avril
    
    # Commencer par l'année actuelle et remonter jusqu'à 10 ans en arrière
    for year_offset in range(0, 10):
        year = today.year - year_offset
        params = {
            "LOCAL_MONTH": current_month,
            "LOCAL_DAY": current_day,
            "VIRTUAL_CLIMATE_ID": station_id,
            "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",
            "f": "json",
            "limit": 10000,
            "offset": 0,
            "LOCAL_YEAR": year
        }
        try:
            url = f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
            print(f"Requête API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Réponse API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {data}")
                if data.get('features'):
                    properties = data['features'][0]['properties']
                    snowfall = properties.get('RECORD_SNOWFALL', 'N/A')
                    print(f"Données de neige trouvées pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: snowfall={snowfall}")
                    return {
                        'date': f"{year}-{current_month:02d}-{current_day:02d}",
                        'snowfall': snowfall
                    }
                else:
                    print(f"Aucune donnée de neige pour {station_id} le {year}-{current_month:02d}-{current_day:02d}")
            else:
                print(f"Erreur API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: Code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {e}")
            continue
    print(f"Aucune donnée de neige trouvée pour {station_id} après 10 ans")
    return None

def fetch_recent_temperatures(station_id):
    """Récupère les températures min/max pour la date actuelle (année la plus récente disponible)."""
    base_url = "https://api.weather.gc.ca/collections/ltce-temperature/items"
    today = datetime.now()
    current_month = today.month  # Par exemple, 4 pour avril
    current_day = today.day      # Par exemple, 8 pour le 8 avril
    
    # Commencer par l'année actuelle et remonter jusqu'à 10 ans en arrière
    for year_offset in range(0, 10):
        year = today.year - year_offset
        params = {
            "LOCAL_MONTH": current_month,
            "LOCAL_DAY": current_day,
            "VIRTUAL_CLIMATE_ID": station_id,
            "sortby": "VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY",
            "f": "json",
            "limit": 10000,
            "offset": 0,
            "LOCAL_YEAR": year
        }
        try:
            url = f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
            print(f"Requête API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Réponse API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {data}")
                if data.get('features'):
                    properties = data['features'][0]['properties']
                    temp_min = properties.get('FIRST_LOW_MIN_TEMP', 'N/A')
                    temp_max = properties.get('FIRST_HIGH_MIN_TEMP', 'N/A')
                    city_name = properties.get('VIRTUAL_STATION_NAME_F', 'N/A')  # Récupérer le nom de la ville
                    print(f"Données trouvées pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: max={temp_max}, min={temp_min}, ville={city_name}")
                    return {
                        'date': f"{year}-{current_month:02d}-{current_day:02d}",
                        'temp_max': temp_max,
                        'temp_min': temp_min,
                        'city_name': city_name
                    }
                else:
                    print(f"Aucune donnée de température pour {station_id} le {year}-{current_month:02d}-{current_day:02d}")
            else:
                print(f"Erreur API pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: Code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau pour {station_id} le {year}-{current_month:02d}-{current_day:02d}: {e}")
            continue
    print(f"Aucune donnée de température trouvée pour {station_id} après 10 ans")
    return None