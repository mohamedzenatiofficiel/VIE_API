import requests
import pandas as pd
import os

# Définition de l'URL et des en-têtes pour la requête
url = "https://civiweb-api-prd.azurewebsites.net/api/Offers/search"
headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://mon-vie-via.businessfrance.fr",
    "Referer": "https://mon-vie-via.businessfrance.fr/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# Définition des données de la requête pour la recherche
data = {
    "limit": 12,
    "skip": 0,
    "query": "data",
    "missionsDurations": ["12", "18", "24"],
    "activitySectorId": [],
    "companiesSizes": [],
    "countriesIds": [],
    "entreprisesIds": [0],
    "gerographicZones": [],
    "missionStartDate": None,
    "missionsTypesIds": [],
    "specializationsIds": [],
    "studiesLevelId": []
}

# Envoi de la requête POST pour récupérer les données
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Vérifie si la requête a été réussie
    data = response.json()
except requests.exceptions.HTTPError as err:
    print("Erreur HTTP :", err)
    print("Contenu de la réponse :", response.text)
except Exception as e:
    print("Erreur :", e)
else:
    # Création d'un DataFrame à partir des résultats de l'API
    df_results = pd.DataFrame(data['result'])

    # Sélection des colonnes à conserver
    colonnes_a_conserver = [
        'id', 'organizationName', 'missionTitle', 'missionDuration', 
        'viewCounter', 'missionType', 'countryNameEn', 'cityAffectation'
    ]
    df_results = df_results[colonnes_a_conserver]

    # Nom du fichier CSV
    filename = 'nom_du_fichier.csv'

    # Vérifie si le fichier existe déjà pour gérer l'incrément
    if os.path.isfile(filename):
        # Ajout des données sans réécrire l'en-tête si le fichier existe
        df_results.to_csv(filename, mode='a', index=False, sep=';', encoding='utf-8', header=False)
    else:
        # Création du fichier avec l'en-tête si le fichier n'existe pas
        df_results.to_csv(filename, mode='w', index=False, sep=';', encoding='utf-8', header=True)

    print("Les nouvelles données ont été ajoutées dans 'nom_du_fichier.csv'")
