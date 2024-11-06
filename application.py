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
def fetch_jobs():
    connection = create_connection()
    query = "SELECT * FROM application"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Filtrer les offres d'emploi par date
def filter_jobs_by_date(start_date, end_date):
    connection = create_connection()
    query = """
        SELECT * FROM application 
        WHERE date BETWEEN %s AND %s
    """
    df = pd.read_sql(query, connection, params=(start_date, end_date))
    connection.close()
    return df

# Streamlit interface
def main():
    st.title("Job Application Interface")

    # Date filter section
    st.subheader("Filter Jobs by Date")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Begin Date", datetime.now())
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    # Fetch and filter job listings
    if st.button("Filter"):
        filtered_jobs = filter_jobs_by_date(start_date, end_date)
        st.write("Filtered Job Listings")
        st.dataframe(filtered_jobs)
   
if __name__ == "__main__":
    main()