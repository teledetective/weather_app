import sqlite3

# Chemin de la base de données SQLite
WEATHER_DB_PATH = "data/weather.db"

def init_db():
    """Crée la table 'weather_data' pour le cache des requêtes."""
    try:
        print("Initialisation de la base de données SQLite...")
        conn = sqlite3.connect(WEATHER_DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS weather_data 
                     (cache_key TEXT PRIMARY KEY, data TEXT)''')
        conn.commit()
        print("Base de données initialisée avec succès.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        raise
    finally:
        if conn:
            conn.close()

def insert_weather_data(station_id, month, day, data, key=None):
    """Stocke les données dans la base avec une clé unique."""
    cache_key = key if key else f"{station_id}_{month}_{day}"
    conn = None
    try:
        conn = sqlite3.connect(WEATHER_DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO weather_data (cache_key, data) VALUES (?, ?)", 
                  (cache_key, data))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des données : {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_weather_data(station_id, month, day, key=None):
    """Récupère les données depuis le cache avec une clé unique."""
    cache_key = key if key else f"{station_id}_{month}_{day}"
    conn = None
    try:
        conn = sqlite3.connect(WEATHER_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT data FROM weather_data WHERE cache_key=?", (cache_key,))
        result = c.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des données : {e}")
        raise
    finally:
        if conn:
            conn.close()