import requests
from bs4 import BeautifulSoup
from database import init_db, insert_station
from app.config import SCRAPER_URL

def scrape_stations():
    response = requests.get(SCRAPER_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Hypothétique : à adapter selon la structure réelle du site
    stations = soup.select('.station-item')  # Remplacez par le sélecteur correct
    for station in stations:
        station_id = station.get('data-id', 'VSQC136')  # Exemple par défaut
        lat = station.get('data-lat', '45.5017')        # Exemple par défaut
        lon = station.get('data-lon', '-73.5673')       # Exemple par défaut
        if station_id and lat and lon:
            insert_station(station_id, float(lat), float(lon))

if __name__ == "__main__":
    init_db()
    scrape_stations()