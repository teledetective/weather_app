import requests
from config import WEATHER_API_BASE_URL, WEATHER_API_DEFAULT_PARAMS

def fetch_weather_data(station_id, month, day):
    # Construct query parameters
    params = WEATHER_API_DEFAULT_PARAMS.copy()
    params.update({
        "LOCAL_MONTH": str(month).zfill(2),
        "LOCAL_DAY": str(day).zfill(2),
        "VIRTUAL_CLIMATE_ID": station_id
    })
    
    # Make the API request
    response = requests.get(WEATHER_API_BASE_URL, params=params)
    return response.json() if response.status_code == 200 else None