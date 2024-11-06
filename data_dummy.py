import mysql.connector
from datetime import datetime, timedelta
import random

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env

load_dotenv()

# Récupérer les informations de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Connexion à la base de données MySQL
def create_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

# Fonction pour créer des enregistrements factices dans la base de données
def create_dummy_jobs():
    connection = create_connection()
    cursor = connection.cursor()

    # Génération de données aléatoires
    positions = ["Engineer", "Manager", "Technician", "Analyst", "Developer"]
    degrees = ["Bachelor's", "Master's", "PhD", "Diploma"]
    
    for _ in range(100):
        position_name = random.choice(positions)
        date = datetime.now() - timedelta(days=random.randint(0, 365))  # Une date dans la dernière année
        required_degree = random.choice(degrees)
        experience = random.randint(0, 20)  # Expérience entre 0 et 20 ans

        # Insérer l'enregistrement dans la table
        cursor.execute(
            "INSERT INTO application (PositionName, Date, RequiredDegree, Experience) VALUES (%s, %s, %s, %s)",
            (position_name, date.strftime('%Y-%m-%d'), required_degree, experience)
        )
    
    # Valider les changements et fermer la connexion
    connection.commit()
    cursor.close()
    connection.close()
    print("100 enregistrements factices ont été créés avec succès.")

# Exécution de la fonction si le script est lancé
if __name__ == "__main__":
    create_dummy_jobs()
