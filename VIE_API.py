import requests
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    response.raise_for_status()
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

    # Chargement des annonces existantes si le fichier existe
    if os.path.isfile(filename):
        df_existing = pd.read_csv(filename, sep=';', encoding='utf-8')
        existing_ids = set(df_existing['id'])
    else:
        existing_ids = set()

    # Filtrer les nouvelles annonces
    df_new = df_results[~df_results['id'].isin(existing_ids)]

    if not df_new.empty:
        # Ajout des nouvelles annonces au fichier CSV
        df_new.to_csv(filename, mode='a', index=False, sep=';', encoding='utf-8', header=not os.path.isfile(filename))
        print("Les nouvelles données ont été ajoutées dans 'nom_du_fichier.csv'")

        # Ajout de l'URL pour chaque annonce dans une nouvelle colonne
        df_new['URL'] = df_new['id'].apply(lambda x: f"<a href='https://mon-vie-via.businessfrance.fr/offres/recherche?query=data&id={x}'>Voir l'offre</a>")
        
        # Construction du contenu HTML de l'e-mail
        html_table = df_new.to_html(index=False, columns=['organizationName', 'missionTitle', 'missionDuration', 'countryNameEn', 'cityAffectation', 'URL'], escape=False, border=1)
        
        email_body = f"""
        <html>
        <body>
            <h2>Nouvelles annonces ajoutées</h2>
            <p>{len(df_new)} nouvelles annonces ont été ajoutées. Voici les détails :</p>
            {html_table}
            <p>Bien cordialement,</p>
            <p>Votre système de suivi des annonces VIE</p>
        </body>
        </html>
        """

        # Configuration de l'e-mail
        sender_email = "z.mohamedpro@gmail.com"
        receiver_email = "z.mohamedpro@gmail.com"
        subject = "Nouvelles annonces ajoutées"

        msg = MIMEMultipart("alternative")
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(email_body, 'html'))

        # Connexion au serveur SMTP
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_password = "dvpgwkatxnmgayrd"  # Mot de passe de votre compte email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, smtp_password)
                server.send_message(msg)
                print("E-mail de notification envoyé avec succès.")
        except smtplib.SMTPException as email_err:
            print("Erreur lors de l'envoi de l'e-mail :", email_err)
    else:
        print("Aucune nouvelle annonce à ajouter.")
