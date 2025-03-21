import requests

def fetch_weather_data(station_id, month, day):
    url = (f"https://api.weather.gc.ca/collections/ltce-temperature/items?"
           f"LOCAL_MONTH={month}&LOCAL_DAY={day}&VIRTUAL_CLIMATE_ID={station_id}"
           f"&sortby=VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY&f=json&limit=10000&offset=0")
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None