import mysql.connector
from datetime import datetime, timedelta
import random

import os
from dotenv import load_dotenv
import json


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

    job_names = ["Engineer", "Manager", "Technician", "Analyst", "Developer"]
    degrees = ["Bachelor's", "Master's", "PhD", "Diploma"]
    softskills = ["Communication", "Teamwork", "Problem-solving", "Adaptability", "Creativity"]
    hardskills = ["Python", "SQL", "Data Analysis", "Project Management", "Machine Learning"]

    for _ in range(100):
        reference = f"JOB-{random.randint(1000, 9999)}"
        name = random.choice(job_names)
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        experience = random.randint(1, 10)
        degree = random.choice(degrees)
        
        job_softskills = json.dumps(random.sample(softskills, random.randint(1, 3)))
        job_hardskills = json.dumps(random.sample(hardskills, random.randint(1, 3)))

        # Insérer l'enregistrement dans la table job
        cursor.execute(
            "INSERT INTO job (reference, name, date, experience, degree, softskills, hardskills) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (reference, name, date.strftime('%Y-%m-%d'), experience, degree, job_softskills, job_hardskills)
        )

    connection.commit()
    cursor.close()
    connection.close()

# Créer des enregistrements factices pour la table application
# Sélectionner 10 offres aléatoires dans la table job
def get_random_jobs():
    connection = create_connection()
    cursor = connection.cursor()

    # Sélectionner 10 offres au hasard
    cursor.execute("SELECT reference FROM job ORDER BY RAND() LIMIT 10")
    job_references = [row[0] for row in cursor.fetchall()]

    connection.close()
    return job_references

# Créer des applications pour les offres sélectionnées
def create_applications_for_jobs(job_references):
    connection = create_connection()
    cursor = connection.cursor()

    degrees = ["Bachelor's", "Master's", "PhD", "Diploma"]
    softskills = ["Communication", "Teamwork", "Problem-solving", "Adaptability", "Creativity"]
    hardskills = ["Python", "SQL", "Data Analysis", "Project Management", "Machine Learning"]

    # Pour chaque offre, créer 10 applications
    for reference in job_references:
        for i in range(10):
            score = round(random.uniform(0, 99), 2)
            first_name = f"First{i+1}"
            last_name = f"Last{i+1}"
            degree = random.choice(degrees)
            experience = random.randint(1, 10)
            
            # Convertir les listes de compétences en chaînes JSON et les stocker sous forme de texte
            application_softskills = json.dumps(random.sample(softskills, random.randint(1, 3)))
            application_hardskills = json.dumps(random.sample(hardskills, random.randint(1, 3)))
            application_date = datetime.now() - timedelta(days=random.randint(0, 365))

            # Insérer l'enregistrement dans la table application
            try:
                cursor.execute(
                    "INSERT INTO application (reference, score, first_name, last_name, degree, experience, hardskills, softskills, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (reference, score, first_name, last_name, degree, experience, application_hardskills, application_softskills, application_date.strftime('%Y-%m-%d'))
                )
                print(f"Insertion réussie pour l'application : {first_name} {last_name} pour le job {reference}")
            except mysql.connector.Error as err:
                print(f"Erreur lors de l'insertion de l'application : {err}")

    connection.commit()
    cursor.close()
    connection.close()
    print("Insertion des applications terminée avec succès.")

# Exécuter les fonctions pour créer les enregistrements
if __name__ == "__main__":
    # Sélectionner 10 offres au hasard
    job_references = get_random_jobs()
    print(f"10 offres sélectionnées : {job_references}")

    # Créer 10 applications pour chaque offre sélectionnée
    create_applications_for_jobs(job_references)