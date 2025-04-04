import requests
import geopandas as gpd
import sqlite3
import os
import pandas as pd
from flask import Flask, jsonify, request, render_template
from shapely.geometry import Point
from datetime import datetime
from config import (
    STATIONS_API_BASE_URL, STATIONS_API_DEFAULT_PARAMS, DEFAULT_API_HEADERS,
    STATIONS_GEOJSON_PATH, HISTORICAL_MAX_TEMP_AVG, HISTORICAL_MIN_TEMP_AVG,
    WEATHER_REQUESTS_DB
)

app = Flask(__name__)

# Fonction pour récupérer les stations et générer stations.geojson
def fetch_stations_to_geopandas():
    response = requests.get(STATIONS_API_BASE_URL, params=STATIONS_API_DEFAULT_PARAMS, headers=DEFAULT_API_HEADERS)
    
    if response.status_code != 200:
        print(f"Erreur lors de la requête : {response.status_code}")
        return None

    data = response.json()
    if data.get("type") != "FeatureCollection":
        print("Les données ne sont pas une FeatureCollection")
        return None

    features = data.get("features", [])
    stations_data = []

    for feature in features:
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        if geometry.get("type") == "Point":
            coordinates = geometry.get("coordinates", [])
            if len(coordinates) == 2:
                longitude, latitude = coordinates
                station = {
                    "station_id": properties.get("VIRTUAL_CLIMATE_ID"),
                    "name": properties.get("VIRTUAL_STATION_NAME_E"),
                    "province": properties.get("PROVINCE_CODE"),
                    "element": properties.get("ELEMENT_NAME_E"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "geometry": Point(longitude, latitude)
                }
                stations_data.append(station)

    df = pd.DataFrame(stations_data)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    os.makedirs(os.path.dirname(STATIONS_GEOJSON_PATH), exist_ok=True)  # Ensure data directory exists
    gdf.to_file(STATIONS_GEOJSON_PATH, driver="GeoJSON")
    return gdf

# Charger les données géospatiales
if not os.path.exists(STATIONS_GEOJSON_PATH):
    print(f"Le fichier {STATIONS_GEOJSON_PATH} n'existe pas. Récupération des données...")
    gdf = fetch_stations_to_geopandas()
    if gdf is None:
        raise RuntimeError("Impossible de récupérer les données des stations.")
else:
    gdf = gpd.read_file(STATIONS_GEOJSON_PATH)

# Initialiser la base de données SQLite
def init_db():
    conn = sqlite3.connect(WEATHER_REQUESTS_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_requests
                 (station_id TEXT, month INTEGER, day INTEGER, request_time TEXT, data TEXT,
                  PRIMARY KEY (station_id, month, day))''')
    conn.commit()
    conn.close()

# Fonction pour calculer la distance (approximation simple en kilomètres)
def calculate_distance(lat1, lon1, lat2, lon2):
    return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111  # 1 degré ≈ 111 km

init_db()

# Endpoint 1 : GET /stations
@app.route('/stations', methods=['GET'])
def get_stations():
    stations = gdf[["station_id", "name", "province", "element", "latitude", "longitude"]].to_dict('records')
    return jsonify(stations)

# Endpoint 2 : GET /stations/near
@app.route('/stations/near', methods=['GET'])
def get_nearby_stations():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid latitude or longitude"}), 400

    gdf_copy = gdf.copy()
    gdf_copy['distance_km'] = gdf.apply(
        lambda row: calculate_distance(lat, lon, row['latitude'], row['longitude']),
        axis=1
    )

    nearest_stations = gdf_copy.sort_values(by='distance_km').head(5)
    result = nearest_stations[["station_id", "name", "province", "latitude", "longitude", "distance_km"]].to_dict('records')
    return jsonify(result)

# Endpoint 3 : GET /station/indicator/<station_id>/<month>/<day>
@app.route('/station/indicator/<station_id>/<month>/<day>', methods=['GET'])
def get_weather_indicator(station_id, month, day):
    if station_id not in gdf['station_id'].values:
        return jsonify({"error": "Station not found"}), 404

    conn = sqlite3.connect(WEATHER_REQUESTS_DB)
    c = conn.cursor()
    c.execute("SELECT data FROM weather_requests WHERE station_id = ? AND month = ? AND day = ?",
              (station_id, int(month), int(day)))
    cached_data = c.fetchone()
    if cached_data:
        conn.close()
        return jsonify({"source": "cache", "data": eval(cached_data[0])})

    url = (f"https://api.weather.gc.ca/collections/ltce-temperature/items?"
           f"LOCAL_MONTH={month.zfill(2)}&LOCAL_DAY={day.zfill(2)}&VIRTUAL_CLIMATE_ID={station_id}"
           f"&sortby=VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY&f=json&limit=10000&offset=0")
    
    response = requests.get(url, headers=DEFAULT_API_HEADERS)
    if response.status_code != 200:
        conn.close()
        return jsonify({"error": "Failed to fetch weather data"}), 500

    data = response.json()
    features = data.get("features", [])

    max_temp = None
    min_temp = None
    for feature in features:
        properties = feature.get("properties", {})
        element_name = properties.get("ELEMENT_NAME", "")
        value = properties.get("VALUE", None)
        if value is not None:
            if "MAX" in element_name:
                max_temp = float(value)
            elif "MIN" in element_name:
                min_temp = float(value)

    trend = {}
    if max_temp is not None:
        trend["max_temperature"] = "progression" if max_temp > HISTORICAL_MAX_TEMP_AVG else "regression"
    if min_temp is not None:
        trend["min_temperature"] = "progression" if min_temp > HISTORICAL_MIN_TEMP_AVG else "regression"

    request_time = datetime.utcnow().isoformat()
    c.execute("INSERT OR REPLACE INTO weather_requests (station_id, month, day, request_time, data) VALUES (?, ?, ?, ?, ?)",
              (station_id, int(month), int(day), request_time, str(data)))
    conn.commit()
    conn.close()

    result = {
        "source": "api",
        "data": data,
        "extremes": {
            "max_temperature": max_temp,
            "min_temperature": min_temp
        },
        "trend": trend
    }
    return jsonify(result)

# Nouvel endpoint : GET /map
@app.route('/', methods=['GET'])
def show_map():
    stations = gdf[["station_id", "name", "province", "latitude", "longitude"]].to_dict('records')
    return render_template('map.html', stations=stations)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)