import requests
import geopandas as gpd
import sqlite3
from flask import Flask, jsonify, request
from shapely.geometry import Point
from datetime import datetime

app = Flask(__name__)

# Charger les données géospatiales
STATIONS_GEOJSON = "stations.geojson"
gdf = gpd.read_file(STATIONS_GEOJSON)

# Initialiser la base de données SQLite
def init_db():
    conn = sqlite3.connect("weather_requests.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_requests
                 (station_id TEXT, month INTEGER, day INTEGER, request_time TEXT, data TEXT,
                  PRIMARY KEY (station_id, month, day))''')
    conn.commit()
    conn.close()

# Fonction pour calculer la distance (approximation simple en kilomètres)
def calculate_distance(lat1, lon1, lat2, lon2):
    # Approximation simple (distance euclidienne projetée, pour des petites distances)
    # Pour une précision géodésique, on pourrait utiliser geopy, mais ici on simplifie
    return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111  # 1 degré ≈ 111 km

# Initialiser la base de données au démarrage
init_db()

# Endpoint 1 : GET /stations
@app.route('/stations', methods=['GET'])
def get_stations():
    # Convertir le GeoDataFrame en liste de dictionnaires
    stations = gdf[["station_id", "name", "province", "element", "latitude", "longitude"]].to_dict('records')
    return jsonify(stations)

# Endpoint 2 : GET /stations/near?lat=<latitude>&lon=<longitude>
@app.route('/stations/near', methods=['GET'])
def get_nearby_stations():
    # Récupérer les paramètres lat et lon
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid latitude or longitude"}), 400

    # Créer un point pour la position donnée
    user_point = Point(lon, lat)

    # Calculer la distance entre la position donnée et chaque station
    gdf_copy = gdf.copy()
    gdf_copy['distance_km'] = gdf.apply(
        lambda row: calculate_distance(lat, lon, row['latitude'], row['longitude']),
        axis=1
    )

    # Trier par distance et prendre les 5 stations les plus proches
    nearest_stations = gdf_copy.sort_values(by='distance_km').head(5)
    result = nearest_stations[["station_id", "name", "province", "latitude", "longitude", "distance_km"]].to_dict('records')
    return jsonify(result)

# Endpoint 3 : GET /station/indicator/<id_station>/<month>/<day>
@app.route('/station/indicator/<station_id>/<month>/<day>', methods=['GET'])
def get_weather_indicator(station_id, month, day):
    # Vérifier si la station existe dans le GeoDataFrame
    if station_id not in gdf['station_id'].values:
        return jsonify({"error": "Station not found"}), 404

    # Vérifier si les données sont déjà en cache
    conn = sqlite3.connect("weather_requests.db")
    c = conn.cursor()
    c.execute("SELECT data FROM weather_requests WHERE station_id = ? AND month = ? AND day = ?",
              (station_id, int(month), int(day)))
    cached_data = c.fetchone()
    if cached_data:
        conn.close()
        return jsonify({"source": "cache", "data": eval(cached_data[0])})

    # Construire l'URL pour l'API weather.gc.ca
    url = (f"https://api.weather.gc.ca/collections/ltce-temperature/items?"
           f"LOCAL_MONTH={month.zfill(2)}&LOCAL_DAY={day.zfill(2)}&VIRTUAL_CLIMATE_ID={station_id}"
           f"&sortby=VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY&f=json&limit=10000&offset=0")
    
    # Faire une requête à l'API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        conn.close()
        return jsonify({"error": "Failed to fetch weather data"}), 500

    # Parser les données
    data = response.json()
    features = data.get("features", [])

    # Extraire les extrêmes (températures max et min)
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

    # Analyser la progression/régression (simplifié : comparer avec une valeur moyenne historique fictive)
    # Pour une analyse réelle, il faudrait des données historiques, ici on simule
    historical_max_avg = 20.0  # Valeur fictive pour l'exemple
    historical_min_avg = 10.0  # Valeur fictive pour l'exemple
    trend = {}
    if max_temp is not None:
        trend["max_temperature"] = "progression" if max_temp > historical_max_avg else "regression"
    if min_temp is not None:
        trend["min_temperature"] = "progression" if min_temp > historical_min_avg else "regression"

    # Stocker la requête et les résultats dans la base de données
    request_time = datetime.utcnow().isoformat()
    c.execute("INSERT OR REPLACE INTO weather_requests (station_id, month, day, request_time, data) VALUES (?, ?, ?, ?, ?)",
              (station_id, int(month), int(day), request_time, str(data)))
    conn.commit()
    conn.close()

    # Retourner les résultats
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)