# app.py : Application Flask principale pour afficher et gérer les données des stations météo
import geopandas as gpd
import requests
import os
from flask import Flask, jsonify, render_template, request
from database import get_weather_data, init_db, insert_weather_data
from weather_api import fetch_weather_data, fetch_recent_snow_data, fetch_recent_temperatures
from config import STATIONS_GEOJSON, PAGINATION_LIMIT
from datetime import datetime

# On crée l'application Flask
app = Flask(__name__)

# Message pour dire que l'appli démarre
print("Démarrage de l'application Flask...")
# On initialise la base de données SQLite
init_db()

def load_stations_from_geojson():
    """Charge toutes les stations météo depuis le fichier GeoJSON."""
    try:
        # On tente de lire le fichier GeoJSON
        print(f"Tentative de lecture de {STATIONS_GEOJSON}")
        # On vérifie si le fichier existe vraiment
        if not os.path.exists(STATIONS_GEOJSON):
            raise FileNotFoundError(f"Le fichier {STATIONS_GEOJSON} n'existe pas")
        # On charge le fichier dans un GeoDataFrame
        gdf = gpd.read_file(STATIONS_GEOJSON)
        # On affiche les colonnes dispo pour debug
        print(f"Colonnes disponibles dans le GeoDataFrame : {list(gdf.columns)}")
        
        # On s'assure que la colonne station_id est bien là
        if 'station_id' not in gdf.columns:
            raise KeyError(f"La colonne 'station_id' n'est pas présente dans {STATIONS_GEOJSON}")
        
        # Dico pour stocker les stations uniques
        stations_dict = {}
        # On parcourt chaque ligne du GeoDataFrame
        for _, row in gdf.iterrows():
            # On met l'ID en majuscules pour être cohérent
            station_id = row['station_id'].upper()
            # On évite les doublons
            if station_id not in stations_dict:
                stations_dict[station_id] = {
                    'id': station_id,
                    'lat': row['geometry'].y,
                    'lon': row['geometry'].x
                }
        
        # On transforme le dico en liste
        stations = list(stations_dict.values())
        # On log combien de stations on a chargé
        print(f"Chargé {len(stations)} stations uniques depuis {STATIONS_GEOJSON}")
        return stations
    except FileNotFoundError as e:
        # Si le fichier est introuvable, on affiche l'erreur
        print(f"Erreur : {e}")
        raise
    except Exception as e:
        # Pour toute autre erreur, on donne des détails
        print(f"Erreur lors du chargement de {STATIONS_GEOJSON} : {type(e).__name__} - {e}")
        raise

@app.route('/')
def index():
    """Affiche la carte avec toutes les stations météo depuis GeoJSON."""
    # On charge les stations depuis le GeoJSON
    stations = load_stations_from_geojson()
    # On rend le template de la carte avec les stations
    return render_template('map.html', stations=stations)

@app.route('/stations', methods=['GET'])
def list_stations():
    """Retourne une liste paginée des stations depuis GeoJSON."""
    # On charge les stations
    stations = load_stations_from_geojson()
    # On récupère les paramètres de pagination
    limit = int(request.args.get('limit', PAGINATION_LIMIT))
    offset = int(request.args.get('offset', 0))
    # On découpe la liste pour la pagination
    paginated_stations = stations[offset:offset + limit]
    # On renvoie les stations en JSON
    return jsonify(paginated_stations)

@app.route('/station/indicator/<station_id>/<month>/<day>', methods=['GET'])
def get_weather_indicator(station_id, month, day):
    """Récupère les données météo avec cache SQLite."""
    try:
        # On check d'abord si les données sont en cache
        cached_data = get_weather_data(station_id, int(month), int(day))
        if cached_data:
            # Si on a du cache, on renvoie direct
            return jsonify({'source': 'cache', 'data': cached_data})
        # Sinon, on va chercher via l'API
        data = fetch_weather_data(station_id, month, day)
        if data:
            # On sauvegarde dans le cache
            insert_weather_data(station_id, int(month), int(day), data)
            return jsonify({'source': 'api', 'data': data})
        # Si ça foire, on renvoie une erreur
        return jsonify({'error': 'Failed to fetch weather data'}), 500
    except Exception as e:
        # On log l'erreur pour debug
        print(f"Erreur dans get_weather_indicator pour {station_id}/{month}/{day} : {type(e).__name__} - {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/station/snow/<station_id>', methods=['GET'])
def get_recent_snow(station_id):
    """Récupère la précipitation de neige record pour aujourd'hui avec cache."""
    try:
        # On récupère la date du jour
        today = datetime.now()
        current_month = today.month
        current_day = today.day
        # On crée une clé unique pour le cache
        cache_key = f"{station_id}_snow_{today.year}-{current_month:02d}-{current_day:02d}"

        # On vérifie si on force le refresh
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Si pas de refresh forcé, on check le cache
        if not force_refresh:
            cached_data = get_weather_data(station_id, 0, 0, key=cache_key)
            if cached_data:
                # Si on a du cache, on le renvoie
                print(f"Données de neige pour {station_id} récupérées depuis le cache (clé: {cache_key})")
                return jsonify({'source': 'cache', 'data': cached_data})

        # Sinon, on va chercher les données via l'API
        snow_data = fetch_recent_snow_data(station_id)
        if snow_data:
            # On met en cache les nouvelles données
            insert_weather_data(station_id, 0, 0, snow_data, key=cache_key)
            print(f"Données de neige pour {station_id} mises en cache (clé: {cache_key})")
            return jsonify({'station_id': station_id, 'snow_data': snow_data})
        # Si ça foire, erreur 500
        return jsonify({'error': 'Failed to fetch snow data'}), 500
    except Exception as e:
        # On log l'erreur pour comprendre ce qui cloche
        print(f"Erreur dans get_recent_snow pour {station_id} : {type(e).__name__} - {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/station/temperatures/<station_id>', methods=['GET'])
def get_recent_temperatures(station_id):
    """Récupère les températures max/min pour aujourd'hui avec cache."""
    try:
        # On récupère la date actuelle
        today = datetime.now()
        current_month = today.month
        current_day = today.day
        # Clé unique pour le cache
        cache_key = f"{station_id}_temp_{today.year}-{current_month:02d}-{current_day:02d}"

        # On regarde si on force le refresh
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Si pas de refresh, on check le cache
        if not force_refresh:
            cached_data = get_weather_data(station_id, 0, 0, key=cache_key)
            if cached_data:
                print(f"Données de température pour {station_id} récupérées depuis le cache (clé: {cache_key})")
                return jsonify({'source': 'cache', 'data': cached_data})

        # Sinon, on fetch via l'API
        temp_data = fetch_recent_temperatures(station_id)
        if temp_data:
            # On cache les données
            insert_weather_data(station_id, 0, 0, temp_data, key=cache_key)
            print(f"Données de température pour {station_id} mises en cache (clé: {cache_key})")
            return jsonify({'station_id': station_id, 'temp_data': temp_data})
        # Erreur si ça rate
        return jsonify({'error': 'Failed to fetch temperature data'}), 500
    except Exception as e:
        # On log l'erreur pour debug
        print(f"Erreur dans get_recent_temperatures pour {station_id} : {type(e).__name__} - {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # On lance le serveur Flask
    print("Lancement du serveur Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)