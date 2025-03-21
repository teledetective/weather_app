# Image de base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Créer le dossier data pour SQLite
RUN mkdir -p /app/data

# Exposer le port 5000
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app/app.py"]