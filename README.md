# Weather API Project

## Description
Une API Flask conteneurisée avec Docker pour scraper des stations météo, afficher leur position sur une carte interactive avec Leaflet, et récupérer des données climatiques via api.weather.gc.ca.

## Prérequis
- Docker installé

## Instructions
1. Construire l'image Docker :
   ```bash
   docker build -t weather_app .