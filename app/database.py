# database.py : Gestion de la base de données SQLite pour stocker les données météo
import sqlite3
import json
from config import DATABASE_PATH

def init_db():
    """Initialise la base SQLite avec une table pour les données météo."""
    # On annonce l'initialisation
    print("Initialisation de la base de données SQLite...")
    try:
        # On se connecte à la base
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        # On crée la table si elle n'existe pas
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
        # On valide les changements
        conn.commit()
        print("Base de données initialisée avec succès.")
    except Exception as e:
        # En cas d'erreur, on affiche le problème
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        raise
    finally:
        # On ferme la connexion
        conn.close()

def get_weather_data(station_id, month, day, key=None):
    """Récupère les données météo depuis la base."""
    # On génère une clé de cache si aucune n'est fournie
    cache_key = f"{station_id}_{month}_{day}" if key is None else key
    try:
        # Connexion à la base
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        # On récupère les données associées à la clé
        c.execute("SELECT data FROM weather_data WHERE cache_key=?", (cache_key,))
        result = c.fetchone()
        if result:
            # Si on a un résultat, on le parse en JSON
            return json.loads(result[0])
        return None
    except Exception as e:
        # On log l'erreur pour debug
        print(f"Erreur dans get_weather_data pour cache_key={cache_key}: {e}")
        raise
    finally:
        # Toujours fermer la connexion
        conn.close()

def insert_weather_data(station_id, month, day, data, key=None):
    """Insère ou met à jour les données météo dans la base."""
    # Clé de cache par défaut si pas fournie
    cache_key = f"{station_id}_{month}_{day}" if key is None else key
    try:
        # Connexion à la base
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        # On convertit les données en JSON
        data_json = json.dumps(data)
        # On insère ou remplace les données
        c.execute("INSERT OR REPLACE INTO weather_data (station_id, month, day, data, cache_key) VALUES (?, ?, ?, ?, ?)",
                  (station_id, month, day, data_json, cache_key))
        # On valide
        conn.commit()
    except Exception as e:
        # On affiche l'erreur si ça foire
        print(f"Erreur dans insert_weather_data pour cache_key={cache_key}: {e}")
        raise
    finally:
        # On ferme la connexion
        conn.close()