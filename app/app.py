from flask import Flask, jsonify, render_template, request
import sqlite3
from database import init_db, get_weather_data, insert_weather_data
from scraper import scrape_stations
import requests

app = Flask(__name__)

# Initialisation au démarrage
init_db()
scrape_stations()  # Scraper les stations au premier lancement

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stations', methods=['GET'])
def get_stations():
    conn = sqlite3.connect('data/weather.db')
    c = conn.cursor()
    c.execute("SELECT id, latitude, longitude FROM stations")
    stations = [{'id': row[0], 'lat': row[1], 'lon': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(stations)

@app.route('/station/indicator/<station_id>/<month>/<day>', methods=['GET'])
def get_weather_indicator(station_id, month, day):
    # Vérifier si les données sont déjà en cache
    cached_data = get_weather_data(station_id, int(month), int(day))
    if cached_data:
        return jsonify({'source': 'cache', 'data': cached_data})

    # Sinon, faire une requête à l'API
    url = (f"https://api.weather.gc.ca/collections/ltce-temperature/items?"
           f"LOCAL_MONTH={month}&LOCAL_DAY={day}&VIRTUAL_CLIMATE_ID={station_id}"
           f"&sortby=VIRTUAL_CLIMATE_ID,LOCAL_MONTH,LOCAL_DAY&f=json&limit=10000&offset=0")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        insert_weather_data(station_id, int(month), int(day), response.text)
        return jsonify({'source': 'api', 'data': data})
    return jsonify({'error': 'Failed to fetch weather data'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)