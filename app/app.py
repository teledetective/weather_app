import geopandas as gpd
import requests
import os
from flask import Flask, jsonify, render_template, request
from database import get_weather_data, init_db, insert_weather_data
from weather_api import fetch_weather_data, fetch_recent_snow_data, fetch_recent_temperatures
from config import STATIONS_GEOJSON, PAGINATION_LIMIT

app = Flask(__name__)

print("Démarrage de l'application Flask...")
init_db()

def load_stations_from_geojson():
    """Charge les stations directement depuis le fichier GeoJSON."""
    try:
        print(f"Tentative de lecture de {STATIONS_GEOJSON}")
        if not os.path.exists(STATIONS_GEOJSON):
            raise FileNotFoundError(f"Le fichier {STATIONS_GEOJSON} n'existe pas")
        gdf = gpd.read_file(STATIONS_GEOJSON)
        print(f"Colonnes disponibles dans le GeoDataFrame : {list(gdf.columns)}")
        
        # Vérifier que la colonne 'station_id' existe
        if 'station_id' not in gdf.columns:
            raise KeyError(f"La colonne 'station_id' n'est pas présente dans {STATIONS_GEOJSON}")
        
        # Utiliser un dictionnaire pour éliminer les doublons (basé sur station_id)
        stations_dict = {}
        for _, row in gdf.iterrows():
            station_id = row['station_id']
            if station_id not in stations_dict:
                stations_dict[station_id] = {
                    'id': station_id,  
                    'lat': row['geometry'].y,
                    'lon': row['geometry'].x
                }
        
        stations = list(stations_dict.values())
        print(f"Chargé {len(stations)} stations uniques depuis {STATIONS_GEOJSON}")
        return stations
    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        raise
    except Exception as e:
        print(f"Erreur lors du chargement de {STATIONS_GEOJSON} : {type(e).__name__} - {e}")
        raise

@app.route('/')
def index():
    """Affiche la carte avec les stations météo depuis GeoJSON."""
    stations = load_stations_from_geojson()
    return render_template('map.html', stations=stations)

@app.route('/stations', methods=['GET'])
def list_stations():
    """Retourne une liste paginée de stations depuis GeoJSON."""
    stations = load_stations_from_geojson()
    limit = int(request.args.get('limit', PAGINATION_LIMIT))
    offset = int(request.args.get('offset', 0))
    paginated_stations = stations[offset:offset + limit]
    return jsonify(paginated_stations)

@app.route('/station/indicator/<station_id>/<month>/<day>', methods=['GET'])
def get_weather_indicator(station_id, month, day):
    """Récupère les données météo avec cache SQLite."""
    cached_data = get_weather_data(station_id, int(month), int(day))
    if cached_data:
        return jsonify({'source': 'cache', 'data': cached_data})
    data = fetch_weather_data(station_id, month, day)
    if data:
        insert_weather_data(station_id, int(month), int(day), str(data))
        return jsonify({'source': 'api', 'data': data})
    return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.route('/station/snow/<station_id>', methods=['GET'])
def get_recent_snow(station_id):
    """Récupère les données de neige des 5 derniers jours avec cache SQLite."""
    try:
        cached_data = get_weather_data(station_id, 0, 0, key=f"{station_id}_snow_recent")
        if cached_data:
            return jsonify({'source': 'cache', 'data': cached_data})
        snow_data = fetch_recent_snow_data(station_id)
        if snow_data:
            insert_weather_data(station_id, 0, 0, str(snow_data), key=f"{station_id}_snow_recent")
            return jsonify({'station_id': station_id, 'snow_data': snow_data})
        return jsonify({'error': 'Failed to fetch snow data'}), 500
    except Exception as e:
        print(f"Erreur dans get_recent_snow pour {station_id} : {type(e).__name__} - {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/station/temperatures/<station_id>', methods=['GET'])
def get_recent_temperatures(station_id):
    """Récupère les températures max/min récentes avec cache SQLite."""
    cached_data = get_weather_data(station_id, 0, 0, key=f"{station_id}_temp_recent")
    if cached_data:
        return jsonify({'source': 'cache', 'data': cached_data})
    temp_data = fetch_recent_temperatures(station_id)
    if temp_data:
        insert_weather_data(station_id, 0, 0, str(temp_data), key=f"{station_id}_temp_recent")
        return jsonify({'station_id': station_id, 'temp_data': temp_data})
    return jsonify({'error': 'Failed to fetch temperature data'}), 500

if __name__ == '__main__':
    print("Lancement du serveur Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)