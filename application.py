import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt # type: ignore
from dotenv import load_dotenv
import openai # type: ignore
from langchain import SQLDatabase # type: ignore
from langchain.llms import OpenAI # type: ignore
from langchain.agents import * # type: ignore
from langchain.sql_database import SQLDatabase # type: ignore
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit # type: ignore
from langchain_community.agent_toolkits import create_sql_agent # type: ignore
from langchain.chat_models import ChatOpenAI # type: ignore
from langchain.chains import create_sql_query_chain # type: ignore

# Charger les variables d'environnement depuis le fichier .env

load_dotenv()

# Récupérer les informations de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


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
    query = "SELECT RoleID, Role FROM jobs"
    jobs = pd.read_sql(query, connection)
    connection.close()
    return jobs

def initialize_sql_chain():
    db =SQLDatabase.from_uri(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    chain = create_sql_query_chain(db=db, llm=llm)
  
    return chain



# Récupérer les informations d'un job spécifique
def get_job_info(RoleID):
    connection = create_connection()
    query = "SELECT * FROM jobs WHERE RoleID = %s"
    job_info = pd.read_sql(query, connection, params=(RoleID,))
    connection.close()
    return job_info
# Filtrer les applications pour un job spécifique et une plage de dates, et trier par score décroissant
def query_applications(query):
    connection = create_connection()
    applications = pd.read_sql(query, connection)
    connection.close()
    return applications

def filter_applications(RoleID, start_date, end_date):
    connection = create_connection()
    query = """
        SELECT * FROM jobapplications
        WHERE RoleID = %s AND date BETWEEN %s AND %s
        ORDER BY Score DESC
    """
    applications = pd.read_sql(query, connection, params=(RoleID, start_date, end_date))
    connection.close()
    return applications

# Récupérer les scores pour une application spécifique

def get_application_scores(application_id):
    connection = create_connection()
    query = """
        SELECT Experience, Degree, HardSkills, SoftSkills
        FROM scores
        WHERE ApplicationID = %s
    """
    scores = pd.read_sql(query, connection, params=(application_id,))
    connection.close()
    if not scores.empty:
        return scores.iloc[0].to_dict()
    else:
        return None


# Fonction pour appliquer un dégradé de couleur rouge-vert en fonction du score

def apply_score_color(Score):
    if Score >= 50:
        # Interpoler le vert pour les scores entre 50 et 100
        green_intensity = int(255 * (Score - 50) / 50)  # Plus le score est élevé, plus c'est vert
        return f"background-color: rgb(0, {green_intensity}, 0); color: white;"
    else:
        # Interpoler le rouge pour les scores entre 0 et 50
        red_intensity = int(255 * (50 - Score) / 50)  # Plus le score est faible, plus c'est rouge
        return f"background-color: rgb({red_intensity}, 0, 0); color: white;"

# Fonction pour afficher un diagramme radar des détails de score
def show_score_radar(score_details):
    labels = list(score_details.keys())
    values = list(score_details.values())
    
    # Création de l'angle pour chaque axe
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Fermer le graphe
    values += values[:1]
    angles += angles[:1]

    # Création de la figure avec une taille réduite
    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='b', alpha=0.25)
    ax.plot(angles, values, color='b', linewidth=2)
    ax.set_yticks([20, 40, 60, 80,100])
    ax.set_yticklabels(['20', '40', '60', '80','100'], color="grey", size=6)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="black", size=6)
    
    st.pyplot(fig)

def default_filter():
    st.title("Job Application Interface")

    st.subheader("Filtering Job")

    # Récupérer et afficher la liste des jobs dans un combo-box
    jobs = get_jobs()
    job_selection = st.selectbox(
        "Sélectionnez un job",
        options=jobs["RoleID"] + " - " + jobs["Role"],
        index=0
    )

    # Extraire la référence du job sélectionné
    selected_reference = job_selection.split(" - ")[0]

    # Sélection de la plage de dates
    st.subheader("Filter applications")
    start_date = st.date_input("Start date", datetime(2023, 1, 1))
    end_date = st.date_input("End date", datetime.now())

    # Filtrer les candidatures et éviter le rechargement
    if 'applications' not in st.session_state:
        st.session_state.applications = None
    if st.button("Filter applications"):
        st.session_state.applications = filter_applications(selected_reference, start_date, end_date)

    # Afficher les candidatures si disponibles
    applications = st.session_state.applications
    if applications is not None:
        st.subheader("Filtering Applications")
        
        # Stocker l'ID de la candidature sélectionnée dans session_state
        if 'selected_application_id' not in st.session_state:
            st.session_state.selected_application_id = None

        # Utiliser selectbox pour déclencher le choix de la ligne sans recharger
        selected_application_id = st.selectbox("Sélectionnez une candidature pour voir les détails du score", options=applications["ID"])

        # Mettre à jour session_state seulement si un nouvel ID est sélectionné
        if selected_application_id != st.session_state.selected_application_id:
            st.session_state.selected_application_id = selected_application_id

        # Afficher le tableau stylisé
        styled_applications = applications.style.applymap(
            lambda Score: apply_score_color(Score) if isinstance(Score, (int, float)) else "",
            subset=["Score"]
        )
        st.dataframe(styled_applications)

        # Afficher les détails du score sous forme de diagramme radar si une candidature est sélectionnée
        if st.session_state.selected_application_id:
            # Récupérer les scores pour l'application sélectionnée
            score_details = get_application_scores(st.session_state.selected_application_id)
            if score_details:
                # Afficher le popup avec le radar
                with st.expander(f"Score details for application {st.session_state.selected_application_id}"):
                    show_score_radar(score_details)
            else:
                st.write("No score details found for this application.")
    else:
        st.write("No applications found for this Job")

def llm_filter():
  
    st.subheader("Ask Question to your Data")
    # Filtrer et afficher les candidatures    
    user_query = st.text_input("Ask a Question ")
    if st.button("Search"):
       with st.spinner("Processing..."):
           try:
               # Run the query with LangChain agent
               # Instruct agent to return raw tabular data
               #structured_query = f"{user_query}"
               chain=initialize_sql_chain()
               sql_query = chain.invoke({"question":user_query})
               sql_query=sql_query.replace("LIMIT 5","")
               print(sql_query)
               applications = query_applications(sql_query)
               if "RoleID" in applications.columns:
                  applications = applications.drop(columns=["RoleID"])
               if not applications.empty:
                  st.subheader("Answer")
                  st.dataframe(applications)
               else:
                 st.write("No Applications Found")
                     
           except Exception as e:
               st.error(f"Erreur lors de l'exécution de la requête : {e}")
def main():
     st.title("Job Application Interface")
     default_filter()
     llm_filter()


if __name__ == "__main__":
    main()
