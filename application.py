import streamlit as st
import mysql.connector
import pandas as pd
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

# Récupérer les offres d'emploi depuis MySQL
def get_jobs():
    connection = create_connection()
    query = "SELECT reference, name FROM job"
    jobs = pd.read_sql(query, connection)
    connection.close()
    return jobs

# Récupérer les informations d'un job spécifique
def get_job_info(reference):
    connection = create_connection()
    query = "SELECT * FROM job WHERE reference = %s"
    job_info = pd.read_sql(query, connection, params=(reference,))
    connection.close()
    return job_info
# Filtrer les applications pour un job spécifique et une plage de dates, et trier par score décroissant
def filter_applications(reference, start_date, end_date):
    connection = create_connection()
    query = """
        SELECT * FROM application 
        WHERE reference = %s AND date BETWEEN %s AND %s
        ORDER BY score DESC
    """
    applications = pd.read_sql(query, connection, params=(reference, start_date, end_date))
    connection.close()
    return applications

# Fonction pour appliquer un dégradé de couleur rouge-vert en fonction du score
def apply_score_color(score):
    if score >= 50:
        # Interpoler le vert pour les scores entre 50 et 100
        green_intensity = int(255 * (score - 50) / 50)  # Plus le score est élevé, plus c'est vert
        return f"background-color: rgb(0, {green_intensity}, 0); color: white;"
    else:
        # Interpoler le rouge pour les scores entre 0 et 50
        red_intensity = int(255 * (50 - score) / 50)  # Plus le score est faible, plus c'est rouge
        return f"background-color: rgb({red_intensity}, 0, 0); color: white;"

def main():
    st.title("Job Application Interface")

    # Récupérer et afficher la liste des jobs dans un combo-box
    jobs = get_jobs()
    job_selection = st.selectbox(
        "Sélectionnez un job",
        options=jobs["reference"] + " - " + jobs["name"],
        index=0
    )

    # Extraire la référence du job sélectionné
    selected_reference = job_selection.split(" - ")[0]

    # Afficher les informations du job sélectionné
    st.subheader("Informations du job")
    job_info = get_job_info(selected_reference)
    st.write(job_info)

    # Sélection de la plage de dates
    st.subheader("Filtrer les candidatures")
    start_date = st.date_input("Date de début", datetime.now())
    end_date = st.date_input("Date de fin", datetime.now())

    # Filtrer et afficher les candidatures
    if st.button("Filtrer les candidatures"):
        applications = filter_applications(selected_reference, start_date, end_date)
        
        # Supprimer la colonne 'reference' du DataFrame
        if "reference" in applications.columns:
            applications = applications.drop(columns=["reference"])

        # Appliquer le style de dégradé rouge-vert sur la colonne 'score'
        if not applications.empty:
            st.subheader("Candidatures filtrées")
            styled_applications = applications.style.applymap(
                lambda score: apply_score_color(score) if isinstance(score, (int, float)) else "", 
                subset=["score"]
            )
            st.dataframe(styled_applications)
        else:
            st.write("Aucune candidature trouvée pour ce filtre.")

if __name__ == "__main__":
    main()