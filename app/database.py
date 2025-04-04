import sqlite3
from app.config import WEATHER_DB_PATH

def init_db():
    conn = sqlite3.connect(WEATHER_DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations 
                 (id TEXT PRIMARY KEY, latitude REAL, longitude REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS weather_data 
                 (station_id TEXT, month INTEGER, day INTEGER, data TEXT, 
                 FOREIGN KEY(station_id) REFERENCES stations(id))''')
    conn.commit()
    conn.close()

def insert_station(station_id, latitude, longitude):
    conn = sqlite3.connect(WEATHER_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO stations (id, latitude, longitude) VALUES (?, ?, ?)", 
              (station_id, latitude, longitude))
    conn.commit()
    conn.close()

def insert_weather_data(station_id, month, day, data):
    conn = sqlite3.connect(WEATHER_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO weather_data (station_id, month, day, data) VALUES (?, ?, ?, ?)", 
              (station_id, month, day, data))
    conn.commit()
    conn.close()

def get_weather_data(station_id, month, day):
    conn = sqlite3.connect(WEATHER_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM weather_data WHERE station_id=? AND month=? AND day=?", 
              (station_id, month, day))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None