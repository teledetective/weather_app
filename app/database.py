import sqlite3
import json
from config import DATABASE_PATH

def init_db():
    """Initialise la base de données SQLite avec une table pour stocker les données météo."""
    print("Initialisation de la base de données SQLite...")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                station_id TEXT,
                month INTEGER,
                day INTEGER,
                data TEXT,
                cache_key TEXT UNIQUE,
                PRIMARY KEY (station_id, month, day)
            )
        ''')
        conn.commit()
        print("Base de données initialisée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        raise
    finally:
        conn.close()

def get_weather_data(station_id, month, day, key=None):
    """Récupère les données météo depuis la base de données."""
    cache_key = f"{station_id}_{month}_{day}" if key is None else key
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT data FROM weather_data WHERE cache_key=?", (cache_key,))
        result = c.fetchone()
        if result:
            return json.loads(result[0])
        return None
    except Exception as e:
        print(f"Erreur dans get_weather_data pour cache_key={cache_key}: {e}")
        raise
    finally:
        conn.close()

def insert_weather_data(station_id, month, day, data, key=None):
    """Insère ou met à jour les données météo dans la base de données."""
    cache_key = f"{station_id}_{month}_{day}" if key is None else key
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        data_json = json.dumps(data)  # Convertir en JSON valide
        c.execute("INSERT OR REPLACE INTO weather_data (station_id, month, day, data, cache_key) VALUES (?, ?, ?, ?, ?)",
                  (station_id, month, day, data_json, cache_key))
        conn.commit()
    except Exception as e:
        print(f"Erreur dans insert_weather_data pour cache_key={cache_key}: {e}")
        raise
    finally:
        conn.close()