# Projet Docker Compose : Application Web avec PostgreSQL et Nginx

Ce projet utilise Docker Compose pour orchestrer une application web Flask avec une base de données PostgreSQL et un serveur web Nginx.

## Structure du projet

Le projet est composé de trois services principaux :

1. **db** : Base de données PostgreSQL avec extension PostGIS
2. **web** : Application web Flask
3. **nginx** : Serveur web Nginx agissant comme proxy inverse

## Prérequis

- Docker
- Docker Compose

## Configuration

Le projet utilise un fichier `.env` pour les variables d'environnement. Assurez-vous de le configurer correctement avant de lancer l'application.

## Démarrage

Pour construire l'application :

`docker compose build`

Pour lancer l'application, exécutez la commande suivante à la racine du projet :

`docker compose up -d`

L'application sera visible : http://localhost