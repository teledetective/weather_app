# from flask import Flask, render_template
# from sqlalchemy import create_engine, text
# import os

# app = Flask(__name__, template_folder='/app/templates')

# # Récupération des variables d'environnement pour la base de données
# DATABASE_URL = os.environ.get('DATABASE_URL', f'postgresql://test_user:test_db@test_host/test_db')

# @app.route('/')
# def home():
#     # Connexion à la base de données
#     engine = create_engine(DATABASE_URL)
#     with engine.connect() as conn:
#         # Récupération des points géographiques
#         result = conn.execute(text("SELECT name, ST_X(geom) as longitude, ST_Y(geom) as latitude FROM points;"))
#         points = [dict(row) for row in result.mappings()]  # Convertir les résultats en dictionnaire
    
#     # Rendre le template HTML avec les données
#     return render_template('index.html', points=points)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)

# on importe les libs
from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# on crée l'application
app = Flask(__name__)

# Configuration de la clé secrète pour JWT
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Remplacez par une clé secrète forte
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60
# Configuration de l'emplacement du token JWT
# il est préférable d'utiliser les cookies pour stocker le token JWT
# car les cookies sont automatiquement envoyés par le navigateur
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

# Initialisation de l'extension JWT
jwt = JWTManager(app)

# Base de données fictive pour les utilisateurs (à remplacer par une vraie base)
users = {
    "user": {"password": "pwd"}
}

# définir une base de données SQLITE
DATABASE = 'points.db'


def initdb():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # créer une table points si elle n'existe pas
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS points (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lat REAL, lon REAL)'
        )
        # inserer des points fictifs
        cursor.execute(
            'INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)',
            ('Point 1', 48.8566, 2.3522)
        )
        # créer une table users si elle n'existe pas
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)'
        )
        # inserer des utilisateurs fictifs
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            ('user', 'pwd')
        )
        conn.commit()

# si le fichier de base de données n'existe pas, on l'initialise
try:
    with open(DATABASE):
        pass
except FileNotFoundError:
    # créer la table points
    initdb()


# Route GET : Afficher la page d'accueil
@app.route('/')
def home():
    # on cherche tous les points
    rows = getAllPoints()
    # on affiche la page d'accueil
    return render_template('index.html', points=rows)

# Route POST : Ajouter un nouveau point
@app.route('/add', methods=['POST'])
def add_point():
    # Récupérer les données du formulaire
    name = request.form['name']
    lat = request.form['lat']
    lon = request.form['lon']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)',
            (name, lat, lon)
        )
        conn.commit()
        # redirect to url '/'
        return redirect('/')

# Route GET : Supprimer un point
@app.route('/delete/<int:id>')
def delete_point(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM points WHERE id = ?', (id,))
        conn.commit()
        
        # redirect to url '/'        
        return redirect('/')
    
# Route GET : Afficher le formulaire d'édition d'un point
@app.route('/edit/<int:id>')
def edit_point(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM points WHERE id = ?', (id,))
        row = cursor.fetchone()
        
        return render_template('index.html', id=row[0], point=row, points=getAllPoints())

# Route POST : Mettre à jour un point
@app.route('/update', methods=['POST'])
def update_point():
    # Récupérer les données du formulaire
    id = request.form['id']
    name = request.form['name']
    lat = request.form['lat']
    lon = request.form['lon']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE points SET name = ?, lat = ?, lon = ? WHERE id = ?',
            (name, lat, lon, id)
        )
        conn.commit()
        
        # redirect to url '/'
        redirect_url = '/'
        return redirect(redirect_url)

# Route GET : Afficher la carte
@app.route('/map')
# on protège la route avec JWT
@jwt_required(locations=["cookies"])
def map():
    current_user = get_jwt_identity()
    print(f"User {current_user} is accessing")
    # on cherche tous les points
    rows = getAllPoints()

    # find the center of the points
    lat = 0
    lon = 0

    for row in rows:
        lat += row[2]
        lon += row[3]
    
    lat /= len(rows)
    lon /= len(rows)

    # on affiche la page de la carte
    return render_template('map.html', lat=lat, lon=lon, points=rows)

# Fonction pour récupérer tous les points
def getAllPoints():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM points')
        rows = cursor.fetchall()
    return rows

# on définit l'action en cas de token expiré
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return redirect(url_for('login'))

def check_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        row = cursor.fetchone()
        if row:
            return True
        else:
            return False

# on définit l'action en cas de token invalide
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    # Redirige l'utilisateur non authentifié vers la page de connexion
    return redirect("/login")

# Route pour afficher le formulaire de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.form.get("username")
        password = request.form.get("password")

        # Vérification des identifiants
        if not check_user(username, password):
            return render_template('login.html', error="Nom d'utilisateur ou mot de passe incorrect")

        # Création du token JWT
        access_token = create_access_token(identity=username)
        # log in concole
        print(f"User {username} logged in")
        response = make_response(redirect(url_for("map")))
        response.set_cookie("access_token_cookie", access_token, httponly=True)
        return response

    # Affichage du formulaire si méthode GET
    return render_template('login.html')

@app.route("/logout")
def logout():
    # Supprime le cookie contenant le token JWT
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("access_token_cookie")
    return response

# on lance l'application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)